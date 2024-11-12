from crewai import Task
from textwrap import dedent

from models import _prompts
from controllers.rag import _clean_data


def post_analysis(agent, post_content, images):
    image_details = ""
    if images:
        for image in images:
            img_link = image.get("img_link", "")
            img_summary = image.get("summary", "")
            image_details += f"\n+ Link ảnh: {img_link}\n+ Mô tả ảnh: {img_summary}\n\n"

    return Task(
        description=dedent(_prompts.POST_SUMMARY.format(post_content=post_content, post_images=image_details)),
        agent=agent,
        expected_output=dedent(
            f"""Quan điểm cá nhân về bài viết này. Tập trung vào ngữ cảnh và ý định của tác giả, phong cách, cảm xúc, và dự đoán về khả năng tương tác.""")
    )


def comment_analysis(agent, comments, task_post_analysis):
    comments = _clean_data.validate_and_fix_braces(comments)

    return Task(
        description=dedent(_prompts.POST_COMMENT_SUMMARY.format(comments=comments)),
        agent=agent,
        expected_output=dedent(f"""\
1. Đưa ra phân tích tổng quát nhất về các bình luận đó.
2. Đưa ra đánh giá về mức độ tương tác và ảnh hưởng của các bình luận dựa trên ngữ cảnh của bài post.
3. Cung cấp thông tin về cách bình luận liên kết với nội dung bài viết và góp phần vào cuộc thảo luận chung.
4. Tóm tắt tất cả các thông tin có trong các comments. Theo thứ tự."""),
        context=[task_post_analysis]
    )


def generate_comment_replies(agent, comment, task_post_analysis, task_comment_analysis):
    return Task(
        description=dedent(_prompts.POST_GENERATE_COMMENT.format(comment=comment)),
        agent=agent,
        expected_output=dedent(
            f"""Câu trả lời cho bình luận: {comment}. Cần liên kết với những comment trước đó và nội dung bài viết (nếu có)."""),
        context=[task_post_analysis, task_comment_analysis]
    )
