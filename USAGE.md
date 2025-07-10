# Hướng dẫn sử dụng Data Integrity Project

## 🚀 Khởi động dự án

### 1. Khởi động tất cả services
```bash
docker-compose up -d
```

### 2. Kiểm tra trạng thái services
```bash
docker-compose ps
```

### 3. Chạy backend (nếu không dùng Docker)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 📊 Kiểm tra services

### PostgreSQL
```bash
# Kết nối database
docker exec -it postgres_db psql -U postgres -d data_integrity_db

# Kiểm tra tables
\dt

# Xem dữ liệu
SELECT * FROM users;
SELECT * FROM sync_log;
```

### Redis
```bash
# Kết nối Redis CLI
docker exec -it redis_cache redis-cli

# Kiểm tra keys
KEYS *

# Xem thông tin cache
INFO memory
INFO stats
```

### Elasticsearch
```bash
# Kiểm tra cluster health
curl http://localhost:9200/_cluster/health

# Xem indices
curl http://localhost:9200/_cat/indices

# Tìm kiếm users
curl "http://localhost:9200/users/_search?q=alice"
```

## 🔧 API Endpoints

### Health Check
```bash
# Kiểm tra sức khỏe tất cả services
curl http://localhost:8000/health

# Chi tiết thống kê
curl http://localhost:8000/health/detailed
```

### User Management
```bash
# Tạo user mới
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Lấy user theo ID (với cache)
curl http://localhost:8000/users/1

# Cập nhật user
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated"}'

# Xóa user
curl -X DELETE http://localhost:8000/users/1

# Tìm kiếm users
curl "http://localhost:8000/users/search?q=john"

# Danh sách users
curl http://localhost:8000/users
```

### Product Management
```bash
# Tạo product mới
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "High performance", "price": 999.99, "category": "Electronics"}'

# Lấy product theo ID
curl http://localhost:8000/products/1

# Tìm kiếm products
curl "http://localhost:8000/products/search?q=laptop"
```

### Cache Management
```bash
# Thống kê cache
curl http://localhost:8000/cache/stats

# Xóa cache của user
curl -X DELETE http://localhost:8000/cache/users/1
```

### Sync Status
```bash
# Thống kê đồng bộ
curl http://localhost:8000/sync/status

# Retry failed syncs
curl http://localhost:8000/sync/retry-failed
```

## 🧪 Chạy tests

```bash
# Chạy test script
python test_api.py
```

## 📈 Monitoring

### Redis Persistence
- **RDB**: Lưu snapshot theo thời gian
- **AOF**: Lưu tất cả commands
- **Dual persistence**: Kết hợp cả hai

### Elasticsearch Mapping
- **Users index**: Tối ưu cho search name và email
- **Products index**: Tối ưu cho search name, description, category

### Data Integrity Strategy
1. **Write-Through**: Mọi write đều update cả 3 systems
2. **Transaction Rollback**: Nếu lỗi, rollback tất cả
3. **Sync Logging**: Track tất cả sync operations
4. **Retry Mechanism**: Tự động retry failed syncs

## 🔍 Debug

### Logs
```bash
# Backend logs
docker-compose logs backend

# PostgreSQL logs
docker-compose logs postgres

# Redis logs
docker-compose logs redis

# Elasticsearch logs
docker-compose logs elasticsearch
```

### Database Queries
```sql
-- Xem sync log
SELECT * FROM sync_log ORDER BY created_at DESC;

-- Xem failed syncs
SELECT * FROM sync_log WHERE sync_status = 'FAILED';

-- Thống kê sync
SELECT 
    sync_status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
FROM sync_log 
GROUP BY sync_status;
```

### Redis Commands
```bash
# Xem tất cả keys
KEYS *

# Xem user cache
GET user:1

# Xem cache stats
INFO memory
INFO stats
```

### Elasticsearch Queries
```bash
# Search users
curl -X GET "localhost:9200/users/_search" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match": {"name": "john"}}}'

# Search products
curl -X GET "localhost:9200/products/_search" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match": {"name": "laptop"}}}'
```

## 🛠️ Troubleshooting

### Common Issues

1. **Redis connection failed**
   - Kiểm tra Redis container đã start chưa
   - Kiểm tra port 6379 có bị conflict không

2. **Elasticsearch not responding**
   - Kiểm tra memory usage
   - Restart Elasticsearch container

3. **Database connection failed**
   - Kiểm tra PostgreSQL container
   - Kiểm tra credentials trong docker-compose.yml

4. **Sync failures**
   - Xem sync_log table
   - Kiểm tra network connectivity giữa containers

### Performance Tuning

1. **Redis Cache**
   - Tăng maxmemory nếu cần
   - Điều chỉnh TTL cho keys

2. **Elasticsearch**
   - Tăng heap size nếu cần
   - Optimize mappings

3. **Database**
   - Tăng connection pool size
   - Add indexes cho frequently queried columns 