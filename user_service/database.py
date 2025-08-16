from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from models.base import Base
from models.user import User

# Load .env locally; on Render, env vars come from dashboard
load_dotenv()

def _get_database_url() -> str:
    """Resolve DB URL from environment with sensible fallbacks.
    Priority:
      1) USER_DATABASE_URL (service-specific)
      2) DATABASE_URL (Render default)
      3) POSTGRES_URL / RENDER_DATABASE_URL (extra fallbacks)
    Adds sslmode=require automatically on Render if missing.
    """
    url = (
        os.getenv("USER_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("RENDER_DATABASE_URL")
    )

    if not url:
        raise RuntimeError(
            "Database URL not configured. Set USER_DATABASE_URL or DATABASE_URL in environment."
        )

    # Ensure sslmode=require on Render unless already specified
    is_render = any(
        os.getenv(k) for k in ["RENDER", "RENDER_SERVICE_ID", "RENDER_EXTERNAL_URL"]
    )
    try:
        parsed = urlparse(url)
    except Exception:
        # Let SQLAlchemy handle invalid strings, but keep our message clearer
        return url

    # If it's a Postgres URL and on Render, enforce sslmode=require
    if parsed.scheme.startswith("postgres") and is_render:
        query = dict(parse_qsl(parsed.query)) if parsed.query else {}
        if "sslmode" not in query:
            query["sslmode"] = "require"
            parsed = parsed._replace(query=urlencode(query))
            url = urlunparse(parsed)

    return url

DATABASE_URL = _get_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()