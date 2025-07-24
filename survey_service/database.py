import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

QUESTIONS_DATABASE_URL = os.getenv("QUESTIONS_DATABASE_URL")
ANSWERS_DATABASE_URL = os.getenv("ANSWERS_DATABASE_URL")

# Engine và session cho questions_db
questions_engine = create_engine(QUESTIONS_DATABASE_URL)
QuestionsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=questions_engine)

# Engine và session cho answers_db
answers_engine = create_engine(ANSWERS_DATABASE_URL)
AnswersSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=answers_engine)
