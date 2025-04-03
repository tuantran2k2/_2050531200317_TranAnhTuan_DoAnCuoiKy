from fastapi import APIRouter, Depends, HTTPException ,Request
from sqlalchemy.orm import Session
from schemas._chatbot import QuestionRequest ,QuestionRequestChat
from dependencies.security import verified_user
from controllers import _chatbot
from dependencies.dependencies import get_db

from models.LichSuTroChuyen import LichSuTroChuyen 
from models.BoSuuTap import  BoSuTap
from controllers import _chatbot


router = APIRouter(
    prefix="/api/v1/chatbot",
    tags=["chatbot"],
)

#######Câu hỏi mặc định , tìm k công việc phù hợp#############
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=500, detail="Authorization header missing")
    
    # Xác thực người dùng
    payload = verified_user(auth_header)
    if not payload:
        raise HTTPException(status_code=500, detail="Invalid token or unauthorized")
    
    return payload


# Bước 1: tìm list CV 
@router.post("/find_jobs")
@router.post("/find_jobs/")
def request_otp(request: QuestionRequest):
    try:
        answer = _chatbot.find_job(id_cv=request.id_cv,k=request.so_luong_job,collection_id=request.collection_id,ma_KH=request.user_id)
        print("answer",answer)
        if answer == 400 :
            return { 
                    "status" : 403 , 
                    "messages": "Số dư của bạn không đủ"
            }
            
        if answer:
            return { 
                    "status" : 200 , 
                    "messages": answer
            }
            
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}
        
#Bước 2 : chatbot       
@router.post("/chat_bot_cv")
def request_otp(request: QuestionRequestChat):
    try:
        answer = _chatbot.chatbot(id_cv=request.id_cv,collection_id=request.collection_id,ma_KH=request.user_id, query=request.query)

        if answer == 400 :
            return { 
                    "status" : 403 , 
                    "messages": "Số dư của bạn không đủ"
            }
        if answer:
            return { 
                    "status" : 200 , 
                    "messages": answer
            }
            
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}


@router.get("/chat-history")
def get_chat_history(msKH: int, maBST: int, db: Session = Depends(get_db)):
    try:
        # Lấy danh sách BST dựa trên msKH và maBST
        bst_records = db.query(BoSuTap).filter(BoSuTap.maKH == msKH, BoSuTap.ma_BST == maBST).all()

        if not bst_records:
            return {"status": 404, "message": "Không tìm thấy bản ghi BST phù hợp."}

        # Lấy lịch sử trò chuyện dựa trên maBST
        chat_history = db.query(LichSuTroChuyen).filter(LichSuTroChuyen.maBST == maBST).all()

        if not chat_history:
            return {"status": 404, "message": "Không tìm thấy lịch sử trò chuyện cho maBST này."}

        # Xây dựng dữ liệu trả về
        data = {
            "chat_history": [
                {
                    "ma_LSTC": chat.ma_LSTC,
                    "cauHoi": chat.cauHoi,
                    "phanHoi": chat.phanHoi,
                    "tongSoToken": chat.tongSoToken,
                    "timestamp": chat.timestamp,
                }
                for chat in chat_history
            ],
        }

        return {"status": 200, "data": data}

    except Exception as e:
        return {"status": 500, "message": f"Lỗi: {e}"}