from dotenv import load_dotenv
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