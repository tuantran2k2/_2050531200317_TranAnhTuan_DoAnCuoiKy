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
    tenHienThi: str
    tenKH: str
    diaChi: str
    ngaySinh: str
    password: str
    
    
class User(BaseModel):
    email: str
    password: str

class UpdateUser(BaseModel):
    maKH: int
    email: str
    tenHienThi: str
    tenKH: str
    diaChi: str
    ngaySinh: str
    password: str

class UpdateStatus(BaseModel):
    maKH: int
    email :str
    trangThai: int
    
    
class UpdateUserInfoRequest(BaseModel):
    maKH: int
    tenHienThi: str
    tenKH: str
    diaChi: str
    ngaySinh: str
    
    