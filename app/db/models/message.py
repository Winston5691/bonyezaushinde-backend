from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base                              # your shared Base

# FILE: app/db/models/message.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
class MessageDB(Base):
    __tablename__ = "messages"

    id           = Column(Integer, primary_key=True)
    customer_id  = Column(String(255))
    phone_number = Column(String(255))
    content      = Column(String(255))
    direction    = Column(String(255))  # incoming / outgoing_question / outgoing_system_response
    status       = Column(String(255))
    message_id   = Column(String(255))
    timestamp    = Column(DateTime, default=datetime.utcnow)

    round_id     = Column(Integer, ForeignKey("rounds.id"), nullable=True)

    # ✅ Define relationship to Round
    round        = relationship("RoundDB", back_populates="messages")

    options      = relationship("MessageOptionDB", back_populates="message")
    deliveries   = relationship("MessageDeliveryDB", back_populates="message")


class MessageOptionDB(Base):
    __tablename__ = "message_options"

    id            = Column(Integer, primary_key=True)
    message_id    = Column(Integer, ForeignKey("messages.id"))
    choice        = Column(String(255))
    amount        = Column(Integer)
    message_text  = Column(String(255), nullable=False)  # <-- Add this

    message       = relationship("MessageDB", back_populates="options")

class MessageDeliveryDB(Base):
    __tablename__ = "message_deliveries"
    __table_args__ = {"extend_existing": True}

    id           = Column(Integer, primary_key=True)
    message_id   = Column(Integer, ForeignKey("messages.id"))
    phone_number = Column(String(255))
    status       = Column(String(255))
    api_response = Column(String(255))

    message      = relationship("MessageDB", back_populates="deliveries")
