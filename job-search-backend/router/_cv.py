from fastapi import APIRouter, Depends , File, UploadFile , Form,HTTPException ,Request
from models.CV import CV
from fastapi.responses import JSONResponse
from pathlib import Path
from controllers import _cv
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from shutil import copyfileobj 
from schemas._cv import MaKHRequest , UpdateStatus
from models.KhachHang import KhachHang
from controllers import _user
from dependencies.security import  verified_user
from controllers.aws3_pdf import connect_s3 
import json  # Import thư viện JSON
import io
import uuid
import magic


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
        # Kiểm tra dung lượng file ngay từ đầu (giới hạn 3MB)
        file_dir = Path(f"./files/data/{ma_KH}")
        file_dir.mkdir(parents=True, exist_ok=True)
        json_path = file_dir / "cv_list.json"
        max_size_mb = 3
        max_size_bytes = max_size_mb * 1024 * 1024

        # Kiểm tra dung lượng file từ thông tin tiêu đề hoặc đọc thủ công
        file_size = file.size if hasattr(file, 'size') else file.file._file.tell()

        if not file_size or file_size > max_size_bytes:
            return JSONResponse(
                content={"status": 400, "message": f"File vượt quá {max_size_mb}MB"},
                status_code=400
            )
        
        #kiểm tra file trùng 
        with json_path.open("r", encoding="utf-8") as json_file:
            cv_list = json.load(json_file)
            
        if json_path.exists():
            if any(cv.get("nameFile") == file.filename for cv in cv_list):
                return JSONResponse(
                    content={"status": 400, "message": f"File '{file.filename}' đã tồn tại. Vui lòng đổi tên file trước khi upload."},
                    status_code=400
                )
        else:
            cv_list = []
        # Đọc nội dung file
        file_content = await file.read()

        # Kiểm tra nội dung file không rỗng
        if not file_content.strip():
            return JSONResponse(
                content={"status": 400, "message": "File content is empty or invalid."},
                status_code=400
            )

        # Kiểm tra MIME type
        file_type = magic.from_buffer(buffer=file_content, mime=True)
        if not file_type or file_type not in connect_s3.SUPPORT_FILE_TYPES:
            return JSONResponse(
                content={"status": 400, "message": f"Unsupported file type: {file_type}"},
                status_code=400
            )

        # Reset con trỏ để xử lý lại nội dung file
        await file.seek(0)

        # Xử lý nội dung file (trích xuất văn bản từ PDF và gọi chatbot)
        try:
            noi_dung_cv = _cv.extract_text_from_pdf(io.BytesIO(file_content))
            answer, total_token = _cv.chatbot_cv(noi_dung_cv)
        except Exception as e:
            return JSONResponse(
                content={"status": 400, "message": f"Error processing file: {str(e)}"},
                status_code=400
            )

        # Kiểm tra số dư token của khách hàng
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == ma_KH).first()
        if total_token > user_in_db.soLuongToken:
            return JSONResponse(
                content={"message": "Số dư của bạn không đủ."},
                status_code=403
            )

        update_mount = user_in_db.soLuongToken - total_token
        _user.update_token(maKH=ma_KH, new_token=update_mount, db=db)

        # Xử lý kết quả từ chatbot
        if not answer.get("hopLe", True):
            return JSONResponse(
                content={"status": 500, "message": answer.get("lyDo", "Lỗi không xác định")},
                status_code=500
            )

        # Lưu file lên S3
        file_extension = connect_s3.SUPPORT_FILE_TYPES[file_type]
        file_extension = file_extension[0] if isinstance(file_extension, list) else file_extension
        file_key = f"{uuid.uuid4()}.{file_extension}"

        file_url = await connect_s3.s3_upload(
            contents=file_content,
            key=file_key,
            mime_type=file_type
        )

        # Lưu thông tin vào cơ sở dữ liệu
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
            ChungChi=answer.get("chungChi", "null"),
            linkURL=file_url
        )
        db.add(new_cv)
        db.commit()
        db.refresh(new_cv)

        maCV = new_cv.maCV
        
        # Lưu file vào thư mục local
        file_path = file_dir / f"{maCV}_{file.filename}"
        with file_path.open("wb") as buffer:
            buffer.write(file_content)

        # Cập nhật hoặc tạo file JSON
        name_parts = answer.get("tenDayDu", "null").split()
        last_name = name_parts[-1] if name_parts else ""
        cv_list.append({
            "id_cv": maCV,
            "ten_cv": last_name,
            "chuyen_nganh": answer.get("nganhNghe", "null"),
            "trangThai": new_cv.trangThai,
            "linkURL": new_cv.linkURL,
            "nameFile" : file.filename  
        })

        with json_path.open("w", encoding="utf-8") as json_file:
            json.dump(cv_list, json_file, ensure_ascii=False, indent=4)

        return JSONResponse(
            content={"status": 200, "message": "File uploaded, processed, and saved successfully."},
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"status": 400, "message": "Error uploading files: " + str(e)},
            status_code=400
        )


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
        
        file_dir = Path(f"./files/data/{request.makh}")
        
        json_path = file_dir / "cv_list.json"
        
        if not json_path.exists():
            return {"status": 404, "message": "File JSON không tồn tại."}

        with json_path.open("r", encoding="utf-8") as json_file:
            cv_list = json.load(json_file)

        for cv in cv_list:
            if cv.get("id_cv") == request.maCV:
                cv["trangThai"] = request.trangThai
                break
        else:
            return {"status": 404, "message": "Không tìm thấy CV với ID đã cho."}
        
        with json_path.open("w", encoding="utf-8") as json_file:
            json.dump(cv_list, json_file, ensure_ascii=False, indent=4)

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
