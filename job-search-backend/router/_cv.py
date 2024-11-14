from fastapi import APIRouter, Depends , File, UploadFile , Form
from models.CV import CV
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from dependencies import security
from pathlib import Path
from controllers import _cv
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from shutil import copyfileobj

import io
import _constants
import aiofiles


router = APIRouter(
    prefix="/api/v1/cv",
    tags=["cv"],
)

################################ upload file CV ########################################################
@router.post("/upload_files")
async def upload_files(
    ma_KH: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Đọc nội dung file vào bộ nhớ
        file_content = await file.read()  # Đọc toàn bộ nội dung của file
        
        # Chuyển đổi file_content thành một đối tượng BytesIO để có thể sử dụng seek
        file_stream = io.BytesIO(file_content)  # Wrap file_content in BytesIO

        # Truyền file_stream vào pdfminer để xử lý
        noi_dung_cv = _cv.extract_text_from_pdf(file_stream)  # Pass file_stream instead of file_content
        answer = _cv.chatbot_cv(noi_dung_cv)

        # Kiểm tra nếu answer có giá trị cho các key cần thiết
        new_cv = CV(
            tenCV=answer.get("tenDayDu", "null"),
            Nganh=answer.get("nganhNghe", "null"),
            KyNangMem=", ".join(answer.get("kyNangMem", ["null"])) if isinstance(answer.get("kyNangMem"), list) else answer.get("kyNangMem", "null"),
            KyNangChuyenNganh=", ".join(answer.get("kyNangChuyenNganh", ["null"])) if isinstance(answer.get("kyNangChuyenNganh"), list) else answer.get("kyNangChuyenNganh", "null"),
            hocVan=answer.get("hocVan", "null"),
            tinhTrang="null",
            DiemGPA=float(answer.get("diemGPA", 0.0)) if answer.get("diemGPA") else 0.0,
            soDienThoai=answer.get("soDienThoai", "null"),
            email=answer.get("email", "null"),
            diaChi=answer.get("diaChi", "null"),
            GioiThieu=answer.get("gioiThieu", "null"),
            maKH=ma_KH,
            ChungChi=answer.get("chungChi", "null")
        )
        db.add(new_cv)
        db.commit()
        db.refresh(new_cv)

        maCV = new_cv.maCV  # Lấy ID của bản ghi mới tạo làm mã CV
        file_dir = Path(f"./files/data/{ma_KH}")
        file_dir.mkdir(parents=True, exist_ok=True)

        # Tạo đường dẫn file với tên theo định dạng yêu cầu
        file_path = file_dir / f"{maCV}_{file.filename}"

        # Lưu file vào thư mục
        with file_path.open("wb") as buffer:
            buffer.write(file_content)  # Ghi nội dung file từ bộ nhớ

        # Chuẩn bị phản hồi
        content = {
            "status": 200,
            "message": "File uploaded, processed, and saved successfully."
        }
        return JSONResponse(content=content, status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error uploading files: " + str(e)}
        return JSONResponse(content=content, status_code=400)
