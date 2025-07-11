#!/usr/bin/env python3
"""
JMeter Performance Test Script với Docker
Chạy JMeter trong container và tạo report chi tiết
"""

import subprocess
import os
import sys
import time
import json
import argparse
from datetime import datetime
import requests
import matplotlib.pyplot as plt
import pandas as pd

class JMeterDockerTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results_dir = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.jmeter_results = f"{self.results_dir}/jmeter_results.jtl"
        self.html_report = f"{self.results_dir}/html_report"
        
    def check_system_health(self):
        """Kiểm tra hệ thống trước khi test"""
        print("🔍 Kiểm tra hệ thống...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Hệ thống hoạt động bình thường")
                print(f"   PostgreSQL: {health_data.get('postgresql', 'Unknown')}")
                print(f"   Redis: {health_data.get('redis', 'Unknown')}")
                print(f"   Elasticsearch: {health_data.get('elasticsearch', 'Unknown')}")
                return True
            else:
                print(f"❌ Hệ thống không khỏe: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Không thể kết nối hệ thống: {e}")
            return False
    
    def create_test_data(self):
        """Tạo dữ liệu test cơ bản"""
        print("📝 Tạo dữ liệu test...")
        
        # Tạo 10 users test
        for i in range(10):
            user_data = {
                "username": f"testuser_{i}",
                "email": f"testuser_{i}@example.com",
                "password": "password123"
            }
            
            try:
                response = requests.post(f"{self.base_url}/users/", json=user_data)
                if response.status_code in [200, 201]:
                    print(f"   ✅ Tạo user {i+1}/10")
                else:
                    print(f"   ⚠️  Lỗi tạo user {i+1}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Lỗi tạo user {i+1}: {e}")
    
    def build_jmeter_image(self):
        """Build JMeter Docker image"""
        print("🔨 Building JMeter Docker image...")
        
        try:
            result = subprocess.run([
                "docker", "build", 
                "-f", "Dockerfile.jmeter", 
                "-t", "jmeter-performance", 
                "."
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ JMeter image built successfully")
                return True
            else:
                print(f"❌ Build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def run_jmeter_test(self, threads=50, ramp_up=10, loops=10):
        """Chạy JMeter test trong Docker"""
        print(f"🚀 Chạy JMeter test với {threads} threads, {ramp_up}s ramp-up, {loops} loops...")
        
        # Tạo thư mục results
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Cập nhật environment variables
        env_vars = {
            "BASE_URL": self.base_url,
            "THREAD_COUNT": str(threads),
            "RAMP_UP": str(ramp_up),
            "LOOP_COUNT": str(loops)
        }
        
        # Chạy JMeter container
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.abspath('jmeter_test_plan.jmx')}:/jmeter/jmeter_test_plan.jmx",
            "-v", f"{os.path.abspath(self.results_dir)}:/jmeter/results",
            "-e", f"BASE_URL={env_vars['BASE_URL']}",
            "-e", f"THREAD_COUNT={env_vars['THREAD_COUNT']}",
            "-e", f"RAMP_UP={env_vars['RAMP_UP']}",
            "-e", f"LOOP_COUNT={env_vars['LOOP_COUNT']}",
            "jmeter-performance",
            "jmeter", "-n", "-t", "jmeter_test_plan.jmx",
            "-l", "results/jmeter_results.jtl",
            "-e", "-o", "results/html_report",
            "-JTHREAD_COUNT=" + env_vars['THREAD_COUNT'],
            "-JRAMP_UP=" + env_vars['RAMP_UP'],
            "-JLOOP_COUNT=" + env_vars['LOOP_COUNT'],
            "-JBASE_URL=" + env_vars['BASE_URL']
        ]
        
        try:
            print("   Chạy lệnh:", " ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("✅ JMeter test hoàn thành thành công")
                print("   Output:", result.stdout)
                return True
            else:
                print(f"❌ JMeter test thất bại: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ JMeter test timeout")
            return False
        except Exception as e:
            print(f"❌ JMeter test error: {e}")
            return False
    
    def analyze_results(self):
        """Phân tích kết quả test"""
        print("📊 Phân tích kết quả...")
        
        if not os.path.exists(self.jmeter_results):
            print("❌ Không tìm thấy file kết quả JMeter")
            return
        
        # Đọc kết quả JMeter
        results = []
        with open(self.jmeter_results, 'r') as f:
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
                        'response_message': parts[4],
                        'thread_name': parts[5],
                        'success': parts[7] == 'true',
                        'bytes': int(parts[8]) if parts[8].isdigit() else 0,
                        'sent_bytes': int(parts[9]) if parts[9].isdigit() else 0
                    })
        
        if not results:
            print("❌ Không có dữ liệu kết quả")
            return
        
        # Tạo DataFrame
        df = pd.DataFrame(results)
        
        # Tính toán metrics
        total_requests = len(df)
        successful_requests = len(df[df['success'] == True])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        # Response time statistics
        avg_response_time = df['elapsed'].mean()
        min_response_time = df['elapsed'].min()
        max_response_time = df['elapsed'].max()
        p95_response_time = df['elapsed'].quantile(0.95)
        p99_response_time = df['elapsed'].quantile(0.99)
        
        # Throughput (requests per second)
        total_time = (df['timestamp'].max() - df['timestamp'].min()) / 1000
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
                "p95_ms": round(p95_response_time, 2),
                "p99_ms": round(p99_response_time, 2)
            },
            "endpoint_performance": {}
        }
        
        # Phân tích theo endpoint
        for endpoint in df['label'].unique():
            endpoint_df = df[df['label'] == endpoint]
            endpoint_success_rate = (len(endpoint_df[endpoint_df['success'] == True]) / len(endpoint_df)) * 100
            endpoint_avg_time = endpoint_df['elapsed'].mean()
            
            report["endpoint_performance"][endpoint] = {
                "requests": len(endpoint_df),
                "success_rate_percent": round(endpoint_success_rate, 2),
                "average_response_time_ms": round(endpoint_avg_time, 2),
                "min_response_time_ms": endpoint_df['elapsed'].min(),
                "max_response_time_ms": endpoint_df['elapsed'].max(),
                "p95_response_time_ms": round(endpoint_df['elapsed'].quantile(0.95), 2)
            }
        
        # Lưu report
        report_file = f"{self.results_dir}/performance_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Tạo charts
        self.create_charts(df)
        
        # In summary
        self.print_summary(report)
        
        return report
    
    def create_charts(self, df):
        """Tạo biểu đồ performance"""
        print("📈 Tạo biểu đồ...")
        
        # Set style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Performance Test Results', fontsize=16, fontweight='bold')
        
        # 1. Response Time Distribution
        axes[0, 0].hist(df['elapsed'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Response Time Distribution')
        axes[0, 0].set_xlabel('Response Time (ms)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(df['elapsed'].mean(), color='red', linestyle='--', label=f'Mean: {df["elapsed"].mean():.1f}ms')
        axes[0, 0].legend()
        
        # 2. Response Time by Endpoint
        endpoint_times = df.groupby('label')['elapsed'].mean().sort_values(ascending=True)
        axes[0, 1].barh(endpoint_times.index, endpoint_times.values, color='lightgreen')
        axes[0, 1].set_title('Average Response Time by Endpoint')
        axes[0, 1].set_xlabel('Response Time (ms)')
        
        # 3. Success Rate by Endpoint
        success_rates = []
        endpoints = []
        for endpoint in df['label'].unique():
            endpoint_df = df[df['label'] == endpoint]
            success_rate = (len(endpoint_df[endpoint_df['success'] == True]) / len(endpoint_df)) * 100
            success_rates.append(success_rate)
            endpoints.append(endpoint)
        
        colors = ['green' if rate >= 95 else 'orange' if rate >= 80 else 'red' for rate in success_rates]
        axes[1, 0].bar(endpoints, success_rates, color=colors, alpha=0.7)
        axes[1, 0].set_title('Success Rate by Endpoint')
        axes[1, 0].set_ylabel('Success Rate (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].axhline(y=95, color='red', linestyle='--', alpha=0.7, label='95% Threshold')
        axes[1, 0].legend()
        
        # 4. Response Time Over Time
        df_sorted = df.sort_values('timestamp')
        axes[1, 1].scatter(df_sorted['timestamp'], df_sorted['elapsed'], alpha=0.6, s=20)
        axes[1, 1].set_title('Response Time Over Time')
        axes[1, 1].set_xlabel('Timestamp')
        axes[1, 1].set_ylabel('Response Time (ms)')
        
        plt.tight_layout()
        chart_file = f"{self.results_dir}/performance_charts.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Biểu đồ đã lưu: {chart_file}")
    
    def print_summary(self, report):
        """In summary report"""
        print("\n" + "="*60)
        print("📊 PERFORMANCE TEST SUMMARY")
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
            print(f"     - P95 Response Time: {perf['p95_response_time_ms']}ms")
        
        print(f"\n📁 Files được tạo:")
        print(f"   • JMeter Results: {self.jmeter_results}")
        print(f"   • HTML Report: {self.html_report}/index.html")
        print(f"   • JSON Report: {self.results_dir}/performance_report.json")
        print(f"   • Charts: {self.results_dir}/performance_charts.png")
        
        print("="*60)
    
    def run_full_test(self, threads=50, ramp_up=10, loops=10):
        """Chạy toàn bộ test suite"""
        print("🚀 Bắt đầu Performance Test Suite với JMeter Docker")
        print(f"   Base URL: {self.base_url}")
        print(f"   Threads: {threads}")
        print(f"   Ramp-up: {ramp_up}s")
        print(f"   Loops: {loops}")
        print()
        
        # Kiểm tra hệ thống
        if not self.check_system_health():
            print("❌ Hệ thống không sẵn sàng cho test")
            return False
        
        # Tạo dữ liệu test
        self.create_test_data()
        
        # Build JMeter image
        if not self.build_jmeter_image():
            print("❌ Không thể build JMeter image")
            return False
        
        # Chạy JMeter test
        if not self.run_jmeter_test(threads, ramp_up, loops):
            print("❌ JMeter test thất bại")
            return False
        
        # Phân tích kết quả
        report = self.analyze_results()
        
        if report:
            print("\n✅ Performance test hoàn thành thành công!")
            return True
        else:
            print("\n❌ Phân tích kết quả thất bại")
            return False

def main():
    parser = argparse.ArgumentParser(description='JMeter Performance Test với Docker')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL của API')
    parser.add_argument('--threads', type=int, default=50, help='Số lượng threads')
    parser.add_argument('--ramp-up', type=int, default=10, help='Thời gian ramp-up (giây)')
    parser.add_argument('--loops', type=int, default=10, help='Số lần lặp')
    
    args = parser.parse_args()
    
    # Kiểm tra Docker
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker chưa được cài đặt hoặc không có trong PATH")
        print("📥 Hướng dẫn cài đặt Docker:")
        print("   1. Tải Docker Desktop từ: https://www.docker.com/products/docker-desktop")
        print("   2. Cài đặt và khởi động Docker Desktop")
        return
    
    # Chạy test
    tester = JMeterDockerTester(args.url)
    success = tester.run_full_test(args.threads, args.ramp_up, args.loops)
    
    if success:
        print("\n🎉 Test hoàn thành! Kiểm tra kết quả trong thư mục:", tester.results_dir)
    else:
        print("\n💥 Test thất bại!")
        sys.exit(1)

if __name__ == "__main__":
    main() 