# Credit Score Backend

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A microservices backend system for Credit Score applications, built with FastAPI and PostgreSQL, using Kong API Gateway for service management.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kong Gateway  │    │   Kong Gateway  │    │   Kong Gateway  │
│   (Port 8000)   │    │   (Port 8001)   │    │   (Port 8443)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      PostgreSQL DB        │
                    │      (Port 5432)          │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
        ┌───────────┴───────────┬───────────────┴───────────┐
        │                       │                           │
┌───────▼────────┐  ┌──────────▼─────────┐  ┌──────────────▼─────────┐
│  User Service  │  │  Profile Service   │  │   Survey Service      │
│   (Port 8002)  │  │   (Port 8003)     │  │    (Port 8005)        │
└────────────────┘  └────────────────────┘  └────────────────────────┘
        │                       │                           │
        └───────────────────────┼───────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Alert Service       │
                    │   (Port 8004)        │
                    └───────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Score Service       │
                    │   (Port 8007)        │
                    └───────────────────────┘
```

## 🚀 Services

### 1. **User Service** (`user_service/`)
- **Port**: 8002
- **Functionality**: Authentication, authorization, and core user data management
- **API Endpoints**:
  - `/auth/*` - Registration, login, password management
  - `/users/*` - Current user information management
  - `/admin/*` - All users management (admin only)
- **Authentication**: JWT Bearer Token
- **Database**: Auto-creates tables on startup

### 2. **Profile Service** (`profile_service/`)
- **Port**: 8003
- **Functionality**: Personal profile information and preferences management
- **API Endpoints**:
  - `/profile/*` - Personal information management
  - `/preferences/*` - Theme and language preferences
- **Authentication**: `X-User-Id` Header
- **Database**: Auto-creates tables on startup

### 3. **Alert Service** (`alert_service/`)
- **Port**: 8004
- **Functionality**: Alerts and milestones management for credit scoring system
- **API Endpoints**:
  - `/alerts/*` - Alerts and notifications management
  - `/score-updates/*` - Credit score update processing
- **Features**: Milestone logic, alert management
- **Database**: Auto-creates tables on startup

### 4. **Survey Service** (`survey_service/`)
- **Port**: 8005
- **Functionality**: Survey questions and answers management
- **API Endpoints**:
  - `/survey/*` - Survey operations
- **Features**: Question management, answer processing
- **Database**: Auto-creates tables on startup

### 5. **Score Service** (`score_service/`)
- **Port**: 8007
- **Functionality**: Credit score calculation and management
- **API Endpoints**:
  - `/scores/*` - Score operations and calculations
- **Features**: ML integration, score processing
- **Database**: Auto-creates tables on startup

## 🛠️ Technologies Used

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation

### Database
- **PostgreSQL 17** - Primary database
- **SQLAlchemy ORM** - Database abstraction layer
- **Auto Table Creation** - Tables are automatically created on service startup

### API Gateway & Management
- **Kong 3.6** - API Gateway and Load Balancer
- **Konga** - Web-based admin interface for Kong

### Security & Authentication
- **JWT** - JSON Web Tokens for authentication
- **Passlib** - Password hashing library
- **Python-jose** - JavaScript Object Signing and Encryption

### Development & Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **CORS** - Cross-Origin Resource Sharing support

## 📋 System Requirements

- **Python**: 3.8+
- **Docker**: 20.10+
- **Docker Compose**: 1.29+
- **PostgreSQL**: 17+ (local installation)
- **RAM**: Minimum 4GB
- **Disk**: Minimum 10GB free space

## 🚀 Installation and Setup

### 1. Clone repository
```bash
git clone <repository-url>
cd creditscore_backend
```

### 2. Install PostgreSQL locally
```bash
# Windows: Download from https://www.postgresql.org/download/windows/
# Or use Docker:
docker run --name postgres-local -e POSTGRES_PASSWORD=180806 -p 5432:5432 -d postgres:17
```

### 3. Create databases
```sql
-- Connect to PostgreSQL and create databases
CREATE DATABASE user_db;
CREATE DATABASE profile_db;
CREATE DATABASE alert_db;
CREATE DATABASE survey_db;
CREATE DATABASE score_db;
```

### 4. Run with Docker Compose (Recommended)
```bash
# Start the entire system
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the system
docker-compose down
```

### 5. Run individual services
```bash
# User Service
cd user_service
docker build -t user-service .
docker run -p 8002:8002 user-service

# Profile Service
cd profile_service
docker build -t profile-service .
docker run -p 8003:8003 profile-service

# Alert Service
cd alert_service
docker build -t alert-service .
docker run -p 8004:8004 alert-service

# Survey Service
cd survey_service
docker build -t survey-service .
docker run -p 8005:8005 survey-service

# Score Service
cd score_service
docker build -t score-service .
docker run -p 8007:8007 score-service
```

### 6. Run without Docker (Development)
```bash
# Install dependencies
pip install -r requirements.txt

# User Service
cd user_service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Profile Service
cd profile_service
uvicorn main:app --host 0.0.0.0 --port 8003 --reload

# Alert Service
cd alert_service
uvicorn main:app --host 0.0.0.0 --port 8004 --reload

# Survey Service
cd survey_service
uvicorn main:app --host 0.0.0.0 --port 8005 --reload

# Score Service
cd score_service
uvicorn main:app --host 0.0.0.0 --port 8007 --reload
```

## 🌐 Service Access

| Service | URL | Port | Description |
|---------|-----|------|-------------|
| **Kong Gateway** | http://localhost:8000 | 8000 | API Gateway |
| **Kong Admin** | http://localhost:8001 | 8001 | Kong Admin API |
| **Konga** | http://localhost:1337 | 1337 | Kong Admin UI |
| **User Service** | http://localhost:8002 | 8002 | User Management |
| **Profile Service** | http://localhost:8003 | 8003 | Profile Management |
| **Alert Service** | http://localhost:8004 | 8004 | Alert Management |
| **Survey Service** | http://localhost:8005 | 8005 | Survey Management |
| **Score Service** | http://localhost:8007 | 8007 | Score Management |

## 📚 API Documentation

Each service has Swagger UI documentation:

- **User Service**: http://localhost:8002/docs
- **Profile Service**: http://localhost:8003/docs
- **Alert Service**: http://localhost:8004/docs
- **Survey Service**: http://localhost:8005/docs
- **Score Service**: http://localhost:8007/docs

## 🔐 Authentication

### JWT Token (User Service)
```bash
# Login to get token
curl -X POST "http://localhost:8002/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token
curl -H "Authorization: Bearer <your-jwt-token>" \
  "http://localhost:8002/users/me"
```

### User ID Header (Profile Service)
```bash
curl -H "X-User-Id: <user-id>" \
  "http://localhost:8003/profile/me"
```

## 🗄️ Database

### PostgreSQL Connection
```bash
# Direct connection
psql -h localhost -U postgres -p 5432

# From Docker container
docker exec -it postgres-local psql -U postgres
```

### Database URLs (Auto-configured in Docker)
```bash
# User Service
postgresql://postgres:180806@host.docker.internal:5432/user_db

# Profile Service
postgresql://postgres:180806@host.docker.internal:5432/profile_db

# Alert Service
postgresql://postgres:180806@host.docker.internal:5432/alert_db

# Survey Service
postgresql://postgres:180806@host.docker.internal:5432/survey_db

# Score Service
postgresql://postgres:180806@host.docker.internal:5432/score_db
```

### Auto Table Creation
All services automatically create their database tables on startup using SQLAlchemy's `Base.metadata.create_all()`. No manual database setup required!

## 🧪 Testing

### Run tests for each service
```bash
# Alert Service
cd alert_service/scripts
python test_alerts.py

# Survey Service
cd survey_service/scripts
./test_survey.ps1
```

## 📁 Project Structure

```
creditscore_backend/
├── docker-compose.yml          # Docker orchestration with environment variables
├── requirements.txt            # Root dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore patterns
├── user_service/              # User management service
│   ├── main.py               # FastAPI application
│   ├── models/               # Database models (auto-created)
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   ├── crud/                 # Database operations
│   └── core/                 # Core utilities
├── profile_service/           # Profile management service
│   ├── main.py               # FastAPI application
│   ├── models/               # Database models (auto-created)
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   └── core/                 # Core utilities
├── alert_service/             # Alert management service
│   ├── main.py               # FastAPI application
│   ├── models/               # Database models (auto-created)
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   ├── core/                 # Core utilities
│   └── scripts/              # Test scripts
├── survey_service/            # Survey management service
│   ├── main.py               # FastAPI application
│   ├── models/               # Database models (auto-created)
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   └── scripts/              # Test scripts
└── score_service/             # Score management service
    ├── main.py               # FastAPI application
    ├── models/               # Database models (auto-created)
    ├── schemas/              # Pydantic schemas
    ├── routers/              # API endpoints
    └── services/             # ML and alert integration
```

## 🔧 Development

### Environment Variables
Environment variables are configured directly in `docker-compose.yml`:

```yaml
environment:
  USER_DATABASE_URL: postgresql://postgres:180806@host.docker.internal:5432/user_db
  SECRET_KEY: your-secret-key-here
  ALGORITHM: HS256
  ACCESS_TOKEN_EXPIRE_MINUTES: 30
```

### Database Configuration
- **Host**: `host.docker.internal` (for Docker containers to access local PostgreSQL)
- **User**: `postgres`
- **Password**: `180806` (change in production)
- **Port**: `5432`

### Code Style
- Use **Black** for code formatting
- Follow **PEP 8** guidelines
- Use **type hints** for all functions
- Write **docstrings** for all functions and classes

### Adding New Service
1. Create new service directory
2. Copy template from existing service
3. Update `docker-compose.yml` with environment variables
4. Add service to Kong Gateway
5. Update documentation

## 🚀 Deployment

### Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```bash
# Production settings
NODE_ENV=production
KONG_ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/dbname
```

## 🐳 Docker Commands

### Quick Start
```bash
# Start all services
docker-compose up --build

# Start specific service
docker-compose up user_service

# View logs
docker-compose logs -f user_service

# Stop all
docker-compose down

# Rebuild and start
docker-compose up --build --force-recreate
```

### Troubleshooting
```bash
# Check service status
docker-compose ps

# Check service logs
docker-compose logs user_service

# Restart service
docker-compose restart user_service

# Remove all containers and volumes
docker-compose down -v
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the [MIT License](LICENSE).

## 📞 Support

- **Email**: support@creditscore.com
- **Documentation**: [API Docs](./docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- Kong team for the API Gateway
- PostgreSQL team for the database system
- Open source community

---

**Made with ❤️ by Andy**
