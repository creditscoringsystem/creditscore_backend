# User Service API

## Mô tả
User Service quản lý authentication và core user data (username, password).

## Architecture Best Practice

### **Service Separation:**
- **User Service**: Quản lý authentication và core user data (username, password)
- **Profile Service**: Quản lý extended personal information (full_name, email, phone, etc.)

### **Data Flow:**
```
1. User Signup → User Service (username, password)
2. Login → Lấy access token
3. Use token → Truy cập protected endpoints
4. Create Profile → Profile Service (personal info)
```

## Cài đặt và chạy

### Yêu cầu
- Python 3.8+
- FastAPI
- SQLAlchemy
- Pydantic

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Chạy server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

### Swagger UI
Truy cập: `http://localhost:8000/docs`

### ReDoc
Truy cập: `http://localhost:8000/redoc`

## Authentication

### Public Endpoints (Không cần token)
- `POST /auth/signup` - Đăng ký tài khoản
- `POST /auth/login` - Đăng nhập
- `POST /auth/forgot-password` - Quên mật khẩu
- `POST /auth/reset-password` - Đặt lại mật khẩu

### Protected Endpoints (Cần Bearer token)
- `GET /users/me` - Lấy thông tin user hiện tại
- `PUT /users/me` - Cập nhật thông tin user
- `DELETE /users/me` - Xóa tài khoản
- Tất cả admin endpoints

## Endpoints

### Auth (Public)
- `POST /auth/signup` - Đăng ký tài khoản mới
- `POST /auth/login` - Đăng nhập và lấy access token
- `POST /auth/verify-token` - Xác thực token
- `POST /auth/forgot-password` - Quên mật khẩu
- `POST /auth/reset-password` - Đặt lại mật khẩu
- `POST /auth/change-password` - Đổi mật khẩu

### Users (Protected)
- `GET /users/me` - Lấy thông tin user hiện tại
- `PUT /users/me` - Cập nhật thông tin user
- `DELETE /users/me` - Xóa tài khoản

### Admin (Admin only)
- `GET /admin/users` - Lấy danh sách tất cả users
- `POST /admin/users` - Tạo user mới
- `GET /admin/users/{user_id}` - Lấy thông tin user theo ID
- `PUT /admin/users/{user_id}` - Cập nhật user theo ID
- `DELETE /admin/users/{user_id}` - Xóa user theo ID
- `GET /admin/summary` - Thống kê tổng quan hệ thống

## Workflow Example

### 1. User Signup
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secret123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "disabled": false,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secret123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get User Info
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Update User Info
```bash
curl -X PUT "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_updated"
  }'
```

### 5. Admin Operations
```bash
# Lấy danh sách users (admin only)
curl -X GET "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Tạo user mới (admin only)
curl -X POST "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "password": "password123"
  }'
```

## Data Models

### User Model
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)  # Core auth data
    hashed_password = Column(String)        # Core auth data
    disabled = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    reset_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## Error Codes

- `400` - Bad Request (dữ liệu không hợp lệ)
- `401` - Unauthorized (thiếu hoặc invalid token)
- `403` - Forbidden (không có quyền admin)
- `404` - Not Found (không tìm thấy resource)
- `422` - Validation Error (dữ liệu không đúng format)

## Security

### Authentication Flow
1. **Signup** → Tạo user với username/password
2. **Login** → Verify credentials và trả về JWT token
3. **Protected endpoints** → Verify JWT token trong Authorization header

### Admin Authorization
- Admin endpoints yêu cầu `is_admin: true` trong JWT token
- User phải có `is_admin=True` trong database

## Development

### Cấu trúc thư mục
```
user_service/
├── main.py              # FastAPI app
├── database.py          # Database configuration
├── core/
│   └── security.py      # JWT authentication logic
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── routers/             # API endpoints
│   ├── auth.py         # Authentication endpoints
│   ├── users.py        # User management endpoints
│   └── admin.py        # Admin endpoints
└── crud/                # Database operations
```

### Best Practices Implemented

1. **Clear Separation**: Auth, Users, Admin endpoints riêng biệt
2. **Proper Authentication**: JWT token với Bearer scheme
3. **Admin Authorization**: Role-based access control
4. **Input Validation**: Pydantic schemas với validation
5. **Error Handling**: Proper HTTP status codes
6. **Documentation**: Swagger UI với examples

### Thêm endpoint mới
1. Tạo schema trong `schemas/`
2. Tạo router trong `routers/`
3. Import router trong `main.py`
4. Thêm documentation và examples 