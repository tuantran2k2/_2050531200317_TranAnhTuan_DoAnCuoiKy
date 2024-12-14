from sqlalchemy import Column, Integer, String, Float, ForeignKey ,Text
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class CV(Base):
    __tablename__ = "CV"

    maCV = Column(Integer, primary_key=True, autoincrement=True)
    tenCV = Column(Text, nullable=False)
    Nganh = Column(Text)
    KyNangMem = Column(Text)
    KyNangChuyenNganh = Column(Text)
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
    # Quan hệ với bảng KhachHang
    khachhang = relationship("KhachHang", back_populates="cvs")
