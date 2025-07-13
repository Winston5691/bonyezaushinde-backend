# scripts/init_db.py
import time
from app.db.base import Base
from app.db.session import engine

# ✅ Force-load models so they are registered
from app.models import customer, message_delivery, payment, received_sms, user
from app.db.models import message, game  # if you have models here too

print(f"📡 USING DATABASE_URL: {engine.url}")
print("⏳ Creating tables...")

Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully.")
