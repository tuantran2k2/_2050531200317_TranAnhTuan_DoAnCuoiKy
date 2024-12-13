from sqlalchemy.orm import Session
from models.LichSuTroChuyen import LichSuTroChuyen
from fastapi.responses import JSONResponse
import logging


def get_history(maBST: int, db: Session):
    try:
        # Truy vấn lịch sử trò chuyện theo maBST
        history_records = db.query(LichSuTroChuyen).filter(LichSuTroChuyen.maBST == maBST).all()

        # Kiểm tra nếu không có bản ghi nào
        if not history_records:
            logging.warning(f"Không có lịch sử trò chuyện cho maBST {maBST}")
            return {"message": "Không có lịch sử trò chuyện"}

        # Tạo danh sách chứa lịch sử trò chuyện
        history_list = []
        for record in history_records:
            history_item = {
                "cauHoi": record.cauHoi,
                "phanHoi": record.phanHoi,
                "tongSoToken": record.tongSoToken,
                "timestamp": record.timestamp.isoformat()  # Chuyển đổi thời gian sang định dạng ISO
            }
            history_list.append(history_item)

        # Trả về danh sách lịch sử trò chuyện dưới dạng JSON
        return {"maBST": maBST, "lichSuTroChuyen": history_list}

    except Exception as e:
        logging.error(f"Database error occurred: {e}")
        return {"error": "Đã xảy ra lỗi khi truy vấn dữ liệu"}