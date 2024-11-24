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
            | _environments.get_llm(model="gpt-4o", temperature=0)
            | StrOutputParser()
        )
        
        # Invoke the chain and get the response
        answer = chain.invoke({"input": ""})

        # Filter out any non-JSON text and parse JSON content
        try:
            # Extract JSON part only using regex
            json_text_match = re.search(r"\{.*\}", answer, re.DOTALL)
            if json_text_match:
                json_text = json_text_match.group(0)
                answer_json = json.loads(json_text)
                return answer_json
            else:
                print("Không tìm thấy JSON hợp lệ trong đầu ra.")
                return answer
        except json.JSONDecodeError as e:
            print(f"Lỗi: Đầu ra không phải là JSON hợp lệ: {e}")
            return answer
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý chatbot_cv: {e}")
        return None

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
