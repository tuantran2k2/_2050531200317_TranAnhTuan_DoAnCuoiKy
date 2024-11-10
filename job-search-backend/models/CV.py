from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class CV(Base):
    __tablename__ = "CV"

    maCV = Column(Integer, primary_key=True, autoincrement=True)
    tenCV = Column(String(100), nullable=False)
    Nganh = Column(String(100))
    KyNangMem = Column(String(100))
    KyNangChuyenNganh = Column(String(100))
    hocVan = Column(String(100))
    tinhTrang = Column(String(100))
    DiemGPA = Column(Float)
    soDienThoai = Column(String(15))
    email = Column(String(100))
    diaChi = Column(String(100))
    GioiThieu = Column(String(255))
    maKH = Column(Integer, ForeignKey("KhachHang.maKH"))

    # Quan hệ với bảng KhachHang
    khachhang = relationship("KhachHang", back_populates="cvs")
