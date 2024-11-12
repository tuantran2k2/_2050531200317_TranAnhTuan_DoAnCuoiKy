import uuid
from dotenv import load_dotenv
from typing import List
from collections import OrderedDict
from typing import List
import concurrent.futures
import re

from langchain_core.documents import Document

from controllers.rag import _summary

load_dotenv()


# simple node
def simple_node(
        doc_contents: List[str], pages: List[int]
) -> tuple[list[Document], list[str]]:
    doc_ids = [i + 1 for i in range(len(doc_contents))]
    docs = []
    for i, s in enumerate(doc_contents):
        metadata = {"type": "text", "doc_id": doc_ids[i], "page": str(pages[i])}
        docs.append(Document(page_content=s, metadata=metadata))

    return docs, doc_ids


# add text 1 node
def add_text(
        doc_contents: List[str],
        summaries: List[str],
        pages: List[int],
        file_names: List[str],
) -> tuple[list[Document], list[str]]:
    doc_ids = [i + 1 for i in range(len(doc_contents))]
    docs = []
    for i, s in enumerate(doc_contents):
        name = file_names[i]
        split_string = name.split("-page")
        _file_name_ = split_string[0]

        metadata = {
            "type": "text",
            "page_content": s,
            "doc_id": doc_ids[i],
            "page": pages[i],
            "file_name": _file_name_,
        }
        docs.append(Document(page_content=summaries[i], metadata=metadata))
    return docs, doc_ids


# add images
def add_images(
        doc_contents: List[str],
        summaries: List[str],
        images_name: List[str],
        img_page: List[str],
) -> tuple[list[Document], list[str]]:
    doc_ids = [i + 1 for i in range(len(doc_contents))]
    docs = []

    for i, s in enumerate(doc_contents):
        metadata = {
            "type": "images",
            "images_base_64": s,
            "doc_id": doc_ids[i],
            "images_name": images_name[i],
            "page": img_page[i],
        }
        docs.append(Document(page_content=summaries[i], metadata=metadata))
    return docs, doc_ids


# Lấy danh sách các id 1 node
def get_ids_1_node(docs):
    list_ids = []

    for doc in docs:
        id = doc.metadata["doc_id"]
        ids = [id - 1, id, id + 1]
        ids = [elem for elem in ids if elem != "None"]
        list_ids.append(ids)

    return list_ids


# Lấy danh sách các id 3 node
def get_ids_3_node(docs):
    list_ids = []

    for doc in docs:
        id = doc.metadata["doc_id"]
        ids = [
            id - 3,
            id - 2,
            id - 1,
            id,
            id + 1,
            id + 2,
            id + 3,
        ]
        ids = [elem for elem in ids if elem > 0]
        list_ids.append(ids)

    return list_ids


def check_common_elements(l1, l2):
    return any(elem in l1 for elem in l2)


# Bước 2: Hợp nhất các danh sách có phần tử trùng nhau và sắp xếp tăng dần
def merge_lists(lists):
    merged = []
    visited = [False] * len(lists)

    for i in range(len(lists)):
        if visited[i]:
            continue
        current_merge = lists[i]
        visited[i] = True
        for j in range(i + 1, len(lists)):
            if check_common_elements(current_merge, lists[j]):
                current_merge += [
                    elem for elem in lists[j] if elem not in current_merge
                ]
                visited[j] = True
        merged.append(sorted(current_merge))  # Sắp xếp danh sách hiện tại

    return merged


class OrderedSet:
    def __init__(self, iterable):
        self.items = list(OrderedDict.fromkeys(iterable))

    def __repr__(self):
        return "{" + ", ".join(map(str, self.items)) + "}"


def get_element_data_simple(raw_data_elements):
    datas = []
    pages = []

    for element in raw_data_elements:
        if "unstructured.documents.elements.CompositeElement" in str(type(element)):
            datas.append(str(element))
            page = sorted(
                {e.metadata.page_number for e in element.metadata.orig_elements}
            )
            ordered_set_numbers = OrderedSet(page)
            pages.append(ordered_set_numbers)

    return datas, pages


def split_array(array: List) -> List[List]:
    """Chia mảng thành nhiều phần bằng nhau dựa trên độ dài của mảng.

    Args:
        array (List): Mảng cần chia.

    Returns:
        List[List]: Mảng chứa các phần đã chia.
    """
    length = len(array)
    if length <= 20:
        num_parts = 1
    else:
        num_parts = (length // 10) - 1

    if num_parts == 1:
        return [array]

    avg = length / float(num_parts)
    out = []
    last = 0.0

    while last < length:
        out.append(array[int(last): int(last + avg)])
        last += avg

    return out


def get_element_data(raw_data_elements):
    datas = [None] * len(raw_data_elements)
    summaries = [None] * len(raw_data_elements)
    pages = [None] * len(raw_data_elements)
    file_names = [None] * len(raw_data_elements)

    def process_element(index, element):
        if "unstructured.documents.elements.Table" in str(type(element)):
            file_name = element.metadata.filename
            table_text = str(element.text)
            table_html = str(element.metadata.text_as_html)
            page = sorted(
                {e.metadata.page_number for e in element.metadata.orig_elements}
            )
            ordered_set_numbers = OrderedSet(page)

            table_summary = _summary.summary_table(table_text)
            table_sum_up = f"# Nội dung của bảng: {table_text}\n\n# Nội dung của bảng dưới dạng HTML: {table_html}"
            return (
                index,
                table_sum_up,
                table_summary,
                str(ordered_set_numbers),
                file_name,
            )

        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            file_name = element.metadata.filename
            page = sorted(
                {e.metadata.page_number for e in element.metadata.orig_elements}
            )
            ordered_set_numbers = OrderedSet(page)

            data_page = f"{str(element)}"
            return index, data_page, str(element), str(ordered_set_numbers), file_name

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_element, idx, element)
            for idx, element in enumerate(raw_data_elements)
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                index, data, summary, page, file_name = result
                datas[index] = data
                summaries[index] = summary
                pages[index] = page
                file_names[index] = file_name

    return datas, summaries, pages, file_names
