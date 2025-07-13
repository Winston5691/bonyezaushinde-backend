# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.routes import auth, customer, message, mpesa
from app.db.session import SessionLocal, engine
from app.db.seeder import seed_db

app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ← tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(auth.router,     prefix="/auth",      tags=["auth"])
app.include_router(customer.router, prefix="/customers", tags=["customers"])
app.include_router(message.router,  prefix="/messages",  tags=["messages"])
app.include_router(mpesa.router,    prefix="/mpesa",     tags=["mpesa"])

# ── Dependency for debug route ────────────────────────────────────────
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional debug endpoint
@app.get("/debug/db", tags=["debug"])
def show_db_info(db: Session = Depends(get_db)):
    dialect = db.bind.dialect.name
    if dialect == "mysql":
        db_name = db.execute(text("SELECT DATABASE()")).scalar()
        return {"dialect": dialect, "database": db_name}
    return {"dialect": dialect}

# ── Startup hook ──────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup() -> None:
    # Log which engine we are using
    print("🛢️  SQLAlchemy URL:", engine.url)
    # Seed initial data
    seed_db(SessionLocal)
