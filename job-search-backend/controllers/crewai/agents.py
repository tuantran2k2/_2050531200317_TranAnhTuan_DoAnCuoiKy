from crewai import Agent, LLM
from textwrap import dedent
import os
from dotenv import load_dotenv

load_dotenv()

# Agent 1: Phân tích CV và tạo câu hỏi cho RAG
def agent_1_cv_analysis():
    return Agent(
        role="AGENT_1: Chuyên gia phân tích CV",
        backstory=dedent(
            """Tôi là một chuyên gia phân tích CV, có khả năng hiểu rõ các thông tin như kỹ năng, ngành, học vấn và kinh nghiệm.
            Tôi sử dụng những thông tin này để đưa ra một câu hỏi duy nhất nhằm xác định 5 công việc phù hợp nhất với CV của ứng viên."""
        ),
        goal=dedent(
            """Phân tích CV và các trường thông tin trong đó, xác định các yếu tố quan trọng như ngành, kỹ năng chuyên ngành, kỹ năng mềm, học vấn, GPA và chứng chỉ.
            Dựa trên các yếu tố này, đưa ra một câu hỏi duy nhất để tìm 5 công việc phù hợp nhất với ứng viên."""
        ),
        approach=dedent(
            """1. Phân tích thông tin từ CV:
                - Ngành Nghề
                - Kỹ năng mềm (Nếu có)
                - Kỹ năng chuyên ngành (Nếu có)
                - Học vấn
                - GPA (Nếu có)
                - Chứng chỉ (Nếu có)

            2. Tạo một câu hỏi duy nhất cho hệ thống RAG: Dựa trên các thông tin trên, tạo câu hỏi có chứa từ khóa "tìm 5 công việc" nhằm mục đích tìm được 5 công việc phù hợp nhất với ngành, kỹ năng và học vấn của ứng viên."""
        ),
        verbose=True,
        llm="gpt-4o",
        temperature=0.7,
    )


# Agent 2: Sử dụng RAG để tìm kiếm công việc phù hợp
def agent_2_job_search(agent_1_output):
    return Agent(
        role="AGENT_2: Chuyên gia tìm kiếm công việc",
        backstory=dedent(
            """Tôi là một chuyên gia tìm kiếm công việc, sử dụng đầu ra từ AGENT_1 để truy vấn dữ liệu và tìm ra các công việc phù hợp nhất cho ứng viên.
            Tôi sử dụng hệ thống RAG để đảm bảo rằng kết quả tìm kiếm có độ chính xác cao và đáp ứng yêu cầu của ứng viên."""
        ),
        goal=dedent(
            """Tìm kiếm và chọn ra 5 công việc phù hợp nhất dựa trên câu hỏi đã cung cấp từ AGENT_1.
            Đảm bảo mỗi công việc đều phù hợp với kỹ năng và yêu cầu của ứng viên."""
        ),
        approach=dedent(
            f"""1. Sử dụng câu hỏi từ AGENT_1: "{agent_1_output}" để thực hiện tìm kiếm trong hệ thống dữ liệu.
            2. Lựa chọn top 5 công việc có mức độ phù hợp cao nhất với các tiêu chí của ứng viên.
            3. Trả về kết quả: Cung cấp tên công việc, title và link để AGENT_3 tổng hợp và trình bày."""
        ),
        verbose=True,
        llm="gpt-4o",
        temperature=0,
    )