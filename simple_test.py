#!/usr/bin/env python3
"""
Simple API Test Script
Kiểm tra API trước khi chạy JMeter
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing API endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"Health Check Error: {e}")
    
    # Test create user
    try:
        user_data = {
            "username": "testuser_1",
            "email": "testuser_1@example.com",
            "password": "password123"
        }
        response = requests.post(f"{base_url}/users/", json=user_data, timeout=10)
        print(f"Create User: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"Create User Error: {e}")
    
    # Test get users
    try:
        response = requests.get(f"{base_url}/users/", timeout=10)
        print(f"Get Users: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Users count: {len(data)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"Get Users Error: {e}")
    
    # Test search users
    try:
        response = requests.get(f"{base_url}/users/search?q=test", timeout=10)
        print(f"Search Users: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Search results: {len(data)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"Search Users Error: {e}")

if __name__ == "__main__":
    test_api() 