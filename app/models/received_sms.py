# app/models/received_sms.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class ReceivedSMS(Base):
    __tablename__ = "received_sms"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    amount = Column(Integer, nullable=True)  # Amount chosen based on response
    matched_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
