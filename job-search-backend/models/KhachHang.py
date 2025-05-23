from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey ,TIMESTAMP, func , Text
from sqlalchemy.orm import relationship
from database._database_mysql import Base


class KhachHang(Base):
    __tablename__ = "KhachHang"

    maKH = Column(Integer, primary_key=True, autoincrement=True)
    tenHienThi = Column(String(100))
    tenKH = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    matKhau = Column(String(255), nullable=False)
    ngayDangKy = Column(Date)
    maQuyen = Column(Integer, ForeignKey("QuyenTruyCap.maQuyen"), default=2)
    soLuongToken = Column(Integer,default=0)
    diaChi = Column(Text)
    ngaySinh = Column(Date)
    trangThai = Column(Integer,default=0)


    quyen_truy_cap = relationship("QuyenTruyCap", back_populates="khachhangs")
    cvs = relationship("CV", back_populates="khachhang")
    bosutaps = relationship("BoSuTap", back_populates="khachhang")
    lichsugiaodichs = relationship("LichSuGiaoDich", back_populates="khachhang")
class OTP(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    otp_code = Column(String(6), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())