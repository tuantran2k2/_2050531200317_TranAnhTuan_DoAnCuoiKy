from sqlalchemy.orm import Session
from models.Jobs import Job
import logging


def get_jobs(db: Session):
    try:
        # Truy vấn lịch sử trò chuyện theo maBST
        jobs = db.query(Job).all()

        # Kiểm tra nếu không có bản ghi nào
        if not jobs:
            return {"message": "không có công việc nào"}

        # Trả về danh sách lịch sử trò chuyện dưới dạng JSON
        return {"status": 200, "data": jobs}

    except Exception as e:
        logging.error(f"Database error occurred: {e}")
        return {"status": 500, "message": f"Lỗi khi truy vấn dữ liệu: {e}"}