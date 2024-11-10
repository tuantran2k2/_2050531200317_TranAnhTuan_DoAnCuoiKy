from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class QuanHuyen(Base):
    __tablename__ = "QuanHuyen"

    maQuanHuyen = Column(Integer, primary_key=True, autoincrement=True)
    tenQuanHuyen = Column(String(100), nullable=False)
    maTinhThanh = Column(Integer, ForeignKey("TinhThanh.maTinhThanh"))

    # Quan hệ với bảng PhuongXa
    phuongxas = relationship("PhuongXa", back_populates="quanhuyen")
    tinhthanh =  relationship("TinhThanh", back_populates="quanhuyens")
    
    