from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class BoSuTap(Base):
    __tablename__ = "BoSuTap"

    ma_BST = Column(Integer, primary_key=True, autoincrement=True)
    TenBST = Column(String(100), nullable=False)
    ngayTao = Column(Date)
    maKH = Column(Integer, ForeignKey("KhachHang.maKH"))

    # Quan hệ với bảng KhachHang
    khachhang = relationship("KhachHang", back_populates="bosutaps")
    lichsutrochuyens = relationship("LichSuTroChuyen", back_populates="bosutap")
