from pydantic import BaseModel

class SimpleCount(BaseModel):
    count: int
class ApprovalPoint(BaseModel):
    week : str
    registered: int
    approved: int