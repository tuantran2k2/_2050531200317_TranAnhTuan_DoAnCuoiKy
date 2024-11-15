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



# Lấy danh sách các id 1 node
def get_ids_1_node(docs):
    list_ids = []

    for doc in docs:
        point_id = doc.metadata.get("_id") if hasattr(doc, "metadata") else None
        if point_id:
            list_ids.append(point_id)
        else:
            print("Không tìm thấy ID cho điểm này:", doc)
    return list_ids