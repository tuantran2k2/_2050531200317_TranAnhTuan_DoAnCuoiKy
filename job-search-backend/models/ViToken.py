from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class ViToken(Base):
    __tablename__ = "ViToken"

    maVi = Column(Integer, primary_key=True, autoincrement=True)
    SoLuong = Column(Integer)

    # Quan hệ với KhachHang
    khach_hangs = relationship("KhachHang", back_populates="vi_token")