from crewai import Crew
from textwrap import dedent
from .agents import agent_1_cv_analysis, agent_2_job_search
from .tasks import cv_analysis, rag_jobs_list
from dotenv import load_dotenv

load_dotenv()

def _crewai_jobscv(id_cv):
    # Tạo nhiệm vụ phân tích CV để lấy câu hỏi từ AGENT_1
    phan_tich_cau_hoi = cv_analysis(agent_1_cv_analysis(), id_cv)

    # Kiểm tra nếu phân tích CV thành công
    if not phan_tich_cau_hoi or not hasattr(phan_tich_cau_hoi, 'expected_output'):
        print("Phân tích CV không thành công hoặc thiếu expected_output")
        return

    # Lấy câu hỏi đầu ra từ AGENT_1
    agent_1_question = phan_tich_cau_hoi.expected_output.strip() if phan_tich_cau_hoi.expected_output else None
    
    
    print("====================================")
    print(agent_1_question)
    print("====================================")

    # Kiểm tra nếu câu hỏi từ AGENT_1 tồn tại
    if not agent_1_question:
        print("Không thể lấy câu hỏi từ AGENT_1")
        return

    # Tạo nhiệm vụ tìm kiếm công việc sử dụng câu hỏi từ AGENT_1
    tim_kiem_cong_viec = rag_jobs_list(agent_2_job_search(agent_1_question), agent_1_question)

    if tim_kiem_cong_viec is None:
        print("Tìm kiếm công việc không thành công")
        return

    # Khởi tạo đội ngũ với các task: phân tích CV và tìm kiếm công việc
    doan = Crew(
        tasks=[phan_tich_cau_hoi, tim_kiem_cong_viec],
        verbose=True,
    )

    # Thực thi công việc và dừng sau khi hoàn thành
    ket_qua = doan.kickoff()
    print("\n\n################################################")
    print("| Đây là kết quả phản hồi bình luận của bạn:\n")
    print(ket_qua)

    return ket_qua