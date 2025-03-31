from src.flow.export_meeting_minutes import export_to_word, export_meeting_minutes
from src.flow.export_transcript import process_audio_video
from src.db import DatabaseManager
import os
import time
from src.config import GlobalConfig
from src.logger import get_formatted_logger

logger = get_formatted_logger(__name__)
db_manager = DatabaseManager()
global_config = GlobalConfig()

async def process_text_job(file_path, job_id):
    """Process text files in background with database tracking"""
    try:
        # Create process in database
        await db_manager.create_process(job_id)
        start_time = time.time()
        
        logger.info(f"Processing text job {job_id} from {file_path}")
        
        # Process transcript
        meeting_minutes = export_meeting_minutes(file_path)
        
        # Export to Word
        output_path = os.path.join(global_config.PathConfig.output_path, f"{job_id}.docx")
        export_to_word(meeting_minutes, output_path)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save transcript data
        await db_manager.save_transcript(
            process_id=job_id,
            transcript_text=open(file_path, 'r').read(),
            model=global_config.GEMINI_CONFIG.model_id,
            model_name=global_config.GEMINI_CONFIG.model_name,
            chunk_size=0,  # Not applicable for text
            overlap=0      # Not applicable for text
        )
        
        # Extract meeting name from minutes (assuming it's in the first line or header)
        meeting_name = meeting_minutes.split('\n')[0].replace('#', '').strip()
        await db_manager.update_meeting_name(job_id, meeting_name)
        
        # Update process status to completed
        await db_manager.update_process(
            process_id=job_id, 
            status="COMPLETED",
            result={"output_path": output_path},
            chunk_count=1,
            processing_time=processing_time,
            metadata={"file_type": "text", "original_filename": os.path.basename(file_path)}
        )
        
        logger.info(f"Text job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing text job {job_id}: {str(e)}")
        # Update process status to failed
        await db_manager.update_process(
            process_id=job_id,
            status="FAILED",
            error=str(e)
        )
        raise e

async def process_media_job(file_path, job_id):
    """Process audio/video files in background with database tracking"""
    try:
        # Create process in database
        await db_manager.create_process(job_id)
        start_time = time.time()
        
        logger.info(f"Processing media job {job_id} from {file_path}")
        
        # Convert media to transcript
        await db_manager.update_process(job_id, "TRANSCRIBING")
        transcript_path = process_audio_video(file_path)
        
        # Read transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        # Save transcript data
        file_type = "audio" if file_path.endswith(('.mp3', '.wav')) else "video"
        await db_manager.save_transcript(
            process_id=job_id,
            transcript_text=transcript_text,
            model="whisper-tiny",  # Based on your transcription code
            model_name="whisper-tiny",
            chunk_size=30000,  # 30s chunks from your code
            overlap=0
        )
        
        # Process transcript
        await db_manager.update_process(job_id, "SUMMARIZING")
        meeting_minutes = export_meeting_minutes(transcript_path)
        
        # Extract meeting name from minutes (assuming it's in the first line or header)
        meeting_name = meeting_minutes.split('\n')[0].replace('#', '').strip()
        await db_manager.update_meeting_name(job_id, meeting_name)
        
        # Export to Word
        output_path = os.path.join(global_config.PathConfig.output_path, f"{job_id}.docx")
        export_to_word(meeting_minutes, output_path)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update process status to completed
        await db_manager.update_process(
            process_id=job_id, 
            status="COMPLETED",
            result={
                "output_path": output_path,
                "transcript_path": transcript_path
            },
            chunk_count=os.path.getsize(file_path) // 30000 + 1,  # Approximate chunk count
            processing_time=processing_time,
            metadata={
                "file_type": file_type,
                "original_filename": os.path.basename(file_path),
                "audio_length_seconds": os.path.getsize(file_path) // 48000  # Rough estimate
            }
        )
        
        logger.info(f"Media job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing media job {job_id}: {str(e)}")
        # Update process status to failed
        await db_manager.update_process(
            process_id=job_id,
            status="FAILED",
            error=str(e)
        )
        raise e