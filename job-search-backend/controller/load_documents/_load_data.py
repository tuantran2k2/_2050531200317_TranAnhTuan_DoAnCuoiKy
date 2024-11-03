import pandas as pd
from langchain.schema import Document  

# Hàm xử lý file CSV
def process_csv_to_docs(file_path: str):
    # Đọc file CSV
    df = pd.read_csv(file_path)
    # Tạo danh sách các Document
    docs = []
    for row in df.iterrows():
        # Metadata
        metadata = {
            "id_job": row["id_job"],
            "job_title": row["job_title"],
            "link_post": row["link_post"],
            "location": row["location"],
            "date": row["date"]
        }

        # Tạo đối tượng Document với page_content là about_job
        doc = Document(metadata=metadata,page_content=row["about_job"])
        docs.append(doc)

    return docs 