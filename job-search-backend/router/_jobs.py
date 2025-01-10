from fastapi import APIRouter, HTTPException , Depends
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from controllers import _jobs
from database import _qdrant
import logging
from dotenv import load_dotenv
import os
from scrapers.crawl_linkedln import crawl_linkedin_jobs
from pydantic import BaseModel


load_dotenv()
# Lấy các biến môi trường từ file .env
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


router = APIRouter(
    prefix="/api/v1/jobs"
)


class CrawlJobsRequest(BaseModel):
    time_range: str

@router.post("/get-jobs")
@router.post("/get-jobs/")
def get_chat_history(db: Session = Depends(get_db)):
    try:
        # Truy vấn lịch sử trò chuyện theo maBST
        jobs = _jobs.get_jobs(db)

        if not jobs:
            raise HTTPException(status_code=404, detail="Không có công việc nào")

        # Trả về danh sách các bản ghi dưới dạng JSON
        return jobs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
    
    
@router.post("/crawl-jobs")
@router.post("/crawl-jobs/")
def crawl_jobs(request: CrawlJobsRequest, db: Session = Depends(get_db)):
    time_range = request.time_range
    try:
        crawl_linkedin_jobs(time_range=time_range, db=db)
        return {"status": 200, "message": "Crawl dữ liệu thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi crawl dữ liệu: {e}")

@router.get("/refresh-qdrant")
@router.get("/refresh-qdrant/")
def refresh_qdrant():
    try:
        logging.info("Đang kiểm tra và xóa các điểm quá 7 ngày trong Qdrant...")
        _qdrant.delete_old_points(COLLECTION_NAME)
        return {"status": 200, "message": "Làm mới Qdrant thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi làm mới Qdrant: {e}")
