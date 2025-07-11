# Redis & ElasticSearch Data Integrity Project

Dự án demo về cách triển khai Redis và ElasticSearch với đảm bảo tính toàn vẹn dữ liệu với database chính (PostgreSQL).

## Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │  ElasticSearch  │
│  (Primary DB)   │◄──►│   (Cache)       │◄──►│  (Search)       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Python API     │
                    │  (Backend)      │
                    └─────────────────┘
```

## Tính năng

- **Data Integrity**: Đảm bảo dữ liệu đồng bộ giữa PostgreSQL, Redis và ElasticSearch
- **Redis Persistence**: Sử dụng RDB và AOF để đảm bảo dữ liệu không mất
- **ElasticSearch Mapping**: Cấu hình mapping tối ưu cho search
- **Transaction Support**: Sử dụng database transactions để đảm bảo consistency
- **Error Handling**: Xử lý lỗi và retry mechanism
- **Monitoring**: Health checks cho tất cả services

## Cấu trúc dự án

```
databaseProject/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── redis_client.py
│   │   ├── elasticsearch_client.py
│   │   ├── sync_service.py
│   │   └── api.py
│   ├── requirements.txt
│   └── main.py
├── docker-compose.yml
├── docker/
│   ├── postgres/
│   │   └── init.sql
│   ├── redis/
│   │   └── redis.conf
│   └── elasticsearch/
│       └── elasticsearch.yml
└── README.md
```

## Cách chạy

1. **Khởi động services:**
```bash
docker-compose up -d
```

2. **Chạy backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **Test API:**
```bash
# Tạo user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Tìm kiếm user
curl "http://localhost:8000/users/search?q=john"
```

## Data Integrity Strategy

1. **Write-Through Pattern**: Mọi write operation đều update cả 3 systems
2. **Transaction Rollback**: Nếu có lỗi, rollback tất cả changes
3. **Eventual Consistency**: Đảm bảo dữ liệu cuối cùng sẽ consistent
4. **Health Checks**: Kiểm tra trạng thái của tất cả services 


# Check postgres
docker-compose exec postgres psql -U postgres -d data_integrity_db -c "SELECT * FROM users;"

# Create user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Elasticsearch Test", "email": "es_test@example.com"}'


curl -X GET "localhost:9200/users/_search?q=john"

# Get from redis
docker-compose exec redis redis-cli GET user:1

# Sync data
docker-compose exec backend bash
python app/sync_all_to_elastic.py

---

## 🇻🇳 Hướng dẫn lấy toàn bộ user từ Redis

1. **Sau khi sync**, Redis sẽ bị xóa sạch cache (`redis_cleared: true`).
2. **Chỉ khi bạn truy cập API `/users/{id}`**, user đó mới được cache vào Redis.
3. **Muốn có tất cả user trong Redis**:
   - Lấy danh sách user từ API:
     ```bash
     curl -X GET http://localhost:8000/users
     ```
   - Lặp qua từng user_id, gọi:
     ```bash
     curl -X GET http://localhost:8000/users/1
     curl -X GET http://localhost:8000/users/2
     # ... cho đến hết
     ```
   - Kiểm tra lại Redis:
     ```bash
     docker-compose exec redis redis-cli KEYS "user:*"
     ```
     Ví dụ bạn vừa làm:
     ```
     1) "user:1"
     ```

4. **Nếu muốn tự động cache toàn bộ user vào Redis khi sync**, cần sửa code trong hàm sync để gọi `set_user` cho từng user.

---

## 🇬🇧 How to get all users from Redis

1. **After sync**, Redis cache is cleared (`redis_cleared: true`).
2. **Only when you access `/users/{id}`**, that user is cached in Redis.
3. **To have all users in Redis**:
   - Get all users:
     ```bash
     curl -X GET http://localhost:8000/users
     ```
   - For each user_id, call:
     ```bash
     curl -X GET http://localhost:8000/users/1
     curl -X GET http://localhost:8000/users/2
     # ... etc.
     ```
   - Check Redis:
     ```bash
     docker-compose exec redis redis-cli KEYS "user:*"
     ```
     Example result:
     ```
     1) "user:1"
     ```

4. **If you want to auto-cache all users in Redis during sync**, update the sync code to call `set_user` for each user.

---

Bạn cần tôi sửa code để khi sync sẽ tự động cache toàn bộ user vào Redis không?  
Do you want me to update the sync logic to auto-cache all users in Redis?
