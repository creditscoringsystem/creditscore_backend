import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()


SURVEY_DATABASE_URL: str = os.getenv("SURVEY_DATABASE_URL")

# Engine và session cho questions_db
engine = create_engine(
    SURVEY_DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
