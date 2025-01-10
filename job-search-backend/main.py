from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database._database_mysql import engine, Base
from router import _user ,_cv ,_chatbot , boSuuTap , _lichSu , _lichSuGiaoDich ,_thongKe , _jobs
import uvicorn
from models import CV, BoSuuTap, KhachHang, LichSuTroChuyen, QuyenTruyCap, LichSuGiaoDich , Jobs

app = FastAPI()

# # Tự động tạo bảng trong cơ sở dữ liệu
# Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(_user.router)
app.include_router(_cv.router)
app.include_router(_chatbot.router)
app.include_router(boSuuTap.router)
app.include_router(_lichSu.router)
app.include_router(_lichSuGiaoDich.router)
app.include_router(_thongKe.router)
app.include_router(_jobs.router)

if __name__ == "__main__":
    uvicorn.run(
    app,
    host="192.168.30.1",  
    port=6006,      
    limit_concurrency=1000, 
    timeout_keep_alive=36000,  
    timeout_graceful_shutdown=120,  # Thời gian để đóng các kết nối khi tắt server
    log_level="info"
)