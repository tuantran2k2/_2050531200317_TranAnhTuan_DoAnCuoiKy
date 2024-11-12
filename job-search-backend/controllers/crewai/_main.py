from crewai import Crew
from textwrap import dedent
from crewai_comment.agents import agent_1_post_analysis, agent_2_comment_analysis, agent_3_generate_reply
from crewai_comment.tasks import post_analysis, comment_analysis, generate_comment_replies
from dotenv import load_dotenv


def _crewai_comment(noi_dung_post, images, cum_comments, comment):
    # Tạo nhiệm vụ phân tích bài post
    phan_tich_bai_post = post_analysis(agent_1_post_analysis(), noi_dung_post, images)

    # Kiểm tra nếu phân tích bài post thành công
    if phan_tich_bai_post is None:
        print("Phân tích bài post không thành công")
        return

    # Chỉ phân tích bình luận nếu bài post đã được phân tích
    phan_tich_binh_luan = comment_analysis(agent_2_comment_analysis(), cum_comments, phan_tich_bai_post)

    if phan_tich_binh_luan is None:
        print("Phân tích bình luận không thành công")
        return

    du_doan_binh_luan = generate_comment_replies(agent_3_generate_reply(), comment, phan_tich_bai_post,
                                                 phan_tich_binh_luan)
    if du_doan_binh_luan is None:
        print("Học hỏi bình luận không thành công")
        return

    # Khởi tạo đội ngũ với các agent
    doan = Crew(
        # agents=[agent_1_post_analysis(), agent_2_comment_analysis(), agent_3_generate_reply()],
        tasks=[phan_tich_bai_post, phan_tich_binh_luan, du_doan_binh_luan],
        verbose=True,
    )

    # Thực thi công việc và dừng sau khi hoàn thành
    ket_qua = doan.kickoff()
    print("\n\n################################################")
    print("| Đây là kết quả phản hồi bình luận của bạn:\n")
    print(ket_qua)

    return ket_qua
