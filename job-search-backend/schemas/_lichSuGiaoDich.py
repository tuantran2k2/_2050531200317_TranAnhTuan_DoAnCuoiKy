from pydantic import BaseModel

class DepositRequest(BaseModel):
    maKH: int
    amount : int