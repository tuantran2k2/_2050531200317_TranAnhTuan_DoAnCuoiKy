from fastapi import APIRouter, HTTPException , Depends
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
 # import model LichSuTroChuyen và BoSuTap
from schemas._lichSu import LichSuTroChuyenRespose   # import các schema
from controllers import _lichSu

router = APIRouter(
    prefix="/api/v1/history",
    tags=["history"],
)


@router.post("/get-history")
def get_chat_history(request : LichSuTroChuyenRespose, db: Session = Depends(get_db)):
    try:
        # Truy vấn lịch sử trò chuyện theo maBST
        history_records = _lichSu.get_history(request.maBST,db)

        if not history_records:
            raise HTTPException(status_code=404, detail="Lịch sử trò chuyện không tìm thấy")

        # Trả về danh sách các bản ghi dưới dạng JSON
        return history_records

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
