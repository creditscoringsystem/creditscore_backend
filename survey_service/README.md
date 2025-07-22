# Survey Service

Service quản lý câu hỏi khảo sát và câu trả lời của người dùng cho hệ thống credit scoring.

## 🏗️ Cấu trúc dự án

```
survey_service/
├── main.py                 # FastAPI app chính
├── database.py             # Cấu hình kết nối database
├── models/
│   └── survey.py          # SQLAlchemy models
├── schemas/
│   └── survey.py          # Pydantic schemas
├── crud/
│   └── crud.py            # CRUD operations
├── routers/
│   └── survey.py          # API endpoints
├── core/
│   ├── security.py        # Authentication & authorization
│   └── validation.py      # Data validation
├── requirements.txt       # Python dependencies
├── init_database.py       # Script khởi tạo database
├── import_questions.py    # Script import câu hỏi từ CSV
└── sample_questions.csv   # File CSV mẫu với 20 câu hỏi
```

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
cd survey_service
pip install -r requirements.txt
```

### 2. Tạo file .env
```bash
# Database URLs
QUESTIONS_DATABASE_URL=postgresql://kong:kong@localhost:5432/survey_questions
ANSWERS_DATABASE_URL=postgresql://kong:kong@localhost:5432/survey_answers

# JWT Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256

# Service Settings
SERVICE_PORT=8002
SERVICE_HOST=0.0.0.0
```

### 3. Khởi tạo database
```bash
python init_database.py
```

### 4. Import câu hỏi mẫu
```bash
python import_questions.py
```

### 5. Chạy service
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

## 📊 API Endpoints

### Public Endpoints
- `GET /questions` - Lấy danh sách tất cả câu hỏi

### User Endpoints (cần JWT token)
- `POST /submit` - Gửi câu trả lời khảo sát
- `GET /answers/{user_id}` - Lấy câu trả lời của user

### Admin Endpoints (cần admin role)
- `POST /admin/import-questions` - Import câu hỏi từ CSV
- `GET /admin/statistics` - Thống kê tổng quan
- `GET /admin/question-stats/{question_id}` - Thống kê theo câu hỏi

## 🔐 Authentication

Service sử dụng JWT Bearer token:
- Header: `Authorization: Bearer <token>`
- Token chứa: `user_id`, `role` (user/admin)

## 📝 Cấu trúc câu hỏi

### 4 nhóm câu hỏi:
1. **basic_info** - Thông tin cơ bản (tuổi, giới tính, học vấn, nghề nghiệp, thu nhập)
2. **credit_limit_usage** - Giới hạn tín dụng và sử dụng (thời gian sử dụng, giới hạn, % sử dụng)
3. **payment_history** - Lịch sử thanh toán (đúng hạn, trễ hạn, phạt phí)
4. **psychometric** - Câu hỏi tâm lý (kế hoạch tài chính, tiết kiệm, rủi ro)

### Các loại câu hỏi:
- `single_choice` - Chọn 1 đáp án
- `multiple_choice` - Chọn nhiều đáp án
- `number` - Nhập số
- `text` - Nhập text

## 🛡️ Tính năng bảo mật

- **Authentication**: JWT token validation
- **Authorization**: Role-based access (user/admin)
- **Anti-spam**: Chỉ cho phép submit 1 lần per user
- **Validation**: Kiểm tra kiểu dữ liệu và giá trị hợp lệ
- **Rate limiting**: Thông qua Kong API Gateway

## 📈 Thống kê và báo cáo

### Admin có thể xem:
- Tổng số user đã submit survey
- Thống kê theo từng câu hỏi
- Phân tích theo nhóm câu hỏi
- Export dữ liệu

## 🔧 Development

### Chạy tests
```bash
# TODO: Thêm tests
```

### Format code
```bash
# TODO: Thêm black, flake8
```

## 📋 TODO

- [x] Models và database schema
- [x] CRUD operations
- [x] API endpoints
- [x] Authentication & authorization
- [x] Data validation
- [x] Anti-spam protection
- [x] Admin statistics
- [ ] Unit tests
- [ ] Integration tests
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring & logging
- [ ] Performance optimization 