import re
from langchain_core.prompts import ChatPromptTemplate

from controllers.rag import _history, _chain_invoke
from models import _prompts


def re_write_query(query, history):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _prompts.RE_WRITE_QUERY.format(history=str(history), query=str(query)),
            ),
        ]
    )

    ans = _chain_invoke.rewrite_query(query, prompt)
    answer = (
            "CÂU TRUY VẤN GỐC: "
            + query
            + "\nCÂU TRUY VẤN ĐƯỢC LÀM RÕ (tham khảo): "
            + ans
    )

    return answer


def extract_questions(text):
    # Sử dụng biểu thức chính quy để tìm nội dung của từng câu hỏi
    original_question = re.search(
        r"CÂU TRUY VẤN GỐC:\s*(.*?)\s*CÂU TRUY VẤN ĐƯỢC LÀM RÕ \(tham khảo\):",
        text,
        re.DOTALL | re.MULTILINE,
    )
    clarified_question = re.search(
        r"CÂU TRUY VẤN ĐƯỢC LÀM RÕ \(tham khảo\):\s*(.*)",
        text,
        re.DOTALL | re.MULTILINE,
    )

    original_question_content = (
        original_question.group(1).strip() if original_question else text
    )
    clarified_question_content = (
        clarified_question.group(1).strip() if clarified_question else text
    )

    return original_question_content, clarified_question_content

# original, clarified = extract_questions(text)


# query = "html là gì"
# user_id = 2
# answer = re_write_query(user_id, query)
# print(answer)
