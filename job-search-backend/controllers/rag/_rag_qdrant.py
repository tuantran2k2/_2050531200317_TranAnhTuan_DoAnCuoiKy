import os
from dotenv import load_dotenv
from database import _qdrant
from controllers.rag import (
    _node_structed
)



def get_value_branch(db, point_ids, collection_name):
    
    points = _qdrant.get_point_from_ids(
        db=db, collection_name=collection_name, point_ids=point_ids
    )

    
    # Kiểm tra xem dữ liệu trả về từ get_point_from_ids là gì
    print("Dữ liệu trả về từ get_point_from_ids:", points)
    
    values = ""

    for point in points:
        print(point)
        context_content = point.payload["page_content"]
        context_title = point.payload["metadata"]["job_title"]
        context_location = point.payload["metadata"]["location"]
        context_link = point.payload["metadata"]["link_post"]
        context_date = point.payload["metadata"]["date"]
        context_id_job = point.payload["metadata"]["id_job"]

        context = (
            f"---\n"
            f"Nội dung:\n{context_content}\n\n"
            f"Tiêu đề Công Việc: {context_title}\n"
            f"Địa chỉ việc làm: {context_location}\n"
            f"Link chi tiết: {context_link}\n"
            f"Ngày đăng: {context_date}\n"
            f"id_job: {context_id_job}\n"
            f"---\n\n"
        )
        values += context + "\n\n"
    return values


def retriever_question(db, query, collection_name , k):
    docs = _qdrant.similarity_search_qdrant_data(db, query, k)
    list_id = _node_structed.get_ids_1_node(docs)
    retriever = get_value_branch(db, list_id, collection_name) + "\n"
    return retriever