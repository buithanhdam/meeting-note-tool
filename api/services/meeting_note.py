# Các hàm background
from src.flow.export_meeting_minutes import export_to_word, export_meeting_minutes
from src.flow.export_transcript import process_audio_video
def process_text_job(file_path, job_id):
    """Xử lý file văn bản trong background"""
    try:
        # Xử lý transcript
        meeting_minutes = export_meeting_minutes(file_path)
        
        # Xuất ra Word
        output_path = f"results/{job_id}.docx"
        export_to_word(meeting_minutes, output_path)
        
        # Cập nhật trạng thái trong database
        # ...
    except Exception as e:
        # Xử lý lỗi
        # ...
        raise e

def process_media_job(file_path, job_id):
    """Xử lý file âm thanh/video trong background"""
    try:
        # Chuyển đổi media thành transcript
        transcript_path = process_audio_video(file_path)
        
        # Xử lý transcript
        meeting_minutes = export_meeting_minutes(transcript_path)
        
        # Xuất ra Word
        export_to_word(meeting_minutes)
        
        # Cập nhật trạng thái trong database
        # ...
    except Exception as e:
        # Xử lý lỗi
        # ...
        raise e