from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Add this new schema for options
class MessageOptionPayload(BaseModel):
    choice: str
    amount: int

# Update this to include options in send payload
class MessageSend(BaseModel):
    customer_id: int
    content: str
    options: List[MessageOptionPayload]

class MessageIn(BaseModel):
    phone_number: str
    content: str

class MessageOut(BaseModel):
    id: int
    direction: str
    phone_number: str
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True
