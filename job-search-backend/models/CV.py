from sqlalchemy import Column, Integer, String, Float, ForeignKey ,Text ,DateTime
from sqlalchemy.orm import relationship
from database._database_mysql import Base
from datetime import datetime

class CV(Base):
    __tablename__ = "CV"

    maCV = Column(Integer, primary_key=True, autoincrement=True)
    tenCV = Column(Text, nullable=False)
    Nganh = Column(Text)
    KyNangMem = Column(Text)
    KyNangChuyenNganh = Column(Text)
    kinhNghiem = Column(Text)
    hocVan = Column(Text)
    tinhTrang = Column(Text)
    DiemGPA = Column(Text)
    soDienThoai = Column(Text) 
    email = Column(Text)
    diaChi = Column(Text)
    GioiThieu = Column(Text)
    maKH = Column(Integer, ForeignKey("KhachHang.maKH"))
    ChungChi = Column(Text)
    trangThai = Column(Integer, default=1) 
    linkURL = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Quan hệ với bảng KhachHang
    khachhang = relationship("KhachHang", back_populates="cvs")
    bosutaps = relationship("BoSuTap", back_populates="cv")