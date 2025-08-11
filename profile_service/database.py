import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models.base import Base
from models.profile import Profile
from models.consent import Consent
from models.device import Device

load_dotenv()

PROFILE_DATABASE_URL = os.getenv("PROFILE_DATABASE_URL")
engine = create_engine(PROFILE_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Auto create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 