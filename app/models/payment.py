# app/models/payment.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(255))
    trans_id = Column(String(255), unique=True, index=True)
    trans_time = Column(String(255))
    trans_amount = Column(Float)
    business_short_code = Column(String(255))
    bill_ref_number = Column(String(255))
    invoice_number = Column(String(255), nullable=True)
    org_account_balance = Column(String(255), nullable=True)
    msisdn = Column(String(255))
    first_name = Column(String(255))
    middle_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    received_at = Column(DateTime, server_default=func.now())
