import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc as sa_exc
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from models.base import Base
from models.alert import Alert

def _is_render_env() -> bool:
    return any(
        os.getenv(k) for k in ["RENDER", "RENDER_SERVICE_ID", "RENDER_EXTERNAL_URL"]
    )

# Chỉ load .env ở môi trường local/dev, tránh ghi đè biến môi trường đúng trên Render
if not _is_render_env():
    load_dotenv()

def _get_database_url() -> str:
    # Ưu tiên DATABASE_URL trước để không bị giá trị ALERT_DATABASE_URL trong .env local lấn át khi deploy
    url = (
        os.getenv("DATABASE_URL")
        or os.getenv("ALERT_DATABASE_URL")
        or os.getenv("SCORE_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("RENDER_DATABASE_URL")
    )
    if not url:
        raise RuntimeError(
            "Database URL not configured. Set ALERT_DATABASE_URL or DATABASE_URL in environment."
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
    """Kết nối DB và tạo bảng với cơ chế retry.

    Hữu ích khi deploy trên Render: DB có thể chưa sẵn ở thời điểm app khởi chạy.
    Có thể điều chỉnh số lần thử và thời gian chờ qua biến môi trường:
      - DB_MAX_RETRIES (mặc định 10)
      - DB_RETRY_INTERVAL (giây, mặc định 3)
    """
    max_retries = int(os.getenv("DB_MAX_RETRIES", "10"))
    retry_interval = int(os.getenv("DB_RETRY_INTERVAL", "3"))

    attempt = 0
    while True:
        try:
            # Thử mở kết nối và tạo bảng
            with engine.begin() as conn:
                Base.metadata.create_all(bind=conn)
            break
        except (sa_exc.OperationalError, sa_exc.InterfaceError) as e:
            attempt += 1
            if attempt > max_retries:
                # Hết lần thử -> raise để Render ghi log lỗi đúng nguyên nhân
                raise
            time.sleep(retry_interval)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


