# 🚀 Performance Testing Guide
## Hướng Dẫn Chạy Performance Test với JMeter và Docker

### 📋 Mục Lục
1. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
2. [Chuẩn Bị](#chuẩn-bị)
3. [Chạy Performance Test](#chạy-performance-test)
4. [Phân Tích Kết Quả](#phân-tích-kết-quả)
5. [Tùy Chỉnh Test](#tùy-chỉnh-test)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ Yêu Cầu Hệ Thống

### Bắt Buộc
- Docker và Docker Compose
- 4GB RAM trở lên
- 2GB disk space

### Tùy Chọn
- Python 3.10+ (để phân tích kết quả)
- Git

---

## ⚙️ Chuẩn Bị

### 1. Kiểm Tra Hệ Thống
```bash
# Kiểm tra Docker
docker --version
docker-compose --version

# Kiểm tra hệ thống đang chạy
docker-compose ps
```

### 2. Đảm Bảo Backend Đang Hoạt Động
```bash
# Khởi động hệ thống nếu chưa chạy
docker-compose up -d

# Kiểm tra health check
curl http://localhost:8000/health
```

### 3. Tạo Thư Mục Kết Quả
```bash
mkdir -p performance_results_real
```

---

## 🏃‍♂️ Chạy Performance Test

### Bước 1: Chạy Test Cơ Bản
```bash
# Xóa kết quả cũ (nếu có)
rm -rf performance_results_real/*

# Chạy JMeter test với Docker
docker run --rm \
  -v $(pwd)/simple_jmeter_test.jmx:/jmeter/simple_jmeter_test.jmx \
  -v $(pwd)/performance_results_real:/jmeter/results \
  jmeter-performance \
  jmeter -n -t simple_jmeter_test.jmx \
  -l results/jmeter_results.jtl \
  -e -o results/html_report
```

### Bước 2: Kiểm Tra Kết Quả
```bash
# Xem kết quả JTL
cat performance_results_real/jmeter_results.jtl

# Xem thống kê
cat performance_results_real/html_report/statistics.json

# Mở HTML report (nếu có browser)
open performance_results_real/html_report/index.html
```

### Bước 3: Phân Tích Chi Tiết
```bash
# Chạy script phân tích bằng Docker
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  python:3.10-slim \
  bash -c "pip install pandas matplotlib seaborn numpy && python analyze_performance.py"
```

---

## 📊 Phân Tích Kết Quả

### 1. Kết Quả Cơ Bản
- **JTL File**: `performance_results_real/jmeter_results.jtl`
- **HTML Report**: `performance_results_real/html_report/index.html`
- **Statistics**: `performance_results_real/html_report/statistics.json`

### 2. Báo Cáo Chi Tiết
- **Markdown Report**: `performance_report.md`
- **Charts**: `performance_charts/performance_overview.png`
- **Detailed Analysis**: `performance_charts/detailed_analysis.png`

### 3. Các Chỉ Số Quan Trọng
- **Response Time**: Thời gian phản hồi trung bình
- **Throughput**: Số requests/giây
- **Success Rate**: Tỷ lệ thành công
- **Error Rate**: Tỷ lệ lỗi

---

## ⚙️ Tùy Chỉnh Test

### 1. Thay Đổi Thông Số Test
Chỉnh sửa file `simple_jmeter_test.jmx`:

```xml
<!-- Thay đổi số threads -->
<stringProp name="ThreadGroup.num_threads">10</stringProp>

<!-- Thay đổi ramp-up time -->
<stringProp name="ThreadGroup.ramp_time">5</stringProp>

<!-- Thay đổi số lần lặp -->
<stringProp name="LoopController.loops">5</stringProp>
```

### 2. Thêm Endpoint Mới
```xml
<HTTPSamplerProxy testname="New Endpoint">
  <stringProp name="HTTPSampler.domain">host.docker.internal</stringProp>
  <stringProp name="HTTPSampler.port">8000</stringProp>
  <stringProp name="HTTPSampler.path">/new-endpoint</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
</HTTPSamplerProxy>
```

### 3. Test Với Tải Cao
```bash
# Test với 50 threads, 10 giây ramp-up, 10 lần lặp
docker run --rm \
  -v $(pwd)/simple_jmeter_test.jmx:/jmeter/simple_jmeter_test.jmx \
  -v $(pwd)/performance_results_real:/jmeter/results \
  jmeter-performance \
  jmeter -n -t simple_jmeter_test.jmx \
  -l results/jmeter_results.jtl \
  -e -o results/html_report \
  -JTHREAD_COUNT=50 \
  -JRAMP_UP=10 \
  -JLOOP_COUNT=10
```

---

## 🔧 Troubleshooting

### 1. Lỗi Kết Nối
```bash
# Kiểm tra backend có hoạt động không
curl http://localhost:8000/health

# Kiểm tra từ Docker container
docker run --rm curlimages/curl:latest curl http://host.docker.internal:8000/health
```

### 2. Lỗi JMeter
```bash
# Xóa kết quả cũ
rm -rf performance_results_real/*

# Chạy với debug logging
docker run --rm \
  -v $(pwd)/simple_jmeter_test.jmx:/jmeter/simple_jmeter_test.jmx \
  -v $(pwd)/performance_results_real:/jmeter/results \
  jmeter-performance \
  jmeter -n -t simple_jmeter_test.jmx \
  -l results/jmeter_results.jtl \
  -e -o results/html_report \
  -L DEBUG
```

### 3. Lỗi Phân Tích
```bash
# Kiểm tra file kết quả
ls -la performance_results_real/

# Chạy phân tích với debug
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  python:3.10-slim \
  bash -c "pip install pandas matplotlib seaborn numpy && python -c 'import analyze_performance; analyze_performance.main()'"
```

### 4. Lỗi Memory
```bash
# Tăng memory cho Docker
docker run --rm \
  -m 2g \
  -v $(pwd)/simple_jmeter_test.jmx:/jmeter/simple_jmeter_test.jmx \
  -v $(pwd)/performance_results_real:/jmeter/results \
  jmeter-performance \
  jmeter -n -t simple_jmeter_test.jmx \
  -l results/jmeter_results.jtl \
  -e -o results/html_report
```

---

## 📈 Ví Dụ Kết Quả

### Kết Quả Tốt
```
📊 PERFORMANCE ANALYSIS REPORT
============================================================

📈 OVERALL METRICS:
   Total Requests: 45
   Successful: 45
   Failed: 0
   Success Rate: 100.00%

⏱️  RESPONSE TIME ANALYSIS:
   Average Response Time: 17.16 ms
   Median Response Time: 10.00 ms
   Min Response Time: 2.00 ms
   Max Response Time: 111.00 ms

🚀 THROUGHPUT ANALYSIS:
   Total Test Duration: 1.59 seconds
   Requests per Second: 28.28 req/s
```

### Cần Cải Thiện
- Response time > 1000ms
- Success rate < 95%
- Error rate > 5%
- Throughput < 10 req/s

---

## 🎯 Best Practices

### 1. Trước Khi Test
- ✅ Đảm bảo backend hoạt động ổn định
- ✅ Xóa cache nếu cần
- ✅ Backup dữ liệu quan trọng
- ✅ Kiểm tra tài nguyên hệ thống

### 2. Trong Khi Test
- 📊 Monitor CPU, Memory, Disk I/O
- 📊 Kiểm tra logs của backend
- 📊 Theo dõi database performance
- 📊 Monitor network traffic

### 3. Sau Khi Test
- 📈 Phân tích kết quả chi tiết
- 📈 So sánh với baseline
- 📈 Tìm bottleneck
- 📈 Đề xuất cải thiện

---

## 🔄 Workflow Hoàn Chỉnh

```bash
# 1. Chuẩn bị
docker-compose up -d
curl http://localhost:8000/health

# 2. Chạy test
rm -rf performance_results_real/*
docker run --rm \
  -v $(pwd)/simple_jmeter_test.jmx:/jmeter/simple_jmeter_test.jmx \
  -v $(pwd)/performance_results_real:/jmeter/results \
  jmeter-performance \
  jmeter -n -t simple_jmeter_test.jmx \
  -l results/jmeter_results.jtl \
  -e -o results/html_report

# 3. Phân tích
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  python:3.10-slim \
  bash -c "pip install pandas matplotlib seaborn numpy && python analyze_performance.py"

# 4. Xem kết quả
cat performance_report.md
open performance_charts/performance_overview.png
```

---

## 📞 Hỗ Trợ

### Lỗi Thường Gặp
1. **Backend không khả dụng**: Kiểm tra `docker-compose ps`
2. **JMeter không kết nối được**: Kiểm tra network và firewall
3. **Kết quả rỗng**: Xóa file cũ và chạy lại
4. **Memory error**: Tăng memory cho Docker container

### Liên Hệ
- Tạo issue trên GitHub
- Kiểm tra logs: `docker-compose logs backend`
- Debug với verbose mode

---

*Hướng dẫn này được tạo cho hệ thống Redis + Elasticsearch + PostgreSQL*
*Cập nhật lần cuối: 2025-07-11* 