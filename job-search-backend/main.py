from fastapi import FastAPI
from database._database_mysql import engine, Base
from router import _user ,_cv
import uvicorn
from models import CV, BoSuuTap,KhachHang,LichSuTroChuyen,PhuongXa,QuanHuyen,QuyenTruyCap, ThonTo,TinhThanh,ViToken
app = FastAPI()

app.include_router(_user.router)
app.include_router(_cv.router)

# Khởi tạo các router cho API
# app.include_router(...)
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        limit_concurrency=1000,       
        timeout_keep_alive=3600        # Tăng thời gian chờ kết nối lên 1 giờ (3600 giây)
    )

