from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.db.base import Base
from app.core.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.db.models import message


# app/db/seeder.py

def seed_db(session_factory=SessionLocal):  # ✅ Accept SessionLocal as default
    db = session_factory()
    Base.metadata.create_all(bind=db.get_bind())  # Use the engine from the session
    if not db.query(User).filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("[✓] Admin user seeded")
    db.close()
