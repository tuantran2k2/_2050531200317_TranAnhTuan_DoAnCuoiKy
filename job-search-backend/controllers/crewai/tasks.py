from crewai import Task
from textwrap import dedent
from controllers.rag import _clean_data
from controllers import _cv 
from controllers.rag.chatbot import _chatbot_cv
from dependencies.dependencies import get_db
from models import BoSuuTap,KhachHang,LichSuTroChuyen,QuyenTruyCap
from models.LichSuTroChuyen import LichSuTroChuyen
from models.BoSuuTap import BoSuTap
from models.KhachHang import KhachHang
from datetime import datetime
from controllers import _user

def rag_jobs_list(agent, id_cv , k ,collection_id , ma_KH):
    with next(get_db()) as db:
        cv_details = _cv.get_cv(id_cv, db)
        
    agent_1_question = f"""Hãy tìm {k} công việc với các yêu cầu sau:
                - Ngành Nghề: {cv_details.get('Nganh', 'Không có')}
                - Kỹ năng mềm: {cv_details.get('KyNangMem', 'Không có')}
                - Kỹ năng chuyên ngành: {cv_details.get('KyNangChuyenNganh', 'Không có')}
                - Học vấn: {cv_details.get('hocVan', 'Không có')}
                - GPA: {cv_details.get('DiemGPA', 'Không có')}
                - Chứng chỉ: {cv_details.get('ChungChi', 'Không có')}"""
        
    answer = _chatbot_cv.chatbot_rag_crewai(agent_1_question,k,collection_id,ma_KH,id_cv)
    
    with next(get_db()) as db:
        bosutap_in_db = db.query(BoSuTap).filter(BoSuTap.ma_BST == collection_id).first()
        if not bosutap_in_db:
            BST = BoSuTap(
                ma_BST=collection_id,
                TenBST=f"tìm {k} công việc về Ngành Nghề: {cv_details.get('Nganh', 'Không có')}",
                ngayTao=datetime.now(),
                maKH=ma_KH
            )
            db.add(BST)  
            db.commit()  
        
        total_characters = len(agent_1_question) + len(answer)
        
        user_in_db = db.query(KhachHang).filter(KhachHang.maKH == ma_KH).first()
        
        if total_characters > user_in_db.soLuongToken:
            return 400
        
        update_mount = user_in_db.soLuongToken - total_characters
        
        _user.update_amount(maKH=ma_KH,new_money=update_mount,db=db)
        history_record = LichSuTroChuyen(
            cauHoi=agent_1_question,
            phanHoi=answer,
            tongSoToken=total_characters,
            maBST = collection_id
        )
        
        db.add(history_record)
        db.commit()
    
    
    return Task(
        description=dedent(f"""
            Sử dụng câu hỏi từ người dùng để tìm kiếm công việc phù hợp:
            {agent_1_question}
        """),
        agent=agent,
        expected_output=dedent(
        f"""
        1. Đưa ra các thông tin gồm tên công việc, chức danh, và link để ứng viên có thể truy cập và xem chi tiết.
        2. Đảm bảo rằng mỗi công việc đều phù hợp với ngành nghề, kỹ năng và yêu cầu của ứng viên.
        
        Kết quả từ chatbot: 
        {answer}
        """
    )
    )