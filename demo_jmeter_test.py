#!/usr/bin/env python3
"""
Demo JMeter Performance Test
Tạo mock data và demo performance testing workflow
"""

import json
import os
import subprocess
from datetime import datetime
import random

def create_mock_jmeter_results():
    """Tạo mock JMeter results để demo"""
    print("🎭 Tạo mock JMeter results để demo...")
    
    # Tạo thư mục results
    results_dir = f"demo_performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(results_dir, exist_ok=True)
    
    # Mock JMeter results
    mock_results = []
    base_timestamp = int(datetime.now().timestamp() * 1000)
    
    endpoints = [
        "Register User",
        "Login User", 
        "Get All Users",
        "Search Users",
        "Health Check"
    ]
    
    # Tạo 500 mock requests
    for i in range(500):
        endpoint = random.choice(endpoints)
        
        # Simulate different response times based on endpoint
        if endpoint == "Register User":
            elapsed = random.randint(80, 200)
        elif endpoint == "Login User":
            elapsed = random.randint(50, 150)
        elif endpoint == "Get All Users":
            elapsed = random.randint(30, 100)
        elif endpoint == "Search Users":
            elapsed = random.randint(40, 120)
        else:  # Health Check
            elapsed = random.randint(10, 50)
        
        # Simulate some failures
        success = random.random() > 0.05  # 95% success rate
        
        mock_results.append({
            'timestamp': base_timestamp + (i * 1000),
            'elapsed': elapsed,
            'label': endpoint,
            'response_code': '200' if success else '500',
            'response_message': 'OK' if success else 'Internal Server Error',
            'thread_name': f'Thread Group 1-{random.randint(1, 50)}',
            'success': success,
            'bytes': random.randint(100, 2000),
            'sent_bytes': random.randint(50, 500)
        })
    
    # Write to CSV format (JMeter format)
    csv_file = f"{results_dir}/jmeter_results.jtl"
    with open(csv_file, 'w') as f:
        f.write("timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect\n")
        
        for result in mock_results:
            f.write(f"{result['timestamp']},{result['elapsed']},{result['label']},{result['response_code']},{result['response_message']},{result['thread_name']},text,{str(result['success']).lower()},,{result['bytes']},{result['sent_bytes']},1,50,http://localhost:8000,{result['elapsed']},0,0\n")
    
    print(f"✅ Mock results created: {csv_file}")
    return results_dir, csv_file

def analyze_mock_results(results_dir, csv_file):
    """Phân tích mock results"""
    print("📊 Phân tích mock results...")
    
    # Đọc results
    results = []
    with open(csv_file, 'r') as f:
        for line in f:
            if line.startswith('timeStamp'):
                continue
            parts = line.strip().split(',')
            if len(parts) >= 10:
                results.append({
                    'timestamp': int(parts[0]),
                    'elapsed': int(parts[1]),
                    'label': parts[2],
                    'response_code': parts[3],
                    'success': parts[7] == 'true'
                })
    
    # Tính toán metrics
    total_requests = len(results)
    successful_requests = len([r for r in results if r['success']])
    failed_requests = total_requests - successful_requests
    success_rate = (successful_requests / total_requests) * 100
    
    # Response time statistics
    elapsed_times = [r['elapsed'] for r in results]
    avg_response_time = sum(elapsed_times) / len(elapsed_times)
    min_response_time = min(elapsed_times)
    max_response_time = max(elapsed_times)
    
    # Calculate percentiles
    sorted_times = sorted(elapsed_times)
    p95_index = int(len(sorted_times) * 0.95)
    p99_index = int(len(sorted_times) * 0.99)
    p95_response_time = sorted_times[p95_index]
    p99_response_time = sorted_times[p99_index]
    
    # Throughput
    total_time = (results[-1]['timestamp'] - results[0]['timestamp']) / 1000
    throughput = total_requests / total_time if total_time > 0 else 0
    
    # Tạo report
    report = {
        "test_summary": {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate_percent": round(success_rate, 2),
            "total_test_time_seconds": round(total_time, 2),
            "throughput_rps": round(throughput, 2)
        },
        "response_time_stats": {
            "average_ms": round(avg_response_time, 2),
            "minimum_ms": min_response_time,
            "maximum_ms": max_response_time,
            "p95_ms": p95_response_time,
            "p99_ms": p99_response_time
        },
        "endpoint_performance": {}
    }
    
    # Phân tích theo endpoint
    endpoints = {}
    for result in results:
        endpoint = result['label']
        if endpoint not in endpoints:
            endpoints[endpoint] = []
        endpoints[endpoint].append(result)
    
    for endpoint, endpoint_results in endpoints.items():
        endpoint_success_rate = (len([r for r in endpoint_results if r['success']]) / len(endpoint_results)) * 100
        endpoint_times = [r['elapsed'] for r in endpoint_results]
        endpoint_avg_time = sum(endpoint_times) / len(endpoint_times)
        
        report["endpoint_performance"][endpoint] = {
            "requests": len(endpoint_results),
            "success_rate_percent": round(endpoint_success_rate, 2),
            "average_response_time_ms": round(endpoint_avg_time, 2),
            "min_response_time_ms": min(endpoint_times),
            "max_response_time_ms": max(endpoint_times)
        }
    
    # Lưu report
    report_file = f"{results_dir}/performance_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report created: {report_file}")
    return report

def print_demo_summary(report, results_dir):
    """In demo summary"""
    print("\n" + "="*60)
    print("🎭 DEMO PERFORMANCE TEST SUMMARY")
    print("="*60)
    
    summary = report["test_summary"]
    print(f"📈 Tổng quan:")
    print(f"   • Tổng requests: {summary['total_requests']:,}")
    print(f"   • Requests thành công: {summary['successful_requests']:,}")
    print(f"   • Requests thất bại: {summary['failed_requests']:,}")
    print(f"   • Tỷ lệ thành công: {summary['success_rate_percent']}%")
    print(f"   • Thời gian test: {summary['total_test_time_seconds']}s")
    print(f"   • Throughput: {summary['throughput_rps']} requests/giây")
    
    print(f"\n⏱️  Response Time:")
    stats = report["response_time_stats"]
    print(f"   • Trung bình: {stats['average_ms']}ms")
    print(f"   • Min: {stats['minimum_ms']}ms")
    print(f"   • Max: {stats['maximum_ms']}ms")
    print(f"   • P95: {stats['p95_ms']}ms")
    print(f"   • P99: {stats['p99_ms']}ms")
    
    print(f"\n🔗 Performance theo Endpoint:")
    for endpoint, perf in report["endpoint_performance"].items():
        print(f"   • {endpoint}:")
        print(f"     - Requests: {perf['requests']}")
        print(f"     - Success Rate: {perf['success_rate_percent']}%")
        print(f"     - Avg Response Time: {perf['average_response_time_ms']}ms")
    
    print(f"\n📁 Files được tạo:")
    print(f"   • JMeter Results: {results_dir}/jmeter_results.jtl")
    print(f"   • JSON Report: {results_dir}/performance_report.json")
    
    print("="*60)

def create_demo_instructions():
    """Tạo hướng dẫn demo"""
    print("\n📋 HƯỚNG DẪN CHẠY JMETER PERFORMANCE TEST THỰC TẾ:")
    print("="*60)
    print("1. Đảm bảo backend đang chạy và khỏe:")
    print("   curl http://localhost:8000/health")
    print()
    print("2. Build JMeter Docker image:")
    print("   docker build -f Dockerfile.jmeter -t jmeter-performance .")
    print()
    print("3. Chạy JMeter test:")
    print("   docker run --rm \\")
    print("     -v $(pwd)/jmeter_test_plan.jmx:/jmeter/jmeter_test_plan.jmx \\")
    print("     -v $(pwd)/performance_results:/jmeter/results \\")
    print("     -e BASE_URL=http://host.docker.internal:8000 \\")
    print("     jmeter-performance \\")
    print("     jmeter -n -t jmeter_test_plan.jmx \\")
    print("     -l results/jmeter_results.jtl \\")
    print("     -e -o results/html_report \\")
    print("     -JTHREAD_COUNT=50 \\")
    print("     -JRAMP_UP=10 \\")
    print("     -JLOOP_COUNT=10 \\")
    print("     -JBASE_URL=http://host.docker.internal:8000")
    print()
    print("4. Phân tích kết quả:")
    print("   - Mở results/html_report/index.html")
    print("   - Xem performance_report.json")
    print("   - Kiểm tra biểu đồ performance")
    print()
    print("5. Các scenarios test:")
    print("   - Light Load: 10 threads, 5 loops")
    print("   - Medium Load: 50 threads, 10 loops") 
    print("   - Heavy Load: 100 threads, 20 loops")
    print("   - Stress Test: 200 threads, 30 loops")
    print("="*60)

def main():
    print("🎭 JMeter Performance Test Demo")
    print("Tạo mock data để demo performance testing workflow")
    print()
    
    # Tạo mock results
    results_dir, csv_file = create_mock_jmeter_results()
    
    # Phân tích results
    report = analyze_mock_results(results_dir, csv_file)
    
    # In summary
    print_demo_summary(report, results_dir)
    
    # Tạo hướng dẫn
    create_demo_instructions()
    
    print(f"\n🎉 Demo hoàn thành! Kết quả trong thư mục: {results_dir}")

if __name__ == "__main__":
    main() 