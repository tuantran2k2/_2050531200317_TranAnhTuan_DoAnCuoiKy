from sqlalchemy.orm import Session
from models.KhachHang import KhachHang
import logging

    
def update_amount(maKH: int, new_money :int , db: Session):
    try:
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == maKH,).first()

        if user_in_db is None:
            return {"success": False, "message": "User not found."}

        # Cập nhật tên bộ sưu tập
        user_in_db.soLuongToken = new_money
        db.commit()
        return {"success": True, "message": f"Collection renamed to '{new_money}' successfully."}

    except Exception as e:
        db.rollback()  # Rollback nếu có lỗi xảy ra
        logging.error(f"Database error occurred: {e}")
        return {"success": False, "message": "Database error."}
