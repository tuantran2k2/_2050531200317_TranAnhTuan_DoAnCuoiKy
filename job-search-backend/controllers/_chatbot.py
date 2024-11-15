from controllers import _cv 
from dependencies.dependencies import get_db
from models import BoSuuTap,KhachHang,LichSuTroChuyen,PhuongXa,QuanHuyen,QuyenTruyCap, ThonTo,TinhThanh,ViToken
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import _prompts ,_environments

def chatbot(id_cv, collection_id, ma_KH, query):
    try:
        # Lấy thông tin chi tiết từ cơ sở dữ liệu
        with next(get_db()) as db:
            cv_details = _cv.get_cv(id_cv, db)
            
        CV = f"""CV của tôi gồm những yêu cầu sau:
                    - Ngành Nghề: {cv_details.get('Nganh', 'Không có')}
                    - Kỹ năng mềm: {cv_details.get('KyNangMem', 'Không có')}
                    - Kỹ năng chuyên ngành: {cv_details.get('KyNangChuyenNganh', 'Không có')}
                    - Học vấn: {cv_details.get('hocVan', 'Không có')}
                    - GPA: {cv_details.get('DiemGPA', 'Không có')}
                    - Chứng chỉ: {cv_details.get('ChungChi', 'Không có')}"""
        
        file_path = f"../files/data/{ma_KH}/{id_cv}_{collection_id}_listCV.txt"

        # Đọc nội dung file với xử lý lỗi nếu không tìm thấy file
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                contexts = file.read()
        except FileNotFoundError:
            return "Không tìm thấy file"
        
        # Tạo prompt từ template và các biến đầu vào
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    _prompts.JOBS_CV.format(
                        Context=str(contexts), query=str(query)
                    ),
                ),
                ("human", str(query)),
            ]
        )

        # Thực thi chain và lấy kết quả
        chain = (
            prompt
            | _environments.get_llm(model="gpt-4o", temperature=0.7)
            | StrOutputParser()
        )
        
        answer = chain.invoke({"input": str(query)})

        return answer

    except Exception as e:
        # Xử lý mọi lỗi khác và trả về thông báo lỗi
        return f"Lỗi trong quá trình thực hiện: {e}"

