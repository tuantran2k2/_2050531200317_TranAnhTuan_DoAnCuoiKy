from sqlalchemy import Column, Integer, ForeignKey, String, Enum, TIMESTAMP , BIGINT
from sqlalchemy.orm import relationship
from database._database_mysql import Base
from datetime import datetime

class LichSuGiaoDich(Base):
    __tablename__ = 'lichSuGiaoDich'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Mã giao dịch
    maKH = Column(Integer, ForeignKey('KhachHang.maKH'), nullable=False)  # Khóa ngoại đúng tên bảng KhachHang
    order_id = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False)
    transaction_type = Column(Enum('credit', 'debit'), default='credit', nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(Enum('PENDING', 'PAID', 'FAILED', 'CANCELLED'), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    token = Column(BIGINT)

    khachhang = relationship("KhachHang", back_populates="lichsugiaodichs")