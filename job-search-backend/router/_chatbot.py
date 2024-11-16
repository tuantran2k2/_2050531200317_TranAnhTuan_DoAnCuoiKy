from fastapi import APIRouter , HTTPException,Request
from schemas._chatbot import QuestionRequest ,QuestionRequestChat
from dependencies.security import verified_user
from controllers.crewai import _main
from controllers import _chatbot
from dependencies.dependencies import get_db


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
def request_otp(request: QuestionRequest):
    try:
        answer = _main._crewai_jobscv(id_cv=request.id_cv,k=request.so_luong_job,collection_id=request.collection_id,ma_KH=request.user_id)

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

        if answer:
            return { 
                    "status" : 200 , 
                    "messages": answer
            }
            
    except Exception as e:
            return {"status" : 500 , "message": f"lỗi {e}"}