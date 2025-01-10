from fastapi import APIRouter, Depends, HTTPException, status ,Request ,Response , File, UploadFile , Form
from sqlalchemy.orm import Session
from models.KhachHang import KhachHang, OTP 
from schemas._users import EmailRequest, OTPVerifyRequest ,UserRegistrationRequest , User , UpdateUser ,UpdateStatus , UpdateUserInfoRequest
from dependencies.otp_service import generate_otp, send_verification_email , send_verification_email_from_admin , send_pdf_email
from dependencies.security import get_password_hash , verify_password , create_access_token , verified_user
from database._database_mysql import SessionLocal
from dependencies.dependencies import get_db
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

import _constants
from datetime import datetime
import jwt
import os
import shutil

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
        # Tạo mã OTP và gửi đến email
        otp_code = generate_otp(email)
        send_verification_email(email,otp_code)

        _otp_code = OTP(
            email=email,
            otp_code=otp_code,
            is_used=False,
            created_at=datetime.utcnow()
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
            OTP.is_used == True
        ).first()

        if not otp_entry:
            raise HTTPException(status_code=400, detail="Phiên đăng ký không hợp lệ")

        # Kiểm tra định dạng ngày sinh
        try:
            ngay_sinh_parsed = datetime.strptime(request.ngaySinh, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Ngày sinh không hợp lệ. Định dạng phải là YYYY-MM-DD")

        # Tạo người dùng mới
        new_user = KhachHang(
            email=otp_entry.email,
            tenHienThi=request.tenHienThi,
            tenKH=request.tenKH,
            diaChi=request.diaChi,
            ngaySinh=ngay_sinh_parsed,
            matKhau=get_password_hash(request.password),
            ngayDangKy=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"status": 200, "message": "Đăng ký thành công"}
    except Exception as e:
        return {"status": 500, "message": f"Lỗi {e}"}

####################################################Đăng nhập tài khoản####################################
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=500, detail="Authorization header missing")
    
    # Xác thực người dùng
    payload = verified_user(auth_header)
    if not payload:
        raise HTTPException(status_code=500, detail="Invalid token or unauthorized")
    
    return payload

@router.post("/login")
async def login(user: User, db: Session = Depends(get_db)):
    try :
        # Kiểm tra nếu email tồn tại trong cơ sở dữ liệu
        user_in_db = db.query(KhachHang).filter(
            KhachHang.email == user.email
        ).first()
        
        if (user_in_db.trangThai == 0):
            return {"status" : 500 , "messages" :"Tài khoản của bạn chưa được duyệt"}
        if (user_in_db.trangThai == 2):
            return {"status" : 500 , "messages" :"Tài khoản của bạn đã bị khóa"}
        
        print(user_in_db.matKhau)
        if user_in_db and verify_password(user.password,user_in_db.matKhau):
            access_token_expires = timedelta(minutes=_constants.ACCESS_TOKEN_EXPIRE_MINUTES)
            # Tạo Access Token
            ngay_sinh_str = user_in_db.ngaySinh.isoformat() if user_in_db.ngaySinh else None
            access_token = create_access_token(
                data={
                    "user_id": user_in_db.maKH,
                    "display_name": user_in_db.tenKH,
                    "user_name": user_in_db.tenHienThi,
                    "email": user_in_db.email,
                    "diaChi" : user_in_db.diaChi,
                    "ngaySinh" : ngay_sinh_str,
                    "role" : user_in_db.maQuyen,
                    "trangThai" : user_in_db.trangThai,
                    "SoDu" : user_in_db.soLuongToken
                },
                expires_delta=access_token_expires
            )
            response = JSONResponse({"access_token": access_token})
            return response
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}


@router.post("/logout")
async def logout(response: Response, current_user: dict = Depends(get_current_user)):
    try:
        # Xóa cookie "refresh_token"
        # response.delete_cookie(key="refresh_token")
        return JSONResponse({"message": "Logged out successfully"}, status_code=200)
    except Exception as e:
        print(f"Error during logout: {e}")
        raise HTTPException(
            status_code=500,
            detail="Logout failed. Please try again."
        )
        
####################################################lấy thông  tin tất cả user ####################################

@router.get("/admin/all-users")
def get_all_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        if current_user['role'] != 1:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")

        # Query tất cả người dùng có mã quyền là 2
        users = db.query(KhachHang).filter(KhachHang.maQuyen == 2).all()

        if not users:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

        # Trả về danh sách người dùng
        return {"status": 200, "users": users}
    except Exception as e:
        return {"status": 500, "message": f"Lỗi {e}"}
    
####################################################cập nhật trạng thái  tin tất cả user ####################################

@router.post("/admin/update-status")
def update_status_user(
    request: UpdateStatus, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    try:
        
        # Query user by maKH (user ID)
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == request.maKH).first()

        if not user_in_db:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate the new status
        if request.trangThai not in [0, 1, 2]:
            raise HTTPException(status_code=400, detail="Invalid status")

        # Check if transitioning from 0 to 1
        if user_in_db.trangThai == 0 and request.trangThai == 1:
            # Send notification email
            try:
                send_verification_email_from_admin(request.email)
            except Exception as email_error:
                raise HTTPException(status_code=500, detail=f"Failed to send email: {email_error}")

        # Update the status
        user_in_db.trangThai = request.trangThai

        # Commit the changes to the database
        db.commit()
        db.refresh(user_in_db)

        return {"status": 200, "message": "User status updated successfully"}

    except HTTPException as http_err:
        db.rollback()  # Rollback any changes if there's an error
        raise http_err  # Rethrow HTTP exceptions

    except Exception as e:
        db.rollback()  # Rollback any changes if there's an unexpected error
        return {"status": 500, "message": f"Error: {e}"}

    
@router.post("/update-user")
def update_user(request: UpdateUser, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    try:
        # Query user by user_id
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == request.maKH).first()

        if not user_in_db:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user fields from the request object
        if request.tenHienThi:
            user_in_db.tenHienThi = request.tenHienThi
        if request.tenKH:
            user_in_db.tenKH = request.tenKH
        if request.diaChi:
            user_in_db.diaChi = request.diaChi
        if request.ngaySinh:
            try:
                user_in_db.ngaySinh = datetime.strptime(request.ngaySinh, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Ngày sinh không hợp lệ. Định dạng phải là YYYY-MM-DD")
        if request.password:
            user_in_db.matKhau = get_password_hash(request.password)

        # Commit the changes to the database
        db.commit()
        db.refresh(user_in_db)

        return {"status": 200, "message": "User updated successfully", "user": user_in_db}
    
    except Exception as e:
        return {"status": 500, "message": f"Error: {e}"}


@router.get("/get-user/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    print(f"current_user: {current_user}")  # In ra để kiểm tra
    try:
        if current_user['user_id'] != user_id:  
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")

        # Tìm người dùng theo user_id
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == user_id).first()

        if not user_in_db:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

        # Trả về thông tin người dùng
        return {
            "status": 200,
            "user": {
                "email": user_in_db.email,
                "tenHienThi": user_in_db.tenHienThi,
                "tenKH": user_in_db.tenKH,
                "diaChi": user_in_db.diaChi,
                "ngaySinh": user_in_db.ngaySinh,
                "ngayDangKy": user_in_db.ngayDangKy,
                "soLuongToken": user_in_db.soLuongToken,
                "trangThai": user_in_db.trangThai,
            }
        }
    except Exception as e:
        print(f"Error: {e}")  # Log chi tiết lỗi
        return {"status": 500, "message": f"Lỗi: {e}"}

@router.post("/update_user_info")
def update_user_info(request: UpdateUserInfoRequest, db: Session = Depends(get_db)):
    
    user_in_db = db.query(KhachHang).filter(KhachHang.maKH == request.maKH).first()

    if not user_in_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_in_db.tenKH = request.tenKH
    user_in_db.tenHienThi = request.tenHienThi
    user_in_db.diaChi = request.diaChi
    user_in_db.ngaySinh = request.ngaySinh

    db.commit()
    db.refresh(user_in_db)

    return {"status": 200, "message": "User information updated successfully"}

@router.get("/user-info/{maKH}")
def get_user_info(maKH: int, db: Session = Depends(get_db)):
    """
    Fetch personal information of a user based on maKH (user ID).
    """
    try:
        # Query user information by maKH
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == maKH).first()

        if not user_in_db:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

        # Return user information
        return {
            "status": 200,
            "user": {
                "email": user_in_db.email,
                "tenHienThi": user_in_db.tenHienThi,
                "tenKH": user_in_db.tenKH,
                "diaChi": user_in_db.diaChi,
                "ngaySinh": user_in_db.ngaySinh,
                "ngayDangKy": user_in_db.ngayDangKy,
                "soLuongToken": user_in_db.soLuongToken,
                "trangThai": user_in_db.trangThai,
            }
        }
    except Exception as e:
        return {"status": 500, "message": f"Lỗi: {e}"}
    
    
@router.post("/send_messages_pdf")
def send_messages_pdf(
    email: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Đường dẫn thư mục tạm
        temp_dir = "/tmp/uploaded_files"
        temp_filepath = os.path.join(temp_dir, file.filename)

        # Kiểm tra và tạo thư mục nếu chưa tồn tại
        os.makedirs(temp_dir, exist_ok=True)

        # Lưu file từ UploadFile vào thư mục tạm
        with open(temp_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Log đường dẫn file
        print(f"File saved at: {temp_filepath}")

        # Gửi email với file đã lưu
        email_sent = send_pdf_email(email, temp_filepath)

        # Xóa file sau khi gửi xong
        os.remove(temp_filepath)

        if not email_sent:
            raise HTTPException(status_code=500, detail="Failed to send email")

        return {"status": 200, "message": "PDF sent to email successfully"}

    except Exception as e:
        # Ghi log lỗi chi tiết
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
