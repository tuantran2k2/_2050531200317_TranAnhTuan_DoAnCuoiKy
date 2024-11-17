from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database._database_mysql import engine, Base
from router import _user ,_cv ,_chatbot
import uvicorn
from models import CV, BoSuuTap,KhachHang,LichSuTroChuyen,PhuongXa,QuanHuyen,QuyenTruyCap, ThonTo,TinhThanh,ViToken
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(_user.router)
app.include_router(_cv.router)
app.include_router(_chatbot.router)
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

