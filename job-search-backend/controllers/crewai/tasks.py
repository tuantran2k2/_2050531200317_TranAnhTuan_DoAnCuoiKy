from crewai import Task
from textwrap import dedent
from controllers.rag import _clean_data
from controllers import _cv 
from controllers.rag.chatbot import _chatbot_cv
from dependencies.dependencies import get_db
from models import BoSuuTap,KhachHang,LichSuTroChuyen,PhuongXa,QuanHuyen,QuyenTruyCap, ThonTo,TinhThanh,ViToken

def cv_analysis(agent, id_cv):
    with next(get_db()) as db:
        cv_details = _cv.get_cv(id_cv, db)

    return Task(
        description=dedent(f"""
            Phân tích chi tiết CV với các thông tin sau:
            {cv_details}
        """),
        agent=agent,
        expected_output=dedent(
            """Tạo ra một câu hỏi duy nhất với nội dung "tìm 5 công việc" nhằm mục đích tìm ra 5 công việc phù hợp nhất với thông tin từ CV."""
        )
    )
    
def rag_jobs_list(agent, agent_1_question):
    _chatbot_cv.chatbot_rag_crewai(agent_1_question)

    return Task(
        description=dedent(f"""
            Sử dụng câu hỏi từ AGENT_1 để tìm kiếm công việc phù hợp:
            {agent_1_question}
        """),
        agent=agent,
        expected_output=dedent(
            """1. Chọn ra 5 công việc phù hợp nhất dựa trên câu hỏi từ AGENT_1.
            2. Đưa ra các thông tin gồm tên công việc, chức danh, và link để ứng viên có thể truy cập và xem chi tiết.
            3. Đảm bảo rằng mỗi công việc đều phù hợp với ngành nghề, kỹ năng và yêu cầu của ứng viên."""
        )
    )