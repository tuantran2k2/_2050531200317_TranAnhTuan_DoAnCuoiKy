from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class PhuongXa(Base):
    __tablename__ = "PhuongXa"

    maPhuongXa = Column(Integer, primary_key=True, autoincrement=True)
    tenPhuongXa = Column(String(100), nullable=False)
    maQuanHuyen = Column(Integer, ForeignKey("QuanHuyen.maQuanHuyen"))

    # Quan hệ với bảng ThonTo
    thontos = relationship("ThonTo", back_populates="phuongxa")
    quanhuyen = relationship("QuanHuyen", back_populates="phuongxas")
