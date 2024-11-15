from crewai import Crew
from .agents import agent_job_search
from .tasks import  rag_jobs_list
from dotenv import load_dotenv

load_dotenv()

def _crewai_jobscv(id_cv,k,collection_id,ma_KH):

    # Tạo nhiệm vụ tìm kiếm công việc sử dụng câu hỏi từ AGENT_1
    tim_kiem_cong_viec = rag_jobs_list(agent_job_search(), id_cv,k,collection_id,ma_KH)

    if tim_kiem_cong_viec is None:
        print("Tìm kiếm công việc không thành công")
        return

    # Khởi tạo đội ngũ với các task: phân tích CV và tìm kiếm công việc
    doan = Crew(
        tasks=[tim_kiem_cong_viec],
        verbose=True,
    )

    # Thực thi công việc và dừng sau khi hoàn thành
    ket_qua = doan.kickoff()
    print("\n\n################################################")
    print("| Đây là kết quả phản hồi bình luận của bạn:\n")
    print(ket_qua)

    return ket_qua
