FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install essential packages
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib python-multipart python-dotenv

# Copy all files
COPY . /app/

EXPOSE 8004

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8004}"]


