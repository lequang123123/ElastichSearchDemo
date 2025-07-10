#!/usr/bin/env python3
"""
Test script for Data Integrity API
Demo how to use the API with Redis cache and Elasticsearch search
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Status: {response.json()}")
    print()

def test_create_user():
    """Test creating a user with data synchronization"""
    print("👤 Creating user with data sync...")
    
    user_data = {
        "name": "Alice Johnson",
        "email": "alice@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    result = response.json()
    
    if result.get("success"):
        print(f"✅ User created successfully!")
        print(f"   User ID: {result['user']['id']}")
        print(f"   Redis sync: {result['sync_status']['redis']}")
        print(f"   Elasticsearch sync: {result['sync_status']['elasticsearch']}")
        return result['user']['id']
    else:
        print(f"❌ Failed to create user: {result.get('error')}")
        return None

def test_get_user_with_cache(user_id):
    """Test getting user with cache-first strategy"""
    print(f"🔍 Getting user {user_id} with cache...")
    
    # First request (should hit database)
    start_time = time.time()
    response1 = requests.get(f"{BASE_URL}/users/{user_id}")
    db_time = time.time() - start_time
    
    # Second request (should hit cache)
    start_time = time.time()
    response2 = requests.get(f"{BASE_URL}/users/{user_id}")
    cache_time = time.time() - start_time
    
    if response1.status_code == 200 and response2.status_code == 200:
        print(f"✅ User retrieved successfully!")
        print(f"   Database time: {db_time:.3f}s")
        print(f"   Cache time: {cache_time:.3f}s")
        print(f"   Speed improvement: {((db_time - cache_time) / db_time * 100):.1f}%")
    else:
        print(f"❌ Failed to get user")
    print()

def test_search_users():
    """Test searching users with Elasticsearch"""
    print("🔍 Testing user search with Elasticsearch...")
    
    # Search for users
    search_queries = ["alice", "john", "example"]
    
    for query in search_queries:
        response = requests.get(f"{BASE_URL}/users/search", params={"q": query})
        result = response.json()
        
        if result.get("success"):
            print(f"✅ Search for '{query}': {result['count']} results")
            for user in result['results']:
                print(f"   - {user['name']} ({user['email']})")
        else:
            print(f"❌ Search failed for '{query}': {result.get('error')}")
    print()

def test_create_product():
    """Test creating a product with data synchronization"""
    print("📦 Creating product with data sync...")
    
    product_data = {
        "name": "MacBook Pro",
        "description": "High-performance laptop for professionals",
        "price": 1999.99,
        "category": "Electronics"
    }
    
    response = requests.post(f"{BASE_URL}/products", json=product_data)
    result = response.json()
    
    if result.get("success"):
        print(f"✅ Product created successfully!")
        print(f"   Product ID: {result['product']['id']}")
        print(f"   Name: {result['product']['name']}")
        print(f"   Price: ${result['product']['price']}")
        print(f"   Redis sync: {result['sync_status']['redis']}")
        print(f"   Elasticsearch sync: {result['sync_status']['elasticsearch']}")
        return result['product']['id']
    else:
        print(f"❌ Failed to create product: {result.get('error')}")
        return None

def test_search_products():
    """Test searching products with Elasticsearch"""
    print("🔍 Testing product search with Elasticsearch...")
    
    # Search for products
    search_queries = ["laptop", "electronics", "macbook"]
    
    for query in search_queries:
        response = requests.get(f"{BASE_URL}/products/search", params={"q": query})
        result = response.json()
        
        if result.get("success"):
            print(f"✅ Search for '{query}': {result['count']} results")
            for product in result['results']:
                print(f"   - {product['name']} (${product['price']})")
        else:
            print(f"❌ Search failed for '{query}': {result.get('error')}")
    print()

def test_cache_statistics():
    """Test getting cache statistics"""
    print("📊 Getting cache statistics...")
    
    response = requests.get(f"{BASE_URL}/cache/stats")
    result = response.json()
    
    if result.get("success"):
        stats = result['stats']
        print(f"✅ Cache statistics:")
        print(f"   Connected clients: {stats.get('connected_clients', 0)}")
        print(f"   Used memory: {stats.get('used_memory_human', '0B')}")
        print(f"   Cache hits: {stats.get('keyspace_hits', 0)}")
        print(f"   Cache misses: {stats.get('keyspace_misses', 0)}")
        
        if stats.get('keyspace_hits', 0) > 0:
            hit_rate = stats['keyspace_hits'] / (stats['keyspace_hits'] + stats['keyspace_misses']) * 100
            print(f"   Hit rate: {hit_rate:.1f}%")
    else:
        print(f"❌ Failed to get cache stats: {result.get('error')}")
    print()

def test_sync_status():
    """Test getting synchronization status"""
    print("📊 Getting sync status...")
    
    response = requests.get(f"{BASE_URL}/sync/status")
    result = response.json()
    
    if result.get("success"):
        stats = result['stats']
        sync_stats = stats.get('sync_statistics', {})
        
        print(f"✅ Sync statistics:")
        print(f"   Total syncs: {sync_stats.get('total_syncs', 0)}")
        print(f"   Successful syncs: {sync_stats.get('successful_syncs', 0)}")
        print(f"   Failed syncs: {sync_stats.get('failed_syncs', 0)}")
        print(f"   Success rate: {sync_stats.get('success_rate', 0):.1f}%")
        
        es_stats = stats.get('elasticsearch_statistics', {})
        print(f"   Elasticsearch docs: {es_stats.get('total_docs', 0)}")
    else:
        print(f"❌ Failed to get sync status: {result.get('error')}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting Data Integrity API Tests")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test user operations
    user_id = test_create_user()
    if user_id:
        test_get_user_with_cache(user_id)
    
    test_search_users()
    
    # Test product operations
    product_id = test_create_product()
    if product_id:
        test_search_products()
    
    # Test statistics
    test_cache_statistics()
    test_sync_status()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 