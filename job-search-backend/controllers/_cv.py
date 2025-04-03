from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session
from models.CV import CV
from pathlib import Path
from fastapi.responses import JSONResponse

import re
import json
import pdfplumber
import _prompts
import _environments

def extract_text_from_pdf(file_path):
    """Extracts text from each page of a PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Lỗi khi đọc file PDF: {e}")
        return None
    return text

def chatbot_cv(noidung_cv):
    """Processes CV content through a language model to extract key information."""
    if not noidung_cv:
        print("Nội dung CV trống.")
        return None
    
    input_tokens = len(noidung_cv)
    # Create the prompt with context
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _prompts.CV_USER.format(
                    context=str(noidung_cv),
                ),
            )
        ]
    )

    try:
        # Initialize the language model chain
        chain = (
            prompt
            | _environments.get_llm(model="gpt-4o", temperature=0.7)
            | StrOutputParser()
        )
        
        # Invoke the chain and get the response
        answer = chain.invoke({"input": ""})
        
        output_tokens = len(answer)
        total_tokens = input_tokens + output_tokens

        # Filter out any non-JSON text and parse JSON content
        try:
            # Extract JSON part only using regex
            json_text_match = re.search(r"\{.*\}", answer, re.DOTALL)
            if json_text_match:
                json_text = json_text_match.group(0)
                answer_json = json.loads(json_text)
                return answer_json , total_tokens
            else:
                print("Không tìm thấy JSON hợp lệ trong đầu ra.")
                return answer , total_tokens
        except json.JSONDecodeError as e:
            print(f"Lỗi: Đầu ra không phải là JSON hợp lệ: {e}")
            return answer , total_tokens
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý chatbot_cv: {e}")
        return None , None

def get_cv(id_CV: int, db: Session):
    # Truy vấn CV dựa vào id_CV
    cv = db.query(CV).filter(CV.maCV == id_CV).first()
    print(cv) 
    # Kiểm tra nếu không tìm thấy CV
    if cv is None:
        return None

    # Chuẩn bị dữ liệu để trả về
    cv_data = {
        "maCV": cv.maCV,
        "tenCV": cv.tenCV,
        "Nganh": cv.Nganh,
        "KyNangMem": cv.KyNangMem,
        "KyNangChuyenNganh": cv.KyNangChuyenNganh,
        "hocVan": cv.hocVan,
        "tinhTrang": cv.tinhTrang,
        "DiemGPA": cv.DiemGPA,
        "soDienThoai": cv.soDienThoai,
        "email": cv.email,
        "diaChi": cv.diaChi,
        "GioiThieu": cv.GioiThieu,
        "maKH": cv.maKH,
        "ChungChi": cv.ChungChi
    }

   
    return cv_data


def get_list_cv(maKH: int):
    try:
        # Đường dẫn thư mục và file JSON
        file_dir = Path(f"./files/data/{maKH}")
        json_path = file_dir / "cv_list.json"
        
        # Kiểm tra file JSON tồn tại
        if not json_path.exists():
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"No CV data found for maKH: {maKH}"
                },
                status_code=404
            )
        
        # Đọc nội dung từ file JSON
        with json_path.open("r", encoding="utf-8") as json_file:
            cv_data = json.load(json_file)
        
        # Chuẩn bị dữ liệu để trả về
        return JSONResponse(
            content={
                "status": 200,
                "message": "List of CVs retrieved successfully.",
                "data": cv_data
            },
            status_code=200
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status": 400,
                "message": f"Error retrieving CV list: {str(e)}"
            },
            status_code=400
        )

def delete_cv(id_CV: int, maKH: int, db: Session):
    """
    Xóa CV dựa trên id_CV và maKH, đồng thời cập nhật JSON và xóa file PDF tương ứng.
    
    Args:
        id_CV (int): ID của CV cần xóa.
        maKH (int): Mã khách hàng sở hữu CV.
        db (Session): Phiên làm việc với cơ sở dữ liệu.
    
    Returns:
        JSONResponse: Kết quả của quá trình xóa.
    """
    try:
        # Đường dẫn thư mục và file JSON
        file_dir = Path(f"./files/data/{maKH}")
        json_path = file_dir / "cv_list.json"
        
        # Kiểm tra sự tồn tại của thư mục và file JSON
        if not file_dir.exists():
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"Directory for maKH {maKH} not found."
                },
                status_code=404
            )
        if not json_path.exists():
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"cv_list.json for maKH {maKH} not found."
                },
                status_code=404
            )
        
        # Đọc và cập nhật JSON
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Kiểm tra nếu id_CV có trong JSON
        cv_exists_in_json = any(cv["id_cv"] == id_CV for cv in data)
        if not cv_exists_in_json:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"CV with id {id_CV} not found in JSON for maKH {maKH}."
                },
                status_code=404
            )
        
        # Lọc dữ liệu JSON
        updated_data = [cv for cv in data if cv["id_cv"] != id_CV]
        
        # Ghi lại file JSON
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)
        
        # Truy vấn CV từ database
        cv = db.query(CV).filter(CV.maCV == id_CV, CV.maKH == maKH).first()
        
        # Xóa file PDF tương ứng
        for file in file_dir.iterdir():
            if file.is_file() and file.suffix == ".pdf" and file.name.startswith(f"{id_CV}_"):
                file.unlink()
        
        # Kiểm tra nếu không tìm thấy CV trong database
        if cv is None:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": f"CV with id {id_CV} and maKH {maKH} not found in database."
                },
                status_code=404
            )
        
        # Xóa CV khỏi database
        db.delete(cv)
        db.commit()
        
        # Trả về phản hồi thành công
        return JSONResponse(
            content={
                "status": 200,
                "message": f"CV with id {id_CV} and maKH {maKH} deleted successfully."
            },
            status_code=200
        )
    
    except Exception as e:
        # Rollback nếu có lỗi
        db.rollback()
        return JSONResponse(
            content={
                "status": 500,
                "message": f"Error deleting CV: {str(e)}"
            },
            status_code=500
        )
        
        
def get_list_cv_admin(db: Session):
    try:
        # Lấy tất cả CV từ cơ sở dữ liệu
        cvs = db.query(CV).all()

        # Nếu không có CV nào trong cơ sở dữ liệu
        if not cvs:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": "No CV data found"
                },
                status_code=404
            )
        
        cv_data = [
            {
                "maCV": cv.maCV,
                "tenCV": cv.tenCV,
                "Nganh": cv.Nganh,
                "KyNangMem": cv.KyNangMem,
                "KyNangChuyenNganh": cv.KyNangChuyenNganh,
                "hocVan": cv.hocVan,
                "tinhTrang": cv.tinhTrang,
                "DiemGPA": cv.DiemGPA,
                "soDienThoai": cv.soDienThoai,
                "email": cv.email,
                "diaChi": cv.diaChi,
                "GioiThieu": cv.GioiThieu,
                "ChungChi": cv.ChungChi,
                "maKH": cv.maKH,
                "trangThai": cv.trangThai  
            } for cv in cvs
        ]
        
        # Trả về dữ liệu dưới dạng JSON
        return JSONResponse(
            content={
                "status": 200,
               "cvs": cv_data
            },
            status_code=200
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status": 400,
                "message": f"Error retrieving CV list: {str(e)}"
            },
            status_code=400
        )


def update_status_admin(db: Session , trangThai : int , maCV: int):
    try:
        # Lấy tất cả CV từ cơ sở dữ liệu
        cvs = db.query(CV).all()

        # Nếu không có CV nào trong cơ sở dữ liệu
        if not cvs:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": "No CV data found"
                },
                status_code=404
            )
        
        cv_data = [
            {
                "maCV": cv.maCV,
                "tenCV": cv.tenCV,
                "Nganh": cv.Nganh,
                "KyNangMem": cv.KyNangMem,
                "KyNangChuyenNganh": cv.KyNangChuyenNganh,
                "hocVan": cv.hocVan,
                "tinhTrang": cv.tinhTrang,
                "DiemGPA": cv.DiemGPA,
                "soDienThoai": cv.soDienThoai,
                "email": cv.email,
                "diaChi": cv.diaChi,
                "GioiThieu": cv.GioiThieu,
                "ChungChi": cv.ChungChi,
                "maKH": cv.maKH,
                "trangThai": cv.trangThai  
            } for cv in cvs
        ]
        
        # Trả về dữ liệu dưới dạng JSON
        return JSONResponse(
            content={
                "status": 200,
               "cvs": cv_data
            },
            status_code=200
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status": 400,
                "message": f"Error retrieving CV list: {str(e)}"
            },
            status_code=400
        )
