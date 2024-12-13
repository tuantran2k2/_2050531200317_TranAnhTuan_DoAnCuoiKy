from pydantic import BaseModel

class GetCollection(BaseModel):
    user_id: int
    
class DeleteCollection(BaseModel):
    user_id: int
    collection_id: int 

class RenameCollection(BaseModel):
    user_id: int
    collection_id: int 
    new_name: str