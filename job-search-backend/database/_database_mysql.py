from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, declarative_base
import _constants

# Chuỗi kết nối tới MySQL
SQLALCHEMY_DATABASE_URL = _constants.SQLALCHEMY_DATABASE_URL
# Tạo engine kết nối tới MySQL, không cần tham số encoding
engine = create_engine(SQLALCHEMY_DATABASE_URL,  
    poolclass=QueuePool,
    pool_recycle=28000,  # Thời gian tối đa để kết nối tái sử dụng
    pool_pre_ping=True   # Kiểm tra kết nối trước khi dùng)
)
# Tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo Base cho các model kế thừa
Base = declarative_base()
