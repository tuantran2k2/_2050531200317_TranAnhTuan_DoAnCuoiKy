from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.KhachHang import KhachHang, OTP 
from schemas._users import EmailRequest, OTPVerifyRequest ,UserRegistrationRequest , User
from dependencies.otp_service import generate_otp, send_verification_email
from dependencies.security import get_password_hash , verify_password , create_access_token, create_refresh_token
from database._database_mysql import SessionLocal
from dependencies.dependencies import get_db
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

import _constants
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/user",
    tags=["user"],
)


################################ Đăng ký tài khoản ########################################################


# Bước 1: Nhập email và yêu cầu gửi OTP
@router.post("/request-otp")
def request_otp(request: EmailRequest, db: Session = Depends(get_db)):
    try:
        email = request.email

        # Kiểm tra xem email đã tồn tại hay chưa
        user = db.query(KhachHang).filter(KhachHang.email == email).first()
        if user:
            return { "status" : 400 ,  "messages " : "Email đã được đăng ký" }
        
        otp_entry = db.query(OTP).filter(
            OTP.email == email,
            OTP.is_used == True,
        ).first()
        
        
        if otp_entry:
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
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}

# Bước 2: Xác thực mã OTP
@router.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    try : 
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
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}


@router.post("/register")
def register_user(request: UserRegistrationRequest, db: Session = Depends(get_db)):
    try:
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

        return {"status" : 200 , "message": "Đăng ký thành công"}
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}

####################################################Đăng nhập tài khoản####################################

@router.post("/login")
async def login(user: User, db: Session = Depends(get_db)):
    try :
        # Kiểm tra nếu email tồn tại trong cơ sở dữ liệu
        user_in_db = db.query(KhachHang).filter(
            KhachHang.email == user.email
        ).first()
        
        
        print(user_in_db.matKhau)
        if user_in_db and verify_password(user.password,user_in_db.matKhau):
            access_token_expires = timedelta(minutes=_constants.ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(days=_constants.ACCESS_REFRESH_TOKEN_EXPIRE_DAY)
            # Tạo Access Token và Refresh Token
            
            access_token = create_access_token(
                data={
                    "user_id": user["user_id"],
                    "display_name": user["tenHienThi"],
                    "user_email": user["tenKH"],
                    "email": user["email"],
                },
                expires_delta=access_token_expires
            )

                    # Tạo refresh token
            refresh_token = create_refresh_token(
                data={
                    "user_id": user["user_id"],
                    "display_name": user["tenHienThi"],
                    "user_email": user["tenKH"],
                    "email": user["email"],
                },
                expires_delta=refresh_token_expires
            )
            # Tạo phản hồi JSON với Access Token
            response = JSONResponse({"access_token": access_token})
            
            # Thiết lập Refresh Token trong Cookie HTTP-only
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

            return response
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}