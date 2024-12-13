from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from dependencies.dependencies import get_db
from schemas._bst import GetCollection , DeleteCollection ,RenameCollection
from controllers import _bst

import json  
import io

router = APIRouter(
    prefix="/api/v1/bst",
    tags=["bst"],
)

################################ upload file CV ########################################################


@router.post("/get_list_bst")
async def list_cv(request: GetCollection,db: Session = Depends(get_db)):
    try:
        response = _bst.get_list_bst(request.user_id,db)
        return response 
    except Exception as e:
        # Xử lý lỗi nếu có
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while fetching CV list: {str(e)}"
        )
        
@router.delete("/delete_collection")
async def delete_collection(request: DeleteCollection, db: Session = Depends(get_db)):
    try:
        # Xóa bộ sưu tập theo mã khách hàng và ID bộ sưu tập
        response = _bst.delete_collection_by_id(request.user_id, request.collection_id, db)
        if not response["success"]:
            raise HTTPException(status_code=404, detail=response["message"])
        return {"success": 200, "message": response["message"]}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while deleting collection: {str(e)}"
        )

@router.post("/rename_collection")
async def rename_collection(request: RenameCollection, db: Session = Depends(get_db)):
    try:
        # Đổi tên bộ sưu tập theo mã khách hàng và ID bộ sưu tập
        response = _bst.rename_collection(request.user_id, request.collection_id, request.new_name, db)
        if not response["success"]:
            raise HTTPException(status_code=404, detail=response["message"])
        return {"success": True, "message": response["message"]}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while renaming collection: {str(e)}"
        )