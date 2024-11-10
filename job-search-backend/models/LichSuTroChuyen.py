from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database._database_mysql import Base

class LichSuTroChuyen(Base):
    __tablename__ = "LichSuTroChuyen"

    ma_LSTC = Column(Integer, primary_key=True, autoincrement=True)
    cauHoi = Column(String(255))
    phanHoi = Column(String(255))
    tongSoToken = Column(Integer)
    maBST = Column(Integer, ForeignKey("BoSuTap.ma_BST"))

    # Quan hệ với bảng BoSuTap
    bosutap = relationship("BoSuTap", back_populates="lichsutrochuyens")
