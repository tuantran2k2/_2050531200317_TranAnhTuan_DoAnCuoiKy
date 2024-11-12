import os
from dotenv import load_dotenv
import threading
from collections import OrderedDict
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from controllers.rag import (
    _history,
    _node_structed,
    _clean_data,
    _summary,
    _re_write_query,
    _chain_invoke,
)
from controllers.vector_databases import _qdrant
from controllers.load_documents import (
    _pdf,
    _docx,
    _txt,
    _code,
    _csv,
    _doc,
    _html,
    _md,
    _xlsx,
)

from models import _environments, _prompts, _ultils, _constants
from queue import Queue
from controllers.ultils._log import log_function

load_dotenv()


class OrderedSet:
    def __init__(self, iterable):
        self.items = list(OrderedDict.fromkeys(iterable))

    def __repr__(self):
        return "{" + ", ".join(map(str, self.items)) + "}"


@log_function
def get_value_branch(db, point_ids, collection_name):
    points = _qdrant.get_point_from_ids(
        db=db, collection_name=collection_name, point_ids=point_ids
    )
    values = ""

    for point in points:
        context_content = point.payload["metadata"]["page_content"]
        context_filename = point.payload["metadata"]["file_name"]
        context_page_number = point.payload["metadata"]["page"]

        context = (
                str(context_content)
                + "\n\n# Thông tin trên thuộc trang: "
                + str(context_page_number)
                + " | của tài liệu: "
                + str(context_filename)
                + "."
        )

        values += context + "\n\n"

    return values


@log_function
def get_value_branch_img(db, point_ids, collection_name):
    points = _qdrant.get_point_from_ids(
        db=db, collection_name=collection_name, point_ids=point_ids
    )
    values = ""

    for point in points:
        context_content = point.payload["page_content"]

        values += context_content + "\n\n"

    return values


@log_function
def retriever_question(db, query, collection_name):
    docs = _qdrant.similarity_search_qdrant_data(db, query, 3)

    # for doc in docs:
    #     print("\n========================================================")
    #     print("### doc id:\n" + str(doc.metadata["doc_id"]))
    #     print("### doc:\n" + doc.metadata["page_content"])
    #     print("========================================================\n")

    # list_ids = _node_structed.get_ids_3_node(docs)
    list_ids = _node_structed.get_ids_1_node(docs)
    results = _node_structed.merge_lists(list_ids)

    retrievers = ""

    for result in results:
        retriever = get_value_branch(db, result, collection_name) + "\n"
        retrievers += retriever

        # nếu không phải là phần tử cuối cùng
        if result != results[-1]:
            retrievers += "\n\n"

    return retrievers


@log_function
def retriever_question_img(db, query, collection_name):
    docs = _qdrant.similarity_search_qdrant_data(db, query, 3)

    # for doc in docs:
    #     print("\n========================================================")
    #     print("### doc id:\n" + str(doc.metadata["doc_id"]))
    #     print("### doc:\n" + doc.metadata["page_content"])
    #     print("========================================================\n")

    list_ids = _node_structed.get_ids_3_node(docs)
    results = _node_structed.merge_lists(list_ids)

    retrievers = ""

    for result in results:
        retriever = get_value_branch_img(db, result, collection_name) + "\n"
        retrievers += retriever
        if result != results[-1]:
            retrievers += "\n\n"

    return retrievers


@log_function
def save_vector_db(file_path, user_id, language, chatbot_name, file_chunk_size, exactly=0):
    file_extension = file_path.split(".")[-1].lower()
    _path = _constants.DATAS_PATH
    path = _path + "/" + chatbot_name
    folder_path = f"{path}/{user_id}"
    loaders = {
        "js": _code.load_documents,
        "py": _code.load_documents,
        "java": _code.load_documents,
        "cpp": _code.load_documents,
        "cc": _code.load_documents,
        "cxx": _code.load_documents,
        "c": _code.load_documents,
        "cs": _code.load_documents,
        "php": _code.load_documents,
        "rb": _code.load_documents,
        "swift": _code.load_documents,
        "ts": _code.load_documents,
        "go": _code.load_documents,
        "csv": _csv.load_documents,
        "docx": _docx.load_documents,
        "doc": _doc.load_documents,
        "html": _html.load_documents,
        "md": _md.load_documents,
        "txt": _txt.load_documents,
        "text": _txt.load_documents,
        "log": _txt.load_documents,
        "xlsx": _xlsx.load_documents,
        "xls": _xlsx.load_documents,
    }
    count_list_collections_qdrant = _qdrant.count_list_collections_qdrant(
        user_id, chatbot_name
    )

    # Ham xu ly file pdf
    if file_extension in loaders:
        raw_elements = loaders[file_extension](file_path)
    elif file_extension == "pdf":
        raw_elements = _ultils.split_and_process_pdf(
            folder_path, language, user_id, count_list_collections_qdrant, chatbot_name, exactly, file_path
        )
    else:
        raise ValueError(f"Unsupported file type: .{file_extension}")

    threading.Thread(
        target=_ultils.add_totals_point_to_file,
        args=(
            len(raw_elements),
            path
            + "/"
            + user_id
            + "/total_points_"
            + str(count_list_collections_qdrant + 1)
            + ".txt",
        ),
    ).start()

    file_name = file_path.split("\\")[-1]
    file_name = file_name.split("/")[-1]

    datas, summaries, pages, file_names = _node_structed.get_element_data(raw_elements)
    if file_extension in ["xlsx", "xls", "csv"]:
        datas = raw_elements

    texts_optimized = _clean_data.clean_data_unstructured(datas)

    docs_text, doc_ids = _node_structed.add_text(
        texts_optimized, summaries, pages, file_names
    )

    collection_name = (
            user_id
            + "_"
            + _constants.NAME_CHATBOT
            + "_"
            + str(count_list_collections_qdrant + 1)
    )

    threading.Thread(
        target=_qdrant.save_list_collections_qdrant,
        args=(
            user_id,
            file_name,
            _constants.NAME_BOT_FACEBOOK,
            _constants.NAME_CHATBOT,
        ),
    ).start()

    threading.Thread(
        target=_ultils.add_totals_point_to_file,
        args=(
            len(raw_elements),
            _constants.DATAS_PATH
            + "/"
            + _constants.NAME_BOT_FACEBOOK
            + "/"
            + user_id
            + "/total_points_"
            + str(count_list_collections_qdrant + 1)
            + ".txt",
        ),
    ).start()

    _qdrant.save_vector_db_as_ids(docs_text, collection_name, doc_ids)
    return collection_name


@log_function
def load_vector_db(collection_name):
    db = _qdrant.load_vector_db(collection_name)
    return db


@log_function
def save_history(answer, user_id, query, collection_id, chatbot_name, base64_images, chart_answer=""):
    _history.save_history(
        user_id, query, answer, collection_id, chatbot_name, base64_images
    )
    _history.save_history_public(
        user_id, query, answer, collection_id, chatbot_name, base64_images, chart_answer
    )


@log_function
def save_history_mekongAI(answer, user_id, query, collection_id, base64_images):
    _history.save_history(
        user_id, query, answer, collection_id, "MEKONGAI", base64_images
    )
    _history.save_history_public(
        user_id, query, answer, collection_id, "MEKONGAI", base64_images
    )


##########################################################################################################
# Trích xuất các keyword từ answer => Return về string
@log_function
def answer_images_keyword(answer, query):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                _prompts.KEYWORD_DETECTION.format(
                    context=str(answer), example=_prompts.keyword_ex, query=str(query)
                ),
            ),
            ("human", str(answer)),
        ]
    )

    chain = (
            prompt | _environments.get_llm("gpt-4o-mini", temperature=0) | StrOutputParser()
    )
    answer_keyword = chain.invoke({"input": str(answer)})
    return answer_keyword


# Hàm trả về ảnh
@log_function
def return_images(result_array, db):
    list_base64 = []
    unique_images = set()

    for res in result_array:
        retrievers = db.similarity_search_with_relevance_scores(str(res), 1)
        content, score = retrievers[0]
        if float(score) > 0.8:
            image_base64 = content.metadata["images_base_64"]
            if image_base64 not in unique_images:
                unique_images.add(image_base64)
                list_base64.append(image_base64)

    # print(list_base64)
    return list_base64


############################################################################################################
# Kiểm tra loại bot
@log_function
def check_bot_type(query):
    detect_query_type = _chain_invoke.query_detection(query=query)
    normalize_string = _ultils.normalize_string(detect_query_type)

    return normalize_string

############################################################################################################
# API
# def chatbot(
#     query, list_collections, user_id, history, collection_id, chatbot_name, temperature
# ):
#     # bot_type = check_bot_type(query)
#     # print("========================================================")
#     # print("bot_type:", bot_type)
#     # print("========================================================\n")
#     #
#     # base64_images = []
#     #
#     # if bot_type == "QUOTE_DOC":
#     #     answer, base64_images = _chatbot_quote.chatbot_quote(
#     #         query,
#     #         list_collections,
#     #         user_id,
#     #         history,
#     #         collection_id,
#     #         chatbot_name,
#     #         temperature,
#     #     )
#     # elif bot_type == "FULL_DOC":
#     #     answer, base64_images = _chatbot_full_docs.chatbot_full_docs(
#     #         query,
#     #         list_collections,
#     #         user_id,
#     #         history,
#     #         collection_id,
#     #         chatbot_name,
#     #         temperature,
#     #     )
#     # else:
#     #     answer, base64_images = _chatbot_basic.chatbot_basic(
#     #         query, user_id, history, collection_id, chatbot_name, temperature
#     #     )
#
#     return answer, base64_images
