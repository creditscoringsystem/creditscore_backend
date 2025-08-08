import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Single database only
SURVEY_DATABASE_URL = os.getenv("SURVEY_DATABASE_URL", "postgresql://kong:kong@localhost:5432/survey_db")

engine = create_engine(SURVEY_DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
