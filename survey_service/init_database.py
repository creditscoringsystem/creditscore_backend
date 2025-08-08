import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models.survey import Base

# Load environment variables
load_dotenv()

SURVEY_DATABASE_URL = os.getenv("SURVEY_DATABASE_URL", "postgresql://kong:kong@localhost:5432/survey")

def create_tables():
    """Tạo các bảng trong database"""
    try:
        engine = create_engine(SURVEY_DATABASE_URL, future=True)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created in 'survey' database")

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