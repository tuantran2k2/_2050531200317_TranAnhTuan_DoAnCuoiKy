from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class QuyenTruyCap (Base):
    __tablename__ = "QuyenTruyCap"

    maQuyen = Column(Integer, primary_key=True, autoincrement=True)
    tenQuyen = Column(String(100), nullable=False)
    
    khachhangs = relationship("KhachHang", back_populates="quyen_truy_cap")
