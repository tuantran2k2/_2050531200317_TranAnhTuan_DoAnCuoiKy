from sqlalchemy.orm import Session
from models.BoSuuTap import BoSuTap
import logging


def get_list_bst(maKH: int, db: Session):
    try:
        # Truy vấn bộ sưu tập theo mã khách hàng (maKH)
        collections = db.query(BoSuTap).filter(BoSuTap.maKH == maKH).all()

        # Kiểm tra nếu không có bộ sưu tập nào
        if not collections:
            logging.warning(f"No collections found for customer ID {maKH}.")
            return []

        # Tạo một danh sách các bộ sưu tập để trả về
        collection_list = []
        for collection in collections:
            collection_data = {
                "id": collection.ma_BST,
                "ten_bo_suu_tap": collection.TenBST,
                "ngay_tao": collection.ngayTao,
                "ma_cv" : collection.maCV
            }
            collection_list.append(collection_data)

        return collection_list

    except Exception as e:
        logging.error(f"Database error occurred: {e}")
        return []

def delete_collection_by_id(maKH: int, collection_id: int, db: Session):
    try:
        # Truy vấn bộ sưu tập theo mã khách hàng và ID bộ sưu tập
        collection = db.query(BoSuTap).filter(BoSuTap.maKH == maKH, BoSuTap.ma_BST == collection_id).first()

        # Kiểm tra xem bộ sưu tập có tồn tại không
        if collection is None:
            logging.warning(f"Collection with ID {collection_id} for customer ID {maKH} not found.")
            return {"success": False, "message": "Collection not found."}

        # Xóa bộ sưu tập
        db.delete(collection)
        db.commit()

        logging.info(f"Collection with ID {collection_id} deleted successfully for customer ID {maKH}.")
        return {"success": True, "message": "Collection deleted successfully."}

    except Exception as e:
        db.rollback()  # Rollback nếu có lỗi xảy ra
        logging.error(f"Database error occurred: {e}")
        return {"success": False, "message": "Database error."}
    
    
def rename_collection(maKH: int, collection_id: int, new_name: str, db: Session):
    try:
        # Truy vấn bộ sưu tập theo mã khách hàng và ID bộ sưu tập
        collection = db.query(BoSuTap).filter(BoSuTap.maKH == maKH, BoSuTap.ma_BST == collection_id).first()

        # Kiểm tra xem bộ sưu tập có tồn tại không
        if collection is None:
            logging.warning(f"Collection with ID {collection_id} for customer ID {maKH} not found.")
            return {"success": False, "message": "Collection not found."}

        # Cập nhật tên bộ sưu tập
        collection.TenBST = new_name
        db.commit()

        logging.info(f"Collection with ID {collection_id} renamed successfully to '{new_name}' for customer ID {maKH}.")
        return {"success": True, "message": f"Collection renamed to '{new_name}' successfully."}

    except Exception as e:
        db.rollback()  # Rollback nếu có lỗi xảy ra
        logging.error(f"Database error occurred: {e}")
        return {"success": False, "message": "Database error."}
