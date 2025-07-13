from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

print("Creating engine with DATABASE_URL:", settings.DATABASE_URL)  # debug print

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)