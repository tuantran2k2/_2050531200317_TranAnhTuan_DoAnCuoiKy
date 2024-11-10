from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.KhachHang import KhachHang, OTP 
from schemas._users import EmailRequest, OTPVerifyRequest ,UserRegistrationRequest
from dependencies.otp_service import generate_otp, send_verification_email
from dependencies.security import get_password_hash
from database._database_mysql import SessionLocal
from dependencies.dependencies import get_db

import datetime
import uuid

router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
)

# Bước 1: Nhập email và yêu cầu gửi OTP
@router.post("/request-otp")
def request_otp(request: EmailRequest, db: Session = Depends(get_db)):
    email = request.email

    # Kiểm tra xem email đã tồn tại hay chưa
    user = db.query(KhachHang).filter(KhachHang.email == email).first()
    if user:
        return { "status" : 400 ,  "messages " : "Email đã được đăng ký" }
    
    otp_entry = db.query(OTP).filter(
        OTP.email == email,
        OTP.is_used == True,
    ).first()
    
    
    if otp_entry :
        return { 
                "status" : 207 , 
                "messages": 
                    {
                        "email": otp_entry.email,
                        "otp_code": otp_entry.otp_code
                    } 
        }
    # Tạo mã OTP và gửi đến ema
    otp_code = generate_otp(email)
    send_verification_email(email,otp_code)

    _otp_code = OTP(
        email=email,
        otp_code=otp_code,
        is_used=False,
        created_at=datetime.datetime.utcnow() 
    )
    db.add(_otp_code)
    db.commit()
    db.refresh(_otp_code)

    return { "status" : 200 , "message": "OTP đã được gửi đến email của bạn"}

# Bước 2: Xác thực mã OTP
@router.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    email = request.email
    otp_code = request.otp_code

    # Tìm người dùng có email và mã OTP phù hợp
    otp_entry = db.query(OTP).filter(
        OTP.email == email,
        OTP.otp_code == otp_code,
        OTP.is_used == False,
    ).first()

    if not otp_entry:
        return  { "status" : 400 ,  "messages " : "OTP không hợp lệ" }
    
    email_sent  = send_verification_email(email,otp_code)
    print(email_sent)
    if email_sent == False:
        return  { "status" : 405 ,  "messages " : "OTP hết hạn " }
    
    otp_entry.is_used = True
    db.commit()
    

    return { 
            "status" : 200 , 
            "messages": 
            {
                    "email": otp_entry.email,
                    "otp_code": otp_entry.otp_code
            } 
    }



@router.post("/register")
def register_user(request: UserRegistrationRequest, db: Session = Depends(get_db)):
    # Kiểm tra token tạm thời hợp lệ
    otp_entry = db.query(OTP).filter(
        OTP.email == request.email,
        OTP.otp_code == request.otp_code,
        OTP.is_used == True
    ).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Phiên đăng ký không hợp lệ")

    # Tạo người dùng mới
    new_user = KhachHang(
        email=otp_entry.email,
        tenHienThi=request.tenHienThi,
        tenKH=request.tenKH,
        matKhau=get_password_hash(request.password),
        ngayDangKy=datetime.utcnow()
    )
    db.add(new_user)


    db.commit()
    db.refresh(new_user)

    return {"message": "Đăng ký thành công", "user_id": new_user.maKH}