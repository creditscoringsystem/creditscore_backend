# Profile Service API

## Mô tả
Profile Service quản lý thông tin hồ sơ cá nhân, bảo mật, tùy chọn và đồng ý của người dùng.

## Architecture Best Practice

### **Service Separation:**
- **User Service**: Quản lý authentication và core user data (username, password)
- **Profile Service**: Quản lý extended personal information (full_name, email, phone, etc.)

### **Data Flow:**
```
1. User Signup → User Service (username, password)
2. Get user_id → Pass to Profile Service via X-User-Id header
3. Create Profile → Profile Service (full_name, email, phone, etc.)
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
uvicorn main:app --reload --host 0.0.0.0 --port 9008
```

## API Documentation

### Swagger UI
Truy cập: `http://localhost:9008/docs`

### ReDoc
Truy cập: `http://localhost:9008/redoc`

## Authentication

Tất cả endpoints yêu cầu header `X-User-Id` để xác thực:

```bash
curl -H "X-User-Id: your_user_id" http://localhost:9008/profile/me
```

## Endpoints

### Profile Management
- `GET /profile/me` - Lấy thông tin hồ sơ cá nhân
- `PUT /profile/me` - Cập nhật hồ sơ cá nhân
- `POST /profile/me` - Tạo mới hồ sơ cá nhân

### Security
- `POST /security/2fa/enable` - Bật xác thực 2 yếu tố
- `POST /security/2fa/disable` - Tắt xác thực 2 yếu tố
- `GET /security/devices` - Lấy danh sách thiết bị
- `DELETE /security/devices/{device_id}` - Xóa thiết bị

### Preferences
- `GET /preferences/me` - Lấy tùy chọn người dùng
- `PUT /preferences/me` - Cập nhật tùy chọn người dùng

### Consent
- `GET /consent/me` - Lấy danh sách đồng ý
- `POST /consent/revoke` - Thu hồi đồng ý

## Workflow Example

### 1. User Signup (User Service)
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

### 2. Create Profile (Profile Service)
```bash
curl -X POST "http://localhost:9008/profile/me" \
  -H "X-User-Id: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nguyễn Văn A",
    "email": "nguyenvana@gmail.com",
    "phone": "0123456789",
    "avatar": "https://example.com/avatar.jpg",
    "date_of_birth": "1990-01-01",
    "address": "123 Đường ABC, Quận 1, TP.HCM"
  }'
```

### 3. Get Profile
```bash
curl -X GET "http://localhost:9008/profile/me" \
  -H "X-User-Id: 1"
```

### 4. Update Profile
```bash
curl -X PUT "http://localhost:9008/profile/me" \
  -H "X-User-Id: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nguyễn Văn B",
    "email": "nguyenvanb@gmail.com"
  }'
```

## Data Models

### Profile Model
```python
class Profile(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String)  # Secondary email (có thể khác với User Service)
    phone = Column(String)
    avatar = Column(String)
    date_of_birth = Column(Date)
    address = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

## Error Codes

- `400` - Bad Request (dữ liệu không hợp lệ)
- `401` - Unauthorized (thiếu header X-User-Id)
- `404` - Not Found (không tìm thấy resource)
- `422` - Validation Error (dữ liệu không đúng format)

## Development

### Cấu trúc thư mục
```
profile_service/
├── main.py              # FastAPI app
├── database.py          # Database configuration
├── core/
│   └── security.py      # Authentication logic
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── routers/             # API endpoints
└── crud/                # Database operations
```

### Best Practices Implemented

1. **Loose Coupling**: User Service và Profile Service độc lập
2. **No Data Duplication**: Không trùng lặp dữ liệu giữa services
3. **Proper Validation**: Validation cho tất cả input fields
4. **Clear Documentation**: Swagger UI với examples
5. **Error Handling**: Proper HTTP status codes và error messages
6. **Security**: X-User-Id header authentication

### Thêm endpoint mới
1. Tạo schema trong `schemas/`
2. Tạo router trong `routers/`
3. Import router trong `main.py`
4. Thêm documentation và examples 