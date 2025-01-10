from fastapi import APIRouter, Depends, HTTPException, status ,Request ,Response
from sqlalchemy.orm import Session
from models.KhachHang import KhachHang 
from models.LichSuGiaoDich import  LichSuGiaoDich
from models.CV import  CV
from dependencies.security import verified_user
from database._database_mysql import SessionLocal
from dependencies.dependencies import get_db
from datetime import datetime, timedelta
from sqlalchemy import func


router = APIRouter(
    prefix="/api/v1/thong-ke",
    tags=["thong-ke"],
)

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=500, detail="Authorization header missing")
    
    # Xác thực người dùng
    payload = verified_user(auth_header)
    if not payload:
        raise HTTPException(status_code=500, detail="Invalid token or unauthorized")
    
    return payload

def authenticate_user(req: Request, user_id: int):
    auth_header = req.headers.get("Authorization")
    payload = verified_user(auth_header)

    # Kiểm tra token có hợp lệ không
    if isinstance(payload, dict) and "status" in payload:
        raise HTTPException(
            status_code=payload.get("status", 400),
            detail={
                "message": payload.get("message", "Invalid token"),
                "status": payload.get("status", 400)
            }
        )


@router.get("/summary")
def get_summary_statistics(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        # Đếm tổng số CV
        total_cvs = db.query(CV).count()

        # Đếm tổng số user
        total_users = db.query(KhachHang).filter(KhachHang.maQuyen == 2).count()

        # Tổng số token
        total_tokens = db.query(func.sum(LichSuGiaoDich.token)).scalar()

        # Tổng số tiền
        total_amount = db.query(func.sum(LichSuGiaoDich.amount)).scalar()

        return {
            "status": 200,
            "data": {
                "total_cvs": total_cvs,
                "total_users": total_users,
                "total_tokens": total_tokens or 0,
                "total_balance": total_amount or 0,
            }
        }
    except Exception as e:
        return {"status": 500, "message": f"Lỗi: {e}"}
    
@router.get("/transaction-statistics/summary")
def get_transaction_statistics_summary(
    timeframe: str, 
    db: Session = Depends(get_db),
):
    """
    API to get summarized transaction statistics (total amount for all users) based on timeframe (daily, weekly, monthly, yearly).
    """
    try:
        # Base query
        query = db.query(
            func.sum(LichSuGiaoDich.amount).label("total_amount")
        )

        # Weekly statistics
        if timeframe == "weekly":
            query = query.add_columns(func.yearweek(LichSuGiaoDich.created_at).label("week"))
            query = query.group_by(func.yearweek(LichSuGiaoDich.created_at))
            query = query.order_by(func.yearweek(LichSuGiaoDich.created_at).asc())

        # Monthly statistics
        elif timeframe == "monthly":
            query = query.add_columns(
                func.year(LichSuGiaoDich.created_at).label("year"),
                func.month(LichSuGiaoDich.created_at).label("month")
            )
            query = query.group_by(
                func.year(LichSuGiaoDich.created_at),
                func.month(LichSuGiaoDich.created_at)
            )
            query = query.order_by(
                func.year(LichSuGiaoDich.created_at).asc(),
                func.month(LichSuGiaoDich.created_at).asc()
            )

        # Yearly statistics
        elif timeframe == "yearly":
            query = query.add_columns(func.year(LichSuGiaoDich.created_at).label("year"))
            query = query.group_by(func.year(LichSuGiaoDich.created_at))
            query = query.order_by(func.year(LichSuGiaoDich.created_at).asc())

        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe parameter")

        # Execute query
        results = query.all()

        # Process results
        statistics = []
        for row in results:
            period = row[1:]  # Time-related information (e.g., week/month/year)

            statistics.append({
                "period": period,
                "total_amount": row.total_amount
            })

        return {
            "timeframe": timeframe,
            "statistics": statistics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "status": 500})


@router.get("/top-users-by-deposit")
def get_top_users_by_deposit(db: Session = Depends(get_db)):
    """
    API to get the top 5 users who have deposited the most money.
    """
    try:
        # Truy vấn để lấy thông tin 5 người nạp tiền nhiều nhất
        top_users = (
            db.query(
                LichSuGiaoDich.maKH.label("user_id"),
                func.sum(LichSuGiaoDich.amount).label("total_deposit"),
                KhachHang.tenHienThi.label("username"),
                KhachHang.email.label("email")
            )
            .join(KhachHang, LichSuGiaoDich.maKH == KhachHang.maKH)
            .group_by(LichSuGiaoDich.maKH, KhachHang.maKH, KhachHang.email)
            .order_by(func.sum(LichSuGiaoDich.amount).desc())
            .limit(5)
            .all()
        )

        # Chuyển đổi kết quả thành danh sách dictionary
        result = [
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "total_deposit": float(user.total_deposit) if user.total_deposit else 0
            }
            for user in top_users
        ]

        return {
            "status": 200,
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "status": 500})
    
    
@router.get("/by-group-cv")
def get_cv_statistics_by_group(db: Session = Depends(get_db)):
    """
    API to get statistics of CVs by group (field specialization).
    """
    try:
        # Query to group CVs by group specialization
        results = (
            db.query(
                CV.Nganh.label("group"),
                func.count(CV.maCV).label("total_cvs")
            )
            .group_by(CV.Nganh)
            .order_by(func.count(CV.maCV).desc())
            .all()
        )

        # Convert results to dictionary format
        data = [
            {
                "group": row.group,
                "total_cvs": row.total_cvs
            }
            for row in results
        ]

        return {
            "status": 200,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "status": 500})

@router.get("/by-timeframe-cv")
def get_cv_statistics_by_timeframe(
    timeframe: str,
    db: Session = Depends(get_db)
):
    """
    API to get statistics of CVs created by timeframe (weekly, monthly, yearly).
    """
    try:
        query = db.query(
            func.count(CV.maCV).label("total_cvs")
        )

        # Weekly statistics
        if timeframe == "weekly":
            query = query.add_columns(func.yearweek(CV.created_at).label("week"))
            query = query.group_by(func.yearweek(CV.created_at))
            query = query.order_by(func.yearweek(CV.created_at).asc())

        # Monthly statistics
        elif timeframe == "monthly":
            query = query.add_columns(
                func.year(CV.created_at).label("year"),
                func.month(CV.created_at).label("month")
            )
            query = query.group_by(
                func.year(CV.created_at),
                func.month(CV.created_at)
            )
            query = query.order_by(
                func.year(CV.created_at).asc(),
                func.month(CV.created_at).asc()
            )

        # Yearly statistics
        elif timeframe == "yearly":
            query = query.add_columns(func.year(CV.created_at).label("year"))
            query = query.group_by(func.year(CV.created_at))
            query = query.order_by(func.year(CV.created_at).asc())

        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe parameter")

        results = query.all()

        # Process results
        statistics = []
        for row in results:
            period = row[1:]  # Time-related information (e.g., week/month/year)

            statistics.append({
                "period": period,
                "total_cvs": row.total_cvs
            })

        return {
            "status": 200,
            "data": statistics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "status": 500})

