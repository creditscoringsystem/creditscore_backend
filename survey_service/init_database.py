import os
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models.survey import Base

# Load environment variables
load_dotenv()

QUESTIONS_DATABASE_URL = os.getenv("QUESTIONS_DATABASE_URL", "postgresql://kong:kong@localhost:5432/survey_questions")
ANSWERS_DATABASE_URL = os.getenv("ANSWERS_DATABASE_URL", "postgresql://kong:kong@localhost:5432/survey_answers")

def create_databases():
    """Tạo các database cần thiết"""
    try:
        # Kết nối đến PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="kong",
            password="kong",
            database="kong"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Tạo database cho questions
        try:
            cursor.execute("CREATE DATABASE survey_questions")
            print("✅ Database 'survey_questions' created successfully")
        except psycopg2.errors.DuplicateDatabase:
            print("ℹ️ Database 'survey_questions' already exists")
        
        # Tạo database cho answers
        try:
            cursor.execute("CREATE DATABASE survey_answers")
            print("✅ Database 'survey_answers' created successfully")
        except psycopg2.errors.DuplicateDatabase:
            print("ℹ️ Database 'survey_answers' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating databases: {e}")
        return False
    
    return True

def create_tables():
    """Tạo các bảng trong database"""
    try:
        # Tạo bảng trong questions database
        questions_engine = create_engine(QUESTIONS_DATABASE_URL)
        Base.metadata.create_all(bind=questions_engine)
        print("✅ Tables created in 'survey_questions' database")
        
        # Tạo bảng trong answers database
        answers_engine = create_engine(ANSWERS_DATABASE_URL)
        Base.metadata.create_all(bind=answers_engine)
        print("✅ Tables created in 'survey_answers' database")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Initializing survey service tables...")
    if create_tables():
        print("✅ Table initialization completed successfully!")
    else:
        print("❌ Failed to create tables") 