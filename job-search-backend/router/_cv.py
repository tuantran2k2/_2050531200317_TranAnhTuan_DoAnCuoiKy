from fastapi import APIRouter, Depends , File, UploadFile , Form,HTTPException ,Request
from models.CV import CV
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from dependencies import security
from pathlib import Path
from controllers import _cv
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from shutil import copyfileobj 
from schemas._cv import MaKHRequest , UpdateStatus
from models.KhachHang import KhachHang
from controllers import _user
from dependencies.security import  verified_user

import json  # Import thư viện JSON
import io
import _constants
import aiofiles


router = APIRouter(
    prefix="/api/v1/cv",
    tags=["cv"],
)

################################ upload file CV ########################################################

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=500, detail="Authorization header missing")
    
    # Xác thực người dùng
    payload = verified_user(auth_header)
    if not payload:
        raise HTTPException(status_code=500, detail="Invalid token or unauthorized")
    
    return payload



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
        answer , total_token = _cv.chatbot_cv(noi_dung_cv)
        
        print("answer")
        print(answer)
        print("answeradsadasdad")
            
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == ma_KH).first()
        
        if total_token > user_in_db.soLuongToken:
            content = {
            "message": "Số dư của bạn không đủ"
            }
            return JSONResponse(content=content, status_code=403)
        
        update_mount = user_in_db.soLuongToken - total_token
        _user.update_amount(maKH=ma_KH,new_money=update_mount,db=db)
        
        if (answer.get("hopLe") == False):
            content = {
                "status": 500,
                "message": answer.get("lyDo")
            }
            return JSONResponse(content=content, status_code=500)
        else:
            # Kiểm tra nếu answer có giá trị cho các key cần thiết
            new_cv = CV(
                tenCV=answer.get("tenDayDu", "null"),
                Nganh=answer.get("nganhNghe", "null"),
                KyNangMem=", ".join(answer.get("kyNangMem", ["null"])) if isinstance(answer.get("kyNangMem"), list) else answer.get("kyNangMem", "null"),
                KyNangChuyenNganh=", ".join(answer.get("kyNangChuyenNganh", ["null"])) if isinstance(answer.get("kyNangChuyenNganh"), list) else answer.get("kyNangChuyenNganh", "null"),
                hocVan=answer.get("hocVan", "null"),
                tinhTrang="null",
                DiemGPA=answer.get("diemGPA", "null"),
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

            # Cập nhật hoặc tạo file JSON lưu danh sách CV
            json_path = file_dir / "cv_list.json"
            if json_path.exists():
                with json_path.open("r", encoding="utf-8") as json_file:
                    cv_list = json.load(json_file)  # Đọc nội dung cũ
            else:
                cv_list = []  # Nếu chưa tồn tại, tạo danh sách rỗng
            name_parts = answer.get("tenDayDu", "null").split()
            # Lấy phần cuối cùng
            last_name = name_parts[-1]
            # Thêm thông tin CV mới vào danh sách
            cv_list.append({
                "id_cv": maCV,
                "ten_cv": last_name,
                "chuyen_nganh" : answer.get("nganhNghe", "null"),
            })

            # Ghi lại file JSON
            with json_path.open("w", encoding="utf-8") as json_file:
                json.dump(cv_list, json_file, ensure_ascii=False, indent=4)

            # Chuẩn bị phản hồi
            content = {
                "status": 200,
                "message": "File uploaded, processed, and saved successfully."
            }
            return JSONResponse(content=content, status_code=200)

    except Exception as e:
        content = {"status": 400, "message": "Error uploading files: " + str(e)}
        return JSONResponse(content=content, status_code=400)


@router.post("/list_cv")
async def list_cv(request: MaKHRequest):
    try:
        # Gọi hàm get_list_cv để lấy danh sách CV
        response = _cv.get_list_cv(request.makh)
        return response  # Trả về JSONResponse từ hàm get_list_cv
    except Exception as e:
        # Xử lý lỗi nếu có
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while fetching CV list: {str(e)}"
        )
        
@router.get("/admin/list_cv")
async def list_cv(db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    try:
        # Gọi hàm get_list_cv_admin
        response = _cv.get_list_cv_admin(db)
        return response  # Trả về kết quả từ JSONResponse của hàm
    except Exception as e:
        # Bắt lỗi và trả về HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while fetching CV list: {str(e)}"
        )
        
@router.post("/admin/update-status")
def update_status_user(
    request: UpdateStatus, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    try:
        
        # Query user by maKH (user ID)
        cv_in_db = db.query(CV).filter(CV.maCV == request.maCV).first()

        if not cv_in_db:
            raise HTTPException(status_code=404, detail="CV not found")

        # Validate the new status
        if request.trangThai not in [0, 1]:
            raise HTTPException(status_code=400, detail="Invalid status")

        # Update the status
        cv_in_db.trangThai = request.trangThai

        # Commit the changes to the database
        db.commit()
        db.refresh(cv_in_db)

        return {"status": 200, "message": "CV status updated successfully"}

    except HTTPException as http_err:
        db.rollback()  # Rollback any changes if there's an error
        raise http_err  # Rethrow HTTP exceptions

    except Exception as e:
        db.rollback()  # Rollback any changes if there's an unexpected error
        return {"status": 500, "message": f"Error: {e}"}


@router.delete("/cv/{id_CV}/maKH/{maKH}")
def api_delete_cv(id_CV: int, maKH: int, db: Session = Depends(get_db)):
    try:
        # Gọi hàm delete_cv và trả về kết quả trực tiếp
        return _cv.delete_cv(id_CV, maKH, db)

    except Exception as e:
        # Bắt lỗi chung và trả về phản hồi chi tiết
        raise HTTPException(status_code=500, detail=f"Lỗi API: {str(e)}")
