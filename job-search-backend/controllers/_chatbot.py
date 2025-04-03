from controllers import _cv 
from dependencies.dependencies import get_db
from models import BoSuuTap,KhachHang,LichSuTroChuyen,QuyenTruyCap
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import _prompts ,_environments

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.LichSuTroChuyen import LichSuTroChuyen
from models.BoSuuTap import BoSuTap
from models.KhachHang import KhachHang
from controllers.rag.chatbot import _chatbot_cv
from datetime import datetime

import _prompts
import _environments
from controllers import _user

def chatbot(id_cv, collection_id, ma_KH, query):
    try:
        total_characters = 0
      
        # Lấy thông tin chi tiết từ cơ sở dữ liệu
        with next(get_db()) as db:
            cv_details = _cv.get_cv(id_cv, db)
            history = ""
            history_records = db.query(LichSuTroChuyen).filter(LichSuTroChuyen.maBST == collection_id).order_by(LichSuTroChuyen.timestamp.desc()).limit(10).all()
            for record in reversed(history_records):  # Đảo ngược thứ tự để giữ ngữ cảnh
                history += f"User: {record.cauHoi}\nBot: {record.phanHoi}\n"
        
        CV = f"""CV của tôi gồm những thông tin sau:
                    - Họ và Tên: {cv_details.get('tenCV', 'Không có')}
                    - Địa chỉ : {cv_details.get('diaChi', 'Không có')}
                    - Giới Thiệu : {cv_details.get('GioiThieu', 'Không có')}
                    - Ngành Nghề: {cv_details.get('Nganh', 'Không có')}
                    - Kỹ năng mềm: {cv_details.get('KyNangMem', 'Không có')}
                    - Kỹ năng chuyên ngành: {cv_details.get('KyNangChuyenNganh', 'Không có')}
                    - Kinh nghiệm làm việc: {cv_details.get('KinhNghiem', 'Không có')}
                    - Học vấn: {cv_details.get('hocVan', 'Không có')}
                    - GPA: {cv_details.get('DiemGPA', 'Không có')}
                    - Chứng chỉ: {cv_details.get('ChungChi', 'Không có')}"""
        
        file_path = f"./files/data/{ma_KH}/{id_cv}_{collection_id}_listCV.txt"
        print(file_path)
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
                    _prompts.CV_Optimize.format(
                        CV=str(CV),  # Thay đổi biến đầu vào cho template
                        list_jobs=str(contexts),  # Biến danh sách công việc
                        history=str(history)  # Lịch sử cuộc trò chuyện
                    ),
                ),
                ("human", str(query)),  # Truy vấn từ người dùng
            ]
        )

        # Thực thi chain và lấy kết quả
        chain = (
            prompt
            | _environments.get_llm(model="gpt-4o", temperature=0.7)
            | StrOutputParser()
        )
        
        answer = chain.invoke({"input": str(query)})
        
        total_characters = len(query) + len(answer)

        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == ma_KH).first()
        
        if total_characters > user_in_db.soLuongToken:
            return 400
        
        update_mount = user_in_db.soLuongToken - total_characters
        
        _user.update_token(maKH=ma_KH,new_token=update_mount,db=db)
        
        with next(get_db()) as db:
            
            history_record = LichSuTroChuyen(
                cauHoi=query,
                phanHoi=answer,
                tongSoToken=total_characters,
                maBST = collection_id
            )
            
            db.add(history_record)
            db.commit()
    
        return answer 

    except Exception as e:
        # Xử lý mọi lỗi khác và trả về thông báo lỗi
        return f"Lỗi trong quá trình thực hiện: {e}"


def find_job(id_cv , k ,collection_id , ma_KH):
    with next(get_db()) as db:
        cv_details = _cv.get_cv(id_cv, db)
        
    CV_user = f"""Vui lòng tìm {k} công việc phù hợp nhất dựa trên các tiêu chí sau trong hồ sơ của ứng viên:
        - Ngành nghề: {cv_details.get('Nganh', 'Không rõ')}
        - Kỹ năng chuyên môn: {cv_details.get('KyNangChuyenNganh', 'Không rõ')}
        - Kinh nghiệm làm việc: {cv_details.get('KinhNghiem', 'Không rõ')}
        - Trình độ học vấn: {cv_details.get('hocVan', 'Không rõ')}
        - Điểm trung bình (GPA): {cv_details.get('DiemGPA', 'Không rõ')}
        - Kỹ năng mềm: {cv_details.get('KyNangMem', 'Không rõ')}
        - Chứng chỉ: {cv_details.get('ChungChi', 'Không rõ')}
        Hãy ưu tiên các công việc đáp ứng tốt nhất những tiêu chí trên."""
        
    answer = _chatbot_cv.chatbot_rag_crewai(CV_user,k,collection_id,ma_KH,id_cv)
    
    with next(get_db()) as db:
        bosutap_in_db = db.query(BoSuTap).filter(BoSuTap.ma_BST == collection_id).first()
        if not bosutap_in_db:
            BST = BoSuTap(
                ma_BST=collection_id,
                TenBST=f"tìm {k} công việc về Ngành Nghề: {cv_details.get('Nganh', 'Không có')}",
                ngayTao=datetime.now(),
                maKH=ma_KH,
                maCV=id_cv
            )
            db.add(BST)  
            db.commit()  
        
        total_characters = len(CV_user) + len(answer)
        
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == ma_KH).first()
        
        if total_characters > user_in_db.soLuongToken:
            return 400
        
        update_mount = user_in_db.soLuongToken - total_characters
        
        _user.update_token(maKH=ma_KH,new_token=update_mount,db=db)
        history_record = LichSuTroChuyen(
            cauHoi=CV_user,
            phanHoi=answer,
            tongSoToken=total_characters,
            maBST = collection_id
        )
        
        db.add(history_record)
        db.commit()
        return answer
    


