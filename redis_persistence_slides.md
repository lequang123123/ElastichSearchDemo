# Redis Persistence Deep Dive
## Hiểu sâu về cơ chế lưu trữ dữ liệu bền vững trong Redis

---

## 🎯 **Tại sao cần Redis Persistence?**

### **Vấn đề cơ bản:**
```python
# Redis là in-memory database
redis_client.set("user:1", "John Doe")
# Dữ liệu chỉ lưu trong RAM
# Server restart → Dữ liệu mất hết! 😱
```

### **Giải pháp:**
```python
# Persistence = Lưu trữ dữ liệu xuống disk
# Khi restart → Dữ liệu được khôi phục ✅
```

### **Tại sao quan trọng?**
- 🚨 **Data Loss**: Không mất dữ liệu khi server crash
- 🔄 **Disaster Recovery**: Khôi phục từ backup
- 🏭 **Production Ready**: Đủ tin cậy cho production
- 💰 **Cost Effective**: Không cần rebuild cache từ đầu

---

## 📊 **Hai loại Persistence**

### **1. RDB (Redis Database) - Snapshot**

#### **Cách hoạt động:**
```bash
# redis.conf
save 900 1      # Save nếu ít nhất 1 key thay đổi trong 900 giây (15 phút)
save 300 10     # Save nếu ít nhất 10 keys thay đổi trong 300 giây (5 phút)
save 60 10000   # Save nếu ít nhất 10000 keys thay đổi trong 60 giây (1 phút)
```

#### **Ưu điểm:**
- ✅ **File nhỏ**: Nén tốt, tiết kiệm disk space
- ✅ **Backup nhanh**: Tạo snapshot nhanh chóng
- ✅ **Khôi phục nhanh**: Load RDB file nhanh hơn AOF
- ✅ **Performance**: Ít ảnh hưởng đến performance

#### **Nhược điểm:**
- ❌ **Data loss**: Có thể mất dữ liệu gần đây (vài phút)
- ❌ **Fork process**: Tạo child process khi save
- ❌ **Not real-time**: Không lưu từng operation

---

## 📊 **Hai loại Persistence (tiếp)**

### **2. AOF (Append Only File) - Operation Log**

#### **Cách hoạt động:**
```bash
# redis.conf
appendonly yes
appendfsync everysec  # Sync mỗi giây
# appendfsync always   # Sync ngay lập tức (chậm hơn)
# appendfsync no       # Không sync (nhanh nhất)
```

#### **File content:**
```bash
# appendonly.aof
SET user:1 "John Doe"
SET user:2 "Jane Smith"
DEL user:1
SET user:3 "Bob Johnson"
EXPIRE user:2 3600
```

#### **Ưu điểm:**
- ✅ **Durability**: Không mất dữ liệu
- ✅ **Replay**: Có thể replay từng operation
- ✅ **Real-time**: Lưu operation ngay lập tức
- ✅ **Debug**: Dễ debug và audit

#### **Nhược điểm:**
- ❌ **File lớn**: AOF file lớn hơn RDB
- ❌ **Khôi phục chậm**: Replay operations chậm
- ❌ **Performance impact**: Ảnh hưởng performance nhiều hơn

---

## 🔧 **Cấu hình hiện tại trong Project**

### **Redis Configuration:**
```bash
# docker/redis/redis.conf

# RDB Persistence
save 900 1      # 15 phút nếu 1 key thay đổi
save 300 10     # 5 phút nếu 10 keys thay đổi
save 60 10000   # 1 phút nếu 10000 keys thay đổi

# AOF Persistence
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Memory settings
maxmemory 256mb
maxmemory-policy allkeys-lru

# Data persistence directory
dir /data
```

### **File Structure:**
```bash
/data/
├── dump.rdb              # RDB snapshot file
├── appendonly.aof        # AOF log file (nếu dùng AOF cũ)
├── appendonlydir/        # AOF directory (Redis 7+)
│   ├── appendonly.aof.1.base.rdb
│   ├── appendonly.aof.1.incr.aof
│   └── appendonly.aof.manifest
└── redis.conf            # Configuration file
```

---

## 🔄 **Cơ chế hoạt động chi tiết**

### **Khi có operation mới:**
```python
# 1. Client gửi command
redis_client.set("user:1", "John Doe")

# 2. Redis thực hiện trong memory
# 3. Redis append vào AOF file (nếu enabled)
# 4. Redis check RDB conditions
# 5. Nếu đủ điều kiện → tạo RDB snapshot
```

### **Khi Redis restart:**
```python
# 1. Redis load AOF file trước (nếu có)
# 2. Replay tất cả operations từ AOF
# 3. Nếu AOF không có → load RDB file
# 4. Redis sẵn sàng phục vụ
```

### **Hybrid Approach:**
```python
# Sử dụng cả RDB và AOF
# RDB: Backup nhanh, khôi phục nhanh
# AOF: Durability, không mất dữ liệu
# Combined: Best of both worlds
```

---

## 🧪 **Demo: Test Persistence**

### **Bước 1: Tạo dữ liệu test**
```bash
# Set test data
docker-compose exec redis redis-cli SET "test:persistence" "Hello World"
docker-compose exec redis redis-cli SET "user:demo" "Demo User"
docker-compose exec redis redis-cli SET "counter" "100"
```

### **Bước 2: Kiểm tra dữ liệu**
```bash
# Verify data exists
docker-compose exec redis redis-cli GET "test:persistence"
docker-compose exec redis redis-cli KEYS "*"
```

### **Bước 3: Kiểm tra persistence files**
```bash
# Check RDB file
docker-compose exec redis ls -la /data/dump.rdb

# Check AOF files
docker-compose exec redis ls -la /data/appendonlydir/
```

### **Bước 4: Test restart**
```bash
# Restart Redis
docker restart redis_cache

# Verify data survives
docker-compose exec redis redis-cli GET "test:persistence"
```

---

## 📊 **So sánh RDB vs AOF**

| Aspect | RDB | AOF |
|--------|-----|-----|
| **File size** | Nhỏ (nén tốt) | Lớn hơn |
| **Recovery speed** | Nhanh | Chậm hơn |
| **Data loss** | Có thể mất vài phút | Không mất |
| **Performance impact** | Ít | Nhiều hơn |
| **File format** | Binary | Text |
| **Use case** | Backup, disaster recovery | Durability |
| **Memory usage** | Thấp | Cao hơn |
| **Network transfer** | Nhanh | Chậm |

---

## 🔍 **Monitoring Persistence**

### **Redis INFO command:**
```bash
# Check persistence status
docker-compose exec redis redis-cli INFO persistence
```

### **Key metrics:**
```bash
# RDB metrics
rdb_changes_since_last_save: 73
rdb_last_save_time: 1752224963
rdb_last_bgsave_status: ok

# AOF metrics
aof_enabled: 1
aof_current_size: 11341
aof_last_write_status: ok
```

### **Manual commands:**
```bash
# Force save RDB
docker-compose exec redis redis-cli BGSAVE

# Force rewrite AOF
docker-compose exec redis redis-cli BGREWRITEAOF

# Check save status
docker-compose exec redis redis-cli LASTSAVE
```

---

## ⚙️ **Cấu hình tối ưu**

### **Production Settings:**
```bash
# redis.conf cho production

# RDB - Backup strategy
save 900 1      # 15 phút
save 300 10     # 5 phút  
save 60 10000   # 1 phút

# AOF - Durability
appendonly yes
appendfsync everysec  # Cân bằng giữa performance và durability

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Performance
tcp-keepalive 300
timeout 0
```

### **Development Settings:**
```bash
# redis.conf cho development

# RDB - Ít frequent
save 3600 1     # 1 giờ
save 300 10     # 5 phút

# AOF - Disabled để tăng performance
appendonly no

# Memory
maxmemory 256mb
maxmemory-policy allkeys-lru
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **1. AOF file quá lớn:**
```bash
# Rewrite AOF file
docker-compose exec redis redis-cli BGREWRITEAOF

# Check AOF size
docker-compose exec redis redis-cli INFO persistence | grep aof_current_size
```

#### **2. RDB save thất bại:**
```bash
# Check disk space
docker-compose exec redis df -h

# Check permissions
docker-compose exec redis ls -la /data/

# Manual save
docker-compose exec redis redis-cli BGSAVE
```

#### **3. Recovery thất bại:**
```bash
# Check AOF file integrity
docker-compose exec redis redis-check-aof /data/appendonly.aof

# Check RDB file integrity  
docker-compose exec redis redis-check-rdb /data/dump.rdb
```

---

## 🎯 **Best Practices**

### **1. Hybrid Approach:**
```bash
# Sử dụng cả RDB và AOF
# RDB cho backup nhanh
# AOF cho durability
```

### **2. Backup Strategy:**
```bash
# Regular backups
# Test recovery process
# Monitor disk space
# Use different locations
```

### **3. Performance Tuning:**
```bash
# appendfsync everysec (cân bằng)
# Monitor AOF rewrite
# Tune save intervals
# Monitor memory usage
```

### **4. Monitoring:**
```bash
# Monitor persistence metrics
# Alert on failures
# Track recovery times
# Monitor disk usage
```

---

## 📈 **Performance Impact**

### **Without Persistence:**
```
Write operations: 100,000 ops/sec
Memory usage: 1GB
Disk usage: 0MB
Recovery time: N/A (no data)
```

### **With RDB only:**
```
Write operations: 95,000 ops/sec (-5%)
Memory usage: 1GB
Disk usage: 100MB
Recovery time: 2 seconds
```

### **With AOF only:**
```
Write operations: 80,000 ops/sec (-20%)
Memory usage: 1.2GB (+20%)
Disk usage: 500MB
Recovery time: 10 seconds
```

### **With RDB + AOF:**
```
Write operations: 75,000 ops/sec (-25%)
Memory usage: 1.2GB (+20%)
Disk usage: 600MB
Recovery time: 8 seconds
Data safety: Maximum
```

---

## 🔧 **Commands Reference**

### **Persistence Commands:**
```bash
# Save RDB
BGSAVE                    # Background save
SAVE                      # Blocking save

# AOF operations
BGREWRITEAOF             # Background rewrite AOF
AOF REWRITE              # Manual rewrite

# Monitoring
INFO persistence         # Persistence info
LASTSAVE                # Last save timestamp
MONITOR                 # Real-time monitoring
```

### **File Management:**
```bash
# Check files
ls -la /data/
redis-check-aof file.aof
redis-check-rdb file.rdb

# Backup
cp /data/dump.rdb /backup/
cp /data/appendonly.aof /backup/
```

---

## 🎯 **Kết luận**

### **Tại sao Redis Persistence quan trọng:**
- 🛡️ **Data Safety**: Bảo vệ dữ liệu khỏi mất mát
- 🔄 **Disaster Recovery**: Khôi phục từ backup
- 🏭 **Production Ready**: Đủ tin cậy cho production
- 📊 **Performance**: Cân bằng giữa speed và durability

### **Recommendations:**
- ✅ **Use Hybrid**: RDB + AOF cho production
- ✅ **Monitor**: Theo dõi persistence metrics
- ✅ **Backup**: Backup thường xuyên
- ✅ **Test**: Test recovery process

### **Next Steps:**
- 🔧 Tune configuration cho workload
- 📊 Set up monitoring và alerting
- 🧪 Test disaster recovery
- 📚 Document procedures

---

## ❓ **Q&A**

### **Câu hỏi thường gặp:**

**Q: Có nên disable persistence để tăng performance?**
A: Chỉ trong development. Production luôn cần persistence.

**Q: AOF hay RDB tốt hơn?**
A: Dùng cả hai. RDB cho backup, AOF cho durability.

**Q: Làm sao giảm AOF file size?**
A: Sử dụng BGREWRITEAOF định kỳ.

**Q: Recovery mất bao lâu?**
A: RDB: 2-5 giây, AOF: 10-30 giây tùy data size. 