# FILE: app/db/models/game.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class RoundDB(Base):
    __tablename__ = "rounds"
    id          = Column(Integer, primary_key=True)
    question    = Column(String(255))
    status      = Column(String(255), default="open")          # open / closed / drawn
    opened_at   = Column(DateTime, default=datetime.utcnow)
    closed_at   = Column(DateTime)
    messages = relationship("MessageDB", back_populates="round")

    tickets     = relationship("TicketDB", back_populates="round")


class TicketDB(Base):
    __tablename__ = "tickets"
    id          = Column(Integer, primary_key=True)
    round_id    = Column(Integer, ForeignKey("rounds.id"))
    message_id  = Column(Integer, ForeignKey("messages.id"))
    phone       = Column(String(255))
    choice      = Column(String(255))
    amount      = Column(Integer)
    status      = Column(String(255), default="pending")       # pending / paid / won / lost
    payment_ref = Column(String(255), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    round       = relationship("RoundDB", back_populates="tickets")
