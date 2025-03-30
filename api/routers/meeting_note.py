from fastapi import APIRouter, HTTPException, Request
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
import os
import uuid
from src.config import GLOBAL_CONFIG
from api.services.meeting_note import process_text_job, process_media_job
meeting_router = APIRouter(prefix="/meeting", tags=["meeting"])

def ensure_folder_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
ensure_folder_exists(GLOBAL_CONFIG.input_path)
ensure_folder_exists(GLOBAL_CONFIG.output_path)
ensure_folder_exists(GLOBAL_CONFIG.tempt_path)

@meeting_router.post("/upload/text")
async def upload_text(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """API để xử lý file văn bản"""
    # Tạo ID cho job
    job_id = str(uuid.uuid4())
    
    # Lưu file tạm
    file_path = os.path.join(GLOBAL_CONFIG.tempt_path, f"temp_{job_id}{os.path.splitext(file.filename)[1]}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Xử lý file trong background
    background_tasks.add_task(process_text_job, file_path, job_id)
    
    return {"job_id": job_id, "status": "processing"}

@meeting_router.post("/upload/media")
async def upload_media(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """API để xử lý file âm thanh/video"""
    # Tạo ID cho job
    job_id = str(uuid.uuid4())
    
    # Lưu file tạm
    file_path = os.path.join(GLOBAL_CONFIG.tempt_path, f"temp_{job_id}{os.path.splitext(file.filename)[1]}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Xử lý file trong background
    background_tasks.add_task(process_media_job, file_path, job_id)
    
    return {"job_id": job_id, "status": "processing"}

@meeting_router.get("/status/{job_id}")
async def get_status(job_id: str):
    """API để kiểm tra trạng thái xử lý"""
    # Kiểm tra trạng thái từ database
    # ...
    
    return {"job_id": job_id, "status": "completed"}

@meeting_router.get("/download/{job_id}")
async def download_result(job_id: str):
    """API để tải xuống kết quả"""
    # Lấy đường dẫn file từ database
    # ...
    
    file_path = f"data//{job_id}.docx"
    
    return FileResponse(file_path, filename="meeting_minutes.docx")
