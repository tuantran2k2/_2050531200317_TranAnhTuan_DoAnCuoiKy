# qdrant_client.py
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Lấy các biến môi trường từ file .env
QDRANT_SERVER = os.getenv("QDRANT_SERVER")

embeddings_model = OpenAIEmbeddings()

# Khởi tạo kết nối tới QdrantClient
qdrant_client = QdrantClient(
    url=QDRANT_SERVER
)

def save_vector_db(docs, collection_name, point_ids):
    qdrant_doc = Qdrant.from_documents(
        documents=docs,
        embedding=embeddings_model,
        url=QDRANT_SERVER,
        prefer_grpc=False,
        collection_name=collection_name,
        ids=point_ids,
    )
    return qdrant_doc

def load_vector_db(collection_names):
    try:
        client = Qdrant.from_existing_collection(
            embedding=embeddings_model,
            collection_name=collection_names,
            url=QDRANT_SERVER,
        )
        return client
    except Exception:
        a = "None"
        return a

# Hàm mới: Xóa các điểm có "date" quá 7 ngày
def delete_old_points(collection_name):
    try:
        # Tính ngày giới hạn là 7 ngày trước
        cutoff_date = datetime.now() - timedelta(days=7)
        points_to_delete = []
        
        # Duyệt qua tất cả các điểm trong collection
        scroll_result, next_page = qdrant_client.scroll(
            collection_name=collection_name,
            limit=100  # Giới hạn số điểm tải mỗi lần
        )
        
        while scroll_result:
            for point in scroll_result:
                point_date_str = point.payload.get("date")
                if point_date_str:
                    # Chuyển đổi chuỗi ngày thành datetime object
                    point_date = datetime.strptime(point_date_str, "%Y-%m-%d %H:%M:%S.%f")
                    
                    # Kiểm tra xem ngày của điểm có quá 7 ngày không
                    if point_date < cutoff_date:
                        points_to_delete.append(point.id)
            
            # Kiểm tra xem có trang tiếp theo không
            if not next_page:
                break
            
            # Tiếp tục scroll để lấy các điểm tiếp theo
            scroll_result, next_page = qdrant_client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=next_page  # Tiếp tục từ trang tiếp theo
            )
        
        # Xóa các điểm có "date" quá 7 ngày
        if points_to_delete:
            qdrant_client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=points_to_delete)
            )
            print(f"Đã xóa {len(points_to_delete)} điểm có 'date' quá 7 ngày.")
        else:
            print("Không có điểm nào cần xóa.")
        update_point_sequence(collection_name)
        total_points = count_points(collection_name)
        return total_points
    except Exception as e:
        print("Lỗi khi xóa các điểm:", e)

def count_points(collection_name):
    try:
        total_points = 0
        scroll_result, next_page = qdrant_client.scroll(
            collection_name=collection_name,
            limit=100  # Limit the number of points loaded each time
        )
        
        # Scroll through all points to count them
        while scroll_result:
            total_points += len(scroll_result)
            
            # Check if there's a next page
            if not next_page:
                break
            
            # Continue scrolling to get the next points
            scroll_result, next_page = qdrant_client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=next_page  # Continue from the next page
            )
        
        print(f"Total number of points in '{collection_name}': {total_points}")
        return total_points
        
    except Exception as e:
        print("Error counting points:", e)
        return 0
    
    
def update_point_sequence(collection_name):
    try:
        sequence_number = 1
        scroll_result, next_page = qdrant_client.scroll(
            collection_name=collection_name,
            limit=100  # Limit the number of points loaded each time
        )
        
        # Scroll through all points to update their sequence number
        while scroll_result:
            points_to_update = []
            for point in scroll_result:
                # Check if the vector is available
                vector = getattr(point, 'vector', None)
                if vector is None:
                    print(f"Skipping point {point.id} due to missing vector.")
                    continue
                
                # Prepare each point with the updated sequence number and existing vector
                points_to_update.append({
                    "id": point.id,
                    "vector": vector,
                    "payload": {
                        **point.payload,  # Keep existing payload data
                        "sequence_number": sequence_number
                    }
                })
                sequence_number += 1
            
            # Use upsert to update points in bulk
            if points_to_update:
                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=points_to_update
                )
            
            # Check if there's a next page
            if not next_page:
                break
            
            # Continue scrolling to get the next points
            scroll_result, next_page = qdrant_client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=next_page  # Continue from the next page
            )
        
        print("Updated sequence numbers for all points.")
        
    except Exception as e:
        print("Error updating sequence numbers:", e)

