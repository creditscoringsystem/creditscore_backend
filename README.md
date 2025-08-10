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

### 2. **Profile Service** (`profile_service/`)
- **Port**: 8003
- **Functionality**: Personal profile information and preferences management
- **API Endpoints**:
  - `/profile/*` - Personal information management
  - `/preferences/*` - Theme and language preferences
- **Authentication**: `X-User-Id` Header

### 3. **Alert Service** (`alert_service/`)
- **Port**: 8004
- **Functionality**: Alerts and milestones management for credit scoring system
- **API Endpoints**:
  - `/alerts/*` - Alerts and notifications management
  - `/score-updates/*` - Credit score update processing
- **Features**: Milestone logic, alert management

### 4. **Survey Service** (`survey_service/`)
- **Port**: 8005
- **Functionality**: Survey questions and answers management
- **API Endpoints**:
  - `/survey/*` - Survey operations
- **Features**: Question management, answer processing

## 🛠️ Technologies Used

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation

### Database
- **PostgreSQL 17** - Primary database
- **SQLAlchemy ORM** - Database abstraction layer

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
- **RAM**: Minimum 4GB
- **Disk**: Minimum 10GB free space

## 🚀 Installation and Setup

### 1. Clone repository
```bash
git clone <repository-url>
cd creditscore_backend
```

### 2. Install dependencies
```bash
# Install dependencies for each service
pip install -r requirements.txt
pip install -r user_service/requirements.txt
pip install -r profile_service/requirements.txt
pip install -r survey_service/requirements.txt
pip install -r alert_service/requirements.txt
```

### 3. Run with Docker Compose
```bash
# Start the entire system
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the system
docker-compose down
```

### 4. Run individual services
```bash
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

## 📚 API Documentation

Each service has Swagger UI documentation:

- **User Service**: http://localhost:8002/docs
- **Profile Service**: http://localhost:8003/docs
- **Alert Service**: http://localhost:8004/docs
- **Survey Service**: http://localhost:8005/docs

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
psql -h localhost -U kong -d kong -p 5432

# From Docker container
docker exec -it kong-database psql -U kong -d kong
```

### Database URLs
```bash
# Kong Database
postgresql://kong:kong@localhost:5432/kong

# Alert Service Database
postgresql://kong:kong@localhost:5432/alert_service
```

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
├── docker-compose.yml          # Docker orchestration
├── requirements.txt            # Root dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore patterns
├── user_service/              # User management service
│   ├── main.py               # FastAPI application
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   ├── crud/                 # Database operations
│   └── core/                 # Core utilities
├── profile_service/           # Profile management service
│   ├── main.py               # FastAPI application
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   └── core/                 # Core utilities
├── alert_service/             # Alert management service
│   ├── main.py               # FastAPI application
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   ├── core/                 # Core utilities
│   └── scripts/              # Test scripts
└── survey_service/            # Survey management service
    ├── main.py               # FastAPI application
    ├── models/               # Database models
    ├── schemas/              # Pydantic schemas
    ├── routers/              # API endpoints
    └── scripts/              # Test scripts
```

## 🔧 Development

### Environment Variables
Create `.env` file in each service directory:

```bash
# Database
DATABASE_URL=postgresql://kong:kong@localhost:5432/service_name

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service Configuration
SERVICE_PORT=8004
SERVICE_NAME=alert-service
```

### Code Style
- Use **Black** for code formatting
- Follow **PEP 8** guidelines
- Use **type hints** for all functions
- Write **docstrings** for all functions and classes

### Adding New Service
1. Create new service directory
2. Copy template from existing service
3. Update `docker-compose.yml`
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
