from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class TinhThanh(Base):
    __tablename__ = "TinhThanh"

    maTinhThanh = Column(Integer, primary_key=True, autoincrement=True)
    tenTinhThanh = Column(String(100), nullable=False)

    # Quan hệ với bảng QuanHuyen
    quanhuyens = relationship("QuanHuyen", back_populates="tinhthanh")
