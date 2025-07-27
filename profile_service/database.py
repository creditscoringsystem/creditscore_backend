import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

PROFILE_DATABASE_URL = os.getenv("PROFILE_DATABASE_URL")
engine = create_engine(PROFILE_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 