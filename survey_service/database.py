import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from models.base import Base
# Ensure models are imported so SQLAlchemy registers tables
import models.survey  # noqa: F401

# Load biến môi trường từ file .env
load_dotenv()

def _get_database_url() -> str:
    url = (
        os.getenv("SURVEY_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("RENDER_DATABASE_URL")
    )
    if not url:
        raise RuntimeError(
            "Database URL not configured. Set SURVEY_DATABASE_URL or DATABASE_URL in environment."
        )
    is_render = any(
        os.getenv(k) for k in ["RENDER", "RENDER_SERVICE_ID", "RENDER_EXTERNAL_URL"]
    )
    try:
        parsed = urlparse(url)
    except Exception:
        return url
    if parsed.scheme.startswith("postgres") and is_render:
        query = dict(parse_qsl(parsed.query)) if parsed.query else {}
        if "sslmode" not in query:
            query["sslmode"] = "require"
            parsed = parsed._replace(query=urlencode(query))
            url = urlunparse(parsed)
    return url

DATABASE_URL = _get_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Auto create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
