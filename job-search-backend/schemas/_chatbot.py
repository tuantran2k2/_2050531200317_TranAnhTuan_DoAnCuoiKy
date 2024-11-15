from pydantic import BaseModel

class QuestionRequest(BaseModel):
    user_id: int
    so_luong_job: int
    collection_id: int 
    id_cv: int
    
    
class QuestionRequestChat(BaseModel):
    user_id: int
    collection_id: int 
    id_cv: int
    query: str
    
