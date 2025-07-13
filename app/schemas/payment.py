# app/schemas/payment.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    TransactionType: str
    TransID: str
    TransTime: str
    TransAmount: float
    BusinessShortCode: str
    BillRefNumber: Optional[str]
    InvoiceNumber: Optional[str]
    OrgAccountBalance: Optional[str]
    ThirdPartyTransID: Optional[str]
    MSISDN: str
    FirstName: str
    MiddleName: Optional[str]
    LastName: Optional[str]

class PaymentOut(BaseModel):
    id: int
    trans_id: str
    trans_amount: float
    msisdn: str
    received_at: datetime

    class Config:
        orm_mode = True
