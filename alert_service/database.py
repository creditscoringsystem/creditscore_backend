import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models.base import Base

load_dotenv()

ALERT_DATABASE_URL = os.getenv("ALERT_DATABASE_URL") or os.getenv("SCORE_DATABASE_URL") or os.getenv("DATABASE_URL")
if not ALERT_DATABASE_URL:
    raise RuntimeError("ALERT_DATABASE_URL is not set")

engine = create_engine(ALERT_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


