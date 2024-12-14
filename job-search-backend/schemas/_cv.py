from pydantic import BaseModel

class MaKHRequest(BaseModel):
    makh: int

class DeleteRequest(BaseModel):
    makh: int
    maCV :int
    
class UpdateStatus(BaseModel):
    trangThai: int
    maCV :int