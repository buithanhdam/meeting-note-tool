from fastapi import APIRouter, HTTPException, Request
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
import os
import uuid
from src.config import GlobalConfig
from api.services.meeting_note import process_text_job, process_media_job
from src.db import DatabaseManager
from src.logger import get_formatted_logger
logger = get_formatted_logger(__name__)

global_config = GlobalConfig()
meeting_router = APIRouter(prefix="/meeting", tags=["meeting"])
db_manager = DatabaseManager()

def ensure_folder_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
ensure_folder_exists(global_config.PathConfig.input_path)
ensure_folder_exists(global_config.PathConfig.output_path)
ensure_folder_exists(global_config.PathConfig.tempt_path)

@meeting_router.post("/upload/text")
async def upload_text(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """API to process text files"""
    try:
        logger.info(f"Received text upload request: {file.filename}")
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Save temp file
        file_path = os.path.join(global_config.PathConfig.tempt_path, f"{job_id}{os.path.splitext(file.filename)[1]}")
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        logger.info(f"Created job {job_id} for file {file.filename}, saved to {file_path}")
        
        # Process file in background
        background_tasks.add_task(process_text_job, file_path, job_id)
        
        return {"job_id": job_id, "status": "PENDING"}
    except Exception as e:
        logger.error(f"Error processing text upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@meeting_router.post("/upload/media")
async def upload_media(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """API to process audio/video files"""
    try:
        logger.info(f"Received media upload request: {file.filename}")
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Save temp file
        file_path = os.path.join(global_config.PathConfig.tempt_path, f"{job_id}{os.path.splitext(file.filename)[1]}")
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        logger.info(f"Created job {job_id} for file {file.filename}, saved to {file_path}")
        
        # Process file in background
        background_tasks.add_task(process_media_job, file_path, job_id)
        
        return {"job_id": job_id, "status": "PENDING"}
    except Exception as e:
        logger.error(f"Error processing media upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@meeting_router.get("/status/{job_id}")
async def get_status(job_id: str):
    """API to check processing status using database"""
    try:
        logger.info(f"Status check for job: {job_id}")
        
        # Get process from database
        process = await db_manager.get_process(job_id)
        
        if not process:
            logger.warning(f"Job ID not found: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Return process information
        return {
            "job_id": job_id, 
            "status": process["status"],
            "created_at": process["created_at"],
            "updated_at": process["updated_at"],
            "processing_time": process.get("processing_time"),
            "error": process.get("error")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@meeting_router.get("/details/{job_id}")
async def get_job_details(job_id: str):
    """API to get comprehensive job details"""
    try:
        logger.info(f"Details request for job: {job_id}")
        
        # Get process from database
        process = await db_manager.get_process(job_id)
        
        if not process:
            logger.warning(f"Job ID not found: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get transcript data if available
        transcript_data = await db_manager.get_transcript_data(job_id)
        
        # Combine data
        result = {
            "job_id": job_id,
            "status": process["status"],
            "created_at": process["created_at"],
            "updated_at": process["updated_at"],
            "start_time": process.get("start_time"),
            "end_time": process.get("end_time"),
            "processing_time": process.get("processing_time"),
            "chunk_count": process.get("chunk_count"),
            "error": process.get("error"),
            "result": process.get("result"),
            "metadata": process.get("metadata"),
        }
        
        if transcript_data:
            result["transcript"] = {
                "meeting_name": transcript_data.get("meeting_name"),
                "model": transcript_data.get("model"),
                "model_name": transcript_data.get("model_name"),
                "chunk_size": transcript_data.get("chunk_size"),
                "overlap": transcript_data.get("overlap"),
                "created_at": transcript_data.get("created_at"),
                # Don't include full transcript text as it could be large
                "transcript_length": len(transcript_data.get("transcript_text", "")) if transcript_data.get("transcript_text") else 0
            }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@meeting_router.get("/download/{job_id}")
async def download_result(job_id: str):
    """API to download results"""
    try:
        logger.info(f"Download request for job: {job_id}")
        
        # Check if job exists and is completed
        process = await db_manager.get_process(job_id)
        
        if not process:
            logger.warning(f"Job ID not found for download: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        
        if process["status"] != "COMPLETED":
            logger.warning(f"Job {job_id} not completed yet. Current status: {process['status']}")
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        # Get file path
        file_path = os.path.join(global_config.PathConfig.output_path, f"{job_id}.docx")
        
        if not os.path.exists(file_path):
            logger.error(f"Output file not found: {file_path}")
            raise HTTPException(status_code=404, detail="Output file not found")
        
        # Get meeting name for filename if available
        transcript_data = await db_manager.get_transcript_data(job_id)
        filename = "meeting_minutes.docx"
        if transcript_data and transcript_data.get("meeting_name"):
            filename = f"{transcript_data['meeting_name'].replace(' ', '_')}_minutes.docx"
        
        logger.info(f"Sending file: {file_path} as {filename}")
        return FileResponse(file_path, filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@meeting_router.get("/download/{job_id}/transcript")
async def download_transcript(job_id: str):
    """API to download transcript for media files"""
    try:
        logger.info(f"Transcript download request for job: {job_id}")
        
        # Check if job exists
        process = await db_manager.get_process(job_id)
        
        if not process:
            logger.warning(f"Job ID not found for transcript download: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
            
        # Get transcript data
        transcript_data = await db_manager.get_transcript_data(job_id)
        
        if not transcript_data:
            logger.error(f"Transcript data not found for job: {job_id}")
            raise HTTPException(status_code=404, detail="Transcript data not found")
        
        # Create a temporary file with the transcript text
        transcript_path = os.path.join(global_config.PathConfig.output_path, f"{job_id}_transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_data.get("transcript_text", ""))
        
        # Get meeting name for filename if available
        filename = "transcript.txt"
        if transcript_data.get("meeting_name"):
            filename = f"{transcript_data['meeting_name'].replace(' ', '_')}_transcript.txt"
        
        logger.info(f"Sending transcript file for {job_id}")
        return FileResponse(transcript_path, filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@meeting_router.delete("/cleanup")
async def cleanup_old_jobs(hours: int = 24):
    """API to clean up old jobs from the database"""
    try:
        logger.info(f"Cleaning up jobs older than {hours} hours")
        await db_manager.cleanup_old_processes(hours)
        return {"status": "success", "message": f"Cleaned up jobs older than {hours} hours"}
    except Exception as e:
        logger.error(f"Error cleaning up old jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))