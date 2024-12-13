from controllers._lichSuGiaoDich import create_payment_link, process_payment_status, calculate_total_balance,  fetch_deposit_history
from dependencies.security import  verified_user
from fastapi import APIRouter, Depends ,HTTPException ,Request
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from shutil import copyfileobj
from schemas._lichSuGiaoDich import DepositRequest
from controllers import _lichSuGiaoDich

router = APIRouter(
    prefix="/api/v1",
    tags=["lsgd"],
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

    # So khớp user_id từ payload
    if payload.get("user_id") != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "User ID does not match",
                "status": 403
            }
        )

    return payload


# ==========================================  PAYMENT ===============================================
@router.post("/deposit")
async def deposit(request: DepositRequest, req: Request ,  current_user: dict = Depends(get_current_user)):
    user_id = request.maKH
    amount = int(request.amount)
    authenticate_user(req, user_id)

    try:
        # Tạo liên kết thanh toán
        payment_link = await create_payment_link(user_id,amount, "http://192.168.1.3:8081/payment-fail/",
                                                 "http://192.168.1.3:8081/payment-success/")
        if not payment_link:
            raise HTTPException(status_code=500, detail="Failed to create payment link")
        print(payment_link)
        return {"payment_link": payment_link.checkoutUrl, "order_id": payment_link.orderCode,"maKH": user_id, }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/payment-status/{order_id}")
def get_payment_status(order_id: str, user_id: int, req: Request,db: Session = Depends(get_db)):
    try:
        status = process_payment_status(order_id, user_id,db)
        # Kiểm tra nếu có Error từ controlle
        if "error" in status:
            if status["error"] == "Payment information not found":
                raise HTTPException(status_code=404, detail=status["error"])
            elif status["error"] == "Failed to save transaction":
                raise HTTPException(status_code=500, detail=status["error"])
            else:
                raise HTTPException(status_code=500, detail=status["error"])

        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "status": 500})


# api get total balance
@router.get("/api/v1/total-balance/{user_id}")
def get_total_balance(user_id: int, req: Request, current_user: dict = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        authenticate_user(req, user_id)
        result = calculate_total_balance(user_id,db)
        if result["total_balance"] is None:
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "status": 500})


# api get list transactions
@router.get("/api/v1/deposit-history/{user_id}")
def get_deposit_history(user_id: int, req: Request, current_user: dict = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        authenticate_user(req, user_id)
        result = fetch_deposit_history(user_id,db)
        if result["transactions"] is None:
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "status": 500})

