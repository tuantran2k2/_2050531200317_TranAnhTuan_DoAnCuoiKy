from payos import PayOS, PaymentData
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.LichSuGiaoDich import LichSuGiaoDich
from models.KhachHang import KhachHang
from dotenv import load_dotenv
import os

load_dotenv()

# Khởi tạo đối tượng PayOS
payOS = PayOS(
    client_id=os.getenv("client_id"),
    api_key=os.getenv("api_key"),
    checksum_key=os.getenv("checksum_key")
)

# Hàm tạo liên kết thanh toán
async def create_payment_link(maKH ,amount, cancelUrl, returnUrl):
    try:
        # Chuyển amount sang int
        amount = int(amount)
        
        # Tạo mã đơn hàng dưới dạng số nguyên từ timestamp
        order_code = int(datetime.utcnow().timestamp() * 1000)  # Đảm bảo order_code là int

        payment_data = PaymentData(
            orderCode=order_code,
            amount=amount,
            description="Buddy AI payment",
            cancelUrl=cancelUrl,
            returnUrl=returnUrl,
             maKH=maKH,
        )
        payment_link_data = payOS.createPaymentLink(paymentData=payment_data)

        if not payment_link_data:
            print("createPaymentLink did not return valid data")
            return None 
        return payment_link_data 
    except Exception as e:
        print(f'Error in create_payment_link: {e}')
        return None 

# Trong hàm kiểm tra trạng thái thanh toán
def process_payment_status(order_id, maKH ,db: Session):
    try:
        existing_transaction = db.query(LichSuGiaoDich).filter_by(order_id=order_id).first()
        if existing_transaction:
            return {"status": existing_transaction.status}

        payment_info = payOS.getPaymentLinkInformation(orderId=order_id)
        
        if not payment_info:
            return {"error": "Payment information not found"}

        if payment_info.status == "PENDING":
            return {"status": "PENDING"}
        else:
            result = save_transaction(
                maKH=maKH,
                order_id=order_id,
                amount=int(payment_info.amount),  # Chuyển amount sang int
                transaction_type="credit",
                payment_method="PayOS",
                created_at=payment_info.createdAt,
                status="PAID",
                db=db
            )
            if result is None:
                return {"error": "Failed to save transaction"}
            if result == 404:
                return {"message": "User ID not found", "status": 404}
            return {"status": "PAID"}
    except Exception as e:
        print(f'Error processing payment: {e}')
        return {"error": f"Internal server error: {str(e)}"}

## hàm lưu vào database
def save_transaction(maKH, order_id, amount, transaction_type, payment_method, created_at, status , db: Session):
    try:
        # Chuyển amount sang int trước khi lưu
        amount = int(amount)

        user = db.query(KhachHang).filter(KhachHang.maKH==maKH).first()
        if not user:
            print("User ID không tồn tại.")
            return 404

        new_transaction = LichSuGiaoDich(
            maKH=maKH,
            order_id=order_id,
            amount=amount,
            currency='VND',
            transaction_type=transaction_type,
            payment_method=payment_method,
            created_at=created_at,
            status=status
        )
        db.add(new_transaction)
        db.commit()
        print("Giao dịch đã được lưu vào cơ sở dữ liệu.")
        return new_transaction
    except Exception as e:
        print(f"Lỗi khi lưu giao dịch: {e}")
        return None

# hàm tính tổng balance của từng user
def calculate_total_balance(user_id: int , db: Session):
    try:
        total_amount = db.query(func.sum(LichSuGiaoDich.amount)).filter(
            LichSuGiaoDich.maKH == user_id,
            LichSuGiaoDich.status == "PAID"
        ).scalar()  # `scalar()` để lấy giá trị duy nhất từ truy vấn

        if total_amount is None:
            return {"message": "No transactions found for this user", "total_balance": 0.0}

        # Chuyển total_amount sang int nếu cần
        return {"message": "Total balance calculated successfully", "total_balance": int(total_amount)}
    except Exception as e:
        print(f"Lỗi khi tính tổng tiền: {e}")
        return {"message": f"Error calculating total balance: {str(e)}", "total_balance": None}

# Hàm lấy danh sách giao dịch
def fetch_deposit_history(user_id: int , db: Session):
    try:
        # Truy vấn để lấy lịch sử nạp tiền theo `user_id`, sắp xếp từ mới nhất đến cũ nhất
        transactions = db.query(LichSuGiaoDich).filter(
            LichSuGiaoDich.maKH == user_id
        ).order_by(LichSuGiaoDich.created_at.desc()).all()

        # Nếu không có giao dịch, trả về thông báo
        if not transactions:
            return {"message": "No transactions found for this user", "transactions": []}

        # Chuyển đổi kết quả truy vấn thành danh sách các dict để trả về JSON
        transaction_history = [
            {
                "transaction_id": txn.id,
                "amount": int(txn.amount),  # Chuyển amount sang int
                "currency": txn.currency,
                "transaction_type": txn.transaction_type,
                "payment_method": txn.payment_method,
                "status": txn.status,
                "created_at": txn.created_at,
                "updated_at": txn.updated_at,
            }
            for txn in transactions
        ]

        return {"message": "Transaction history fetched successfully", "transactions": transaction_history}
    except Exception as e:
        print(f"Lỗi khi lấy lịch sử nạp tiền: {e}")
        return {"message": f"Error fetching transaction history: {str(e)}", "transactions": None}
