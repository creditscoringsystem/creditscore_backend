import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from models.base import Base
# Import models module to ensure SQLAlchemy tables are registered
import models.score  # noqa: F401
import time
from sqlalchemy import exc as sa_exc

def _is_render_env() -> bool:
    return any(
        os.getenv(k) for k in ["RENDER", "RENDER_SERVICE_ID", "RENDER_EXTERNAL_URL"]
    )

# Load .env only locally
if not _is_render_env():
    load_dotenv()

def _get_database_url() -> str:
    url = (
        os.getenv("DATABASE_URL")
        or os.getenv("SCORE_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("RENDER_DATABASE_URL")
    )
    if not url:
        raise RuntimeError(
            "Database URL not configured. Set SCORE_DATABASE_URL or DATABASE_URL in environment."
        )
    is_render = _is_render_env()
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
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    max_retries = int(os.getenv("DB_MAX_RETRIES", "10"))
    retry_interval = int(os.getenv("DB_RETRY_INTERVAL", "3"))

    attempt = 0
    while True:
        try:
            with engine.begin() as conn:
                Base.metadata.create_all(bind=conn)
            break
        except (sa_exc.OperationalError, sa_exc.InterfaceError):
            attempt += 1
            if attempt > max_retries:
                raise
            time.sleep(retry_interval)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()