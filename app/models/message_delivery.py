from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base

class MessageDelivery(Base):
    __tablename__ = "message_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    phone_number = Column(String(255), nullable=False)
    status = Column(String(255))
    api_response = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)