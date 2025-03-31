from pydub import AudioSegment
import whisper
import os
from src.config import GlobalConfig
from src.logger import get_formatted_logger

logger = get_formatted_logger(__name__)

global_config = GlobalConfig()

def extract_audio_from_video(video_path):
    try:
        logger.info(f"Extracting audio from video: {video_path}")
        audio = AudioSegment.from_file(video_path, format="mp4")
        audio_path = video_path.replace('.mp4', '.mp3')
        audio.export(audio_path, format="mp3")
        logger.info(f"Audio extracted successfully to: {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"Error extracting audio from video: {str(e)}")
        raise

def split_audio(audio_path, chunk_duration=30000):
    try:
        logger.info(f"Splitting audio file: {audio_path} into {chunk_duration}ms chunks")
        audio = AudioSegment.from_file(audio_path)
        chunks = []
        
        for i in range(0, len(audio), chunk_duration):
            chunk = audio[i:i+chunk_duration]
            chunk_path = os.path.join(global_config.PathConfig.tempt_path, f"chunk_{i//chunk_duration}.mp3")
            chunk.export(chunk_path, format="mp3")
            chunks.append(chunk_path)
            logger.debug(f"Created chunk {i//chunk_duration} at {chunk_path}")
        
        logger.info(f"Audio split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Error splitting audio: {str(e)}")
        raise

def speech_to_text(audio_chunks):
    try:
        logger.info("Starting speech-to-text conversion")
        transcript = ""
        stt_model = whisper.load_model("tiny")
        logger.info("Whisper model loaded")
        
        for i, chunk_path in enumerate(audio_chunks):
            logger.debug(f"Processing chunk {i+1}/{len(audio_chunks)}: {chunk_path}")
            # load audio and pad/trim it to fit 30 seconds
            audio = whisper.load_audio(chunk_path)
            audio = whisper.pad_or_trim(audio)
            
            # make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio, n_mels=stt_model.dims.n_mels).to(stt_model.device)
            
            # detect the spoken language
            _, probs = stt_model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            logger.debug(f"Detected language for chunk {i+1}: {detected_language}")
            
            # decode the audio
            options = whisper.DecodingOptions()
            result = whisper.decode(stt_model, mel, options)
            
            chunk_transcript = result.text
            transcript += chunk_transcript + " "
            logger.debug(f"Transcribed chunk {i+1}, added {len(chunk_transcript)} characters")
        
        logger.info(f"Speech-to-text conversion completed. Total transcript length: {len(transcript)} characters")
        return transcript
    except Exception as e:
        logger.error(f"Error in speech-to-text conversion: {str(e)}")
        raise

def process_audio_video(file_path):
    try:
        logger.info(f"Starting audio/video processing for: {file_path}")
        if file_path.endswith('.mp4'):
            logger.info("Detected video file, extracting audio")
            audio_path = extract_audio_from_video(file_path)
        else:
            logger.info("Using audio file directly")
            audio_path = file_path
        
        logger.info("Splitting audio into chunks")
        audio_chunks = split_audio(audio_path)
        
        logger.info("Converting speech to text")
        transcript = speech_to_text(audio_chunks)
        
        transcript_path = os.path.join(
            global_config.PathConfig.output_path,
            os.path.splitext(os.path.basename(file_path))[0] + "_transcript.txt"
        )

        # Ensure the parent directory exists, NOT the file itself
        output_dir = os.path.dirname(transcript_path)
        os.makedirs(output_dir, exist_ok=True)

        # Now write to the file
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        logger.info(f"Transcript saved to: {transcript_path}")
        return transcript_path
    except Exception as e:
        logger.error(f"Error in audio/video processing: {str(e)}")
        raise