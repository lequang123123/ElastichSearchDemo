import os
import json
import time
import redis
from typing import Optional, Any, Dict
from datetime import datetime

class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self, max_retries=5, delay=1):
        """Test Redis connection with retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"Testing Redis connection (attempt {attempt + 1}/{max_retries})")
                if self.health_check():
                    print("Redis connection successful!")
                    return
                else:
                    raise Exception("Health check failed")
            except Exception as e:
                print(f"Redis connection failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Redis connection failed.")
                    # Don't raise exception, just log the error
    
    def health_check(self) -> bool:
        """Check Redis connectivity"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            print(f"Redis health check failed: {e}")
            return False
    
    def set_user(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """Cache user data in Redis"""
        try:
            key = f"user:{user_id}"
            # Add timestamp for cache invalidation
            user_data['cached_at'] = datetime.now().isoformat()
            self.client.setex(key, 3600, json.dumps(user_data))  # TTL: 1 hour
            return True
        except Exception as e:
            print(f"Failed to cache user {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from Redis cache"""
        try:
            key = f"user:{user_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Failed to get user {user_id} from cache: {e}")
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user from Redis cache"""
        try:
            key = f"user:{user_id}"
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Failed to delete user {user_id} from cache: {e}")
            return False
    
    def set_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Cache product data in Redis"""
        try:
            key = f"product:{product_id}"
            product_data['cached_at'] = datetime.now().isoformat()
            self.client.setex(key, 3600, json.dumps(product_data))  # TTL: 1 hour
            return True
        except Exception as e:
            print(f"Failed to cache product {product_id}: {e}")
            return False
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product data from Redis cache"""
        try:
            key = f"product:{product_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Failed to get product {product_id} from cache: {e}")
            return None
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product from Redis cache"""
        try:
            key = f"product:{product_id}"
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Failed to delete product {product_id} from cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        try:
            info = self.client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            print(f"Failed to get cache stats: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """Clear all cache data"""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"Failed to clear cache: {e}")
            return False
    
    def count_users(self) -> int:
        """Count cached users"""
        try:
            keys = self.client.keys("user:*")
            return len(keys)
        except Exception as e:
            print(f"Failed to count users: {e}")
            return 0
    
    def count_products(self) -> int:
        """Count cached products"""
        try:
            keys = self.client.keys("product:*")
            return len(keys)
        except Exception as e:
            print(f"Failed to count products: {e}")
            return 0
    
    def ping(self) -> bool:
        """Ping Redis server"""
        try:
            return self.client.ping()
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False

# Global Redis client instance
redis_client = RedisClient() 