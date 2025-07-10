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