from pydantic import BaseModel

# Schema để yêu cầu mã OTP
class EmailRequest(BaseModel):
    email: str

# Schema để xác thực mã OTP
class OTPVerifyRequest(BaseModel):
    email: str
    otp_code: str
    
class UserRegistrationRequest(BaseModel):
    email: str
    otp_code: str
    tenHienThi: str
    ngaySinh: str
    tenKH: str
    diaChi: str
    password: str
    
    
class User(BaseModel):
    email: str
    password: str

