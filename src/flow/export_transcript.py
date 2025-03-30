import pydub
from pydub import AudioSegment
import openai
import os
from src.config import GLOBAL_CONFIG

openai.api_key = GLOBAL_CONFIG.OPENAI_API_KEY

def extract_audio_from_video(video_path):
    audio = AudioSegment.from_file(video_path, format="mp4")
    audio_path = video_path.replace('.mp4', '.mp3')
    audio.export(audio_path, format="mp3")
    return audio_path

def split_audio(audio_path, chunk_duration=60000):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    
    for i in range(0, len(audio), chunk_duration):
        chunk = audio[i:i+chunk_duration]
        chunk_path = os.path.join( GLOBAL_CONFIG.tempt_path,f"chunk_{i//chunk_duration}.mp3")
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    
    return chunks

def speech_to_text(audio_chunks):
    transcript = ""
    
    for chunk_path in audio_chunks:
        with open(chunk_path, "rb") as audio_file:
            # Sử dụng OpenAI Whisper API
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            chunk_transcript = response.text
            transcript += chunk_transcript + " "
    
    return transcript

def process_audio_video(file_path):
    if file_path.endswith('.mp4'):
        audio_path = extract_audio_from_video(file_path)
    else:
        audio_path = file_path
    
    audio_chunks = split_audio(audio_path)
    
    transcript = speech_to_text(audio_chunks)
    
    transcript_path = os.path.join(GLOBAL_CONFIG.output_path, os.path.splitext(file_path)[0] + "_transcript.txt")
    with open(transcript_path, "w") as f:
        f.write(transcript)
    
    return transcript_path