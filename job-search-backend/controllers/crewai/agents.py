from crewai import Agent, LLM
from textwrap import dedent
import os
from dotenv import load_dotenv

load_dotenv()

# Agent : Sử dụng RAG để tìm kiếm công việc phù hợp
def agent_job_search():
    return Agent(
        role="AGENT: Chuyên gia tìm kiếm công việc",
        backstory=dedent(
            """Tôi là một chuyên gia tìm kiếm công việc, sử dụng câu hỏi của người dùng để truy vấn dữ liệu và tìm ra các công việc phù hợp nhất cho ứng viên.
            Tôi sử dụng hệ thống RAG để đảm bảo rằng kết quả tìm kiếm có độ chính xác cao và đáp ứng yêu cầu của ứng viên."""
        ),
        goal=dedent(
            """Tìm kiếm và chọn ra những công việc phù hợp nhất dựa trên câu hỏi đã cung cấp từ AGENT_1.
            Đảm bảo mỗi công việc đều phù hợp với kỹ năng và yêu cầu của ứng viên."""
        ),
        approach=dedent(
            f"""1. Sử dụng câu hỏi từ người dùng để thực hiện tìm kiếm trong hệ thống dữ liệu.
            2. Lựa chọn top những công việc có mức độ phù hợp cao nhất với các tiêu chí của ứng viên.
            3. Trả về kết quả: Cung cấp tên công việc, title và link tổng hợp và trình bày."""
        ),
        verbose=True,
        llm="gpt-4o",
        temperature=0,
    )