# 🚀 JMeter Performance Testing với Docker

Hướng dẫn chạy performance test cho hệ thống Redis, Elasticsearch, PostgreSQL sử dụng JMeter trong Docker.

## 📋 Yêu cầu

- Docker Desktop đã cài đặt và chạy
- Python 3.8+ với các thư viện: `requests`, `matplotlib`, `pandas`
- Hệ thống backend đang chạy trên `http://localhost:8000`

## 🛠️ Cài đặt

1. **Cài đặt Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Kiểm tra Docker:**
```bash
docker --version
```

## 🚀 Chạy Performance Test

### Cách 1: Sử dụng script Python (Khuyến nghị)

```bash
# Chạy với cấu hình mặc định
python run_jmeter_docker.py

# Chạy với cấu hình tùy chỉnh
python run_jmeter_docker.py --threads 100 --ramp-up 20 --loops 20 --url http://localhost:8000
```

### Cách 2: Sử dụng Docker Compose

```bash
# Build và chạy JMeter test
docker-compose -f docker-compose.jmeter.yml up --build
```

### Cách 3: Chạy JMeter trực tiếp

```bash
# Build JMeter image
docker build -f Dockerfile.jmeter -t jmeter-performance .

# Chạy test
docker run --rm \
  -v $(pwd)/jmeter_test_plan.jmx:/jmeter/jmeter_test_plan.jmx \
  -v $(pwd)/performance_results:/jmeter/results \
  -e BASE_URL=http://host.docker.internal:8000 \
  -e THREAD_COUNT=50 \
  -e RAMP_UP=10 \
  -e LOOP_COUNT=10 \
  jmeter-performance \
  jmeter -n -t jmeter_test_plan.jmx \
  -l results/jmeter_results.jtl \
  -e -o results/html_report \
  -JTHREAD_COUNT=50 \
  -JRAMP_UP=10 \
  -JLOOP_COUNT=10 \
  -JBASE_URL=http://host.docker.internal:8000
```

## 📊 Kết quả Test

Sau khi chạy test, bạn sẽ có các file sau trong thư mục `performance_results_YYYYMMDD_HHMMSS/`:

### 📁 Files được tạo:

1. **`jmeter_results.jtl`** - Raw JMeter results
2. **`html_report/`** - HTML report chi tiết từ JMeter
3. **`performance_report.json`** - JSON report với metrics
4. **`performance_charts.png`** - Biểu đồ performance

### 📈 Metrics được đo:

- **Tổng quan:**
  - Tổng số requests
  - Requests thành công/thất bại
  - Tỷ lệ thành công (%)
  - Thời gian test (giây)
  - Throughput (requests/giây)

- **Response Time:**
  - Trung bình (ms)
  - Min/Max (ms)
  - P95 (95th percentile)
  - P99 (99th percentile)

- **Performance theo Endpoint:**
  - User Registration
  - User Login
  - Get All Users
  - Search Users
  - Health Check

## 🔧 Cấu hình Test

### JMeter Test Plan (`jmeter_test_plan.jmx`)

Test plan bao gồm 5 Thread Groups:

1. **User Registration Test** - Test đăng ký user
2. **User Login Test** - Test đăng nhập
3. **Get Users Test** - Test lấy danh sách users
4. **Search Users Test** - Test tìm kiếm users
5. **Health Check Test** - Test health check

### Parameters có thể tùy chỉnh:

- `THREAD_COUNT`: Số lượng concurrent users (mặc định: 50)
- `RAMP_UP`: Thời gian tăng dần users (giây, mặc định: 10)
- `LOOP_COUNT`: Số lần lặp test (mặc định: 10)
- `BASE_URL`: URL của API (mặc định: http://localhost:8000)

## 📊 Đọc Report

### 1. HTML Report (JMeter)

Mở file `html_report/index.html` trong browser để xem:
- Summary report
- Response time distribution
- Throughput graph
- Error analysis

### 2. JSON Report

File `performance_report.json` chứa:
```json
{
  "test_summary": {
    "total_requests": 2500,
    "successful_requests": 2450,
    "failed_requests": 50,
    "success_rate_percent": 98.0,
    "total_test_time_seconds": 120.5,
    "throughput_rps": 20.75
  },
  "response_time_stats": {
    "average_ms": 45.2,
    "minimum_ms": 12,
    "maximum_ms": 890,
    "p95_ms": 120.5,
    "p99_ms": 250.8
  },
  "endpoint_performance": {
    "Register User": {
      "requests": 500,
      "success_rate_percent": 98.5,
      "average_response_time_ms": 65.2
    }
  }
}
```

### 3. Biểu đồ Performance

File `performance_charts.png` hiển thị:
- Phân phối response time
- Response time theo endpoint
- Success rate theo endpoint
- Response time theo thời gian

## 🎯 Benchmark Scenarios

### 1. Light Load Test
```bash
python run_jmeter_docker.py --threads 10 --ramp-up 5 --loops 5
```

### 2. Medium Load Test
```bash
python run_jmeter_docker.py --threads 50 --ramp-up 10 --loops 10
```

### 3. Heavy Load Test
```bash
python run_jmeter_docker.py --threads 100 --ramp-up 20 --loops 20
```

### 4. Stress Test
```bash
python run_jmeter_docker.py --threads 200 --ramp-up 30 --loops 30
```

## 🔍 Troubleshooting

### Lỗi thường gặp:

1. **Docker không chạy:**
   ```bash
   # Khởi động Docker Desktop
   # Kiểm tra: docker --version
   ```

2. **Backend không accessible:**
   ```bash
   # Kiểm tra backend đang chạy
   curl http://localhost:8000/health
   ```

3. **Port conflict:**
   ```bash
   # Kiểm tra port 8000
   lsof -i :8000
   ```

4. **Memory issues:**
   ```bash
   # Giảm số threads
   python run_jmeter_docker.py --threads 20
   ```

### Performance Tips:

1. **Tăng performance:**
   - Sử dụng SSD cho storage
   - Tăng Docker memory limit
   - Chạy test trên máy mạnh

2. **Giảm resource usage:**
   - Giảm số threads
   - Tăng ramp-up time
   - Giảm loop count

## 📝 Customization

### Thêm endpoint mới:

1. Mở `jmeter_test_plan.jmx` trong JMeter GUI
2. Thêm HTTP Request Sampler
3. Cấu hình endpoint và parameters
4. Save và chạy lại test

### Tùy chỉnh metrics:

1. Sửa file `run_jmeter_docker.py`
2. Thêm metrics mới trong `analyze_results()`
3. Cập nhật chart generation

## 🎉 Kết luận

Performance test này giúp bạn:

- ✅ Đo lường performance của hệ thống
- ✅ Xác định bottlenecks
- ✅ Validate scalability
- ✅ Tạo baseline cho optimization
- ✅ Generate professional reports

Sử dụng kết quả để optimize hệ thống và đảm bảo performance trong production! 