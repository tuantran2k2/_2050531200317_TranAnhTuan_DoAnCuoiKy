from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class ThonTo(Base):
    __tablename__ = "ThonTo"

    maThonTo = Column(Integer, primary_key=True, autoincrement=True)
    tenThonTo = Column(String(100), nullable=False)
    maPhuongXa = Column(Integer, ForeignKey("PhuongXa.maPhuongXa"))

    # Quan hệ với bảng KhachHang
    khachhangs = relationship("KhachHang", back_populates="thonto")
    phuongxa = relationship("PhuongXa", back_populates="thontos")
