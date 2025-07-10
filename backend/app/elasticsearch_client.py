import os
from elasticsearch import Elasticsearch
from typing import Dict, List, Any, Optional
from datetime import datetime

class ElasticsearchClient:
    def __init__(self):
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.client = Elasticsearch(
            [self.es_url],
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        self.init_indices()
    
    def health_check(self) -> bool:
        """Check Elasticsearch connectivity"""
        try:
            health = self.client.cluster.health()
            return health['status'] in ['green', 'yellow']
        except Exception as e:
            print(f"Elasticsearch health check failed: {e}")
            return False
    
    def init_indices(self):
        """Initialize Elasticsearch indices with proper mappings"""
        # Users index
        users_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "email": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        # Products index
        products_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "price": {"type": "float"},
                    "category": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        
        # Create indices if they don't exist
        if not self.client.indices.exists(index="users"):
            self.client.indices.create(index="users", body=users_mapping)
        
        if not self.client.indices.exists(index="products"):
            self.client.indices.create(index="products", body=products_mapping)
    
    def index_user(self, user_data: Dict[str, Any]) -> bool:
        """Index user data in Elasticsearch"""
        try:
            doc = {
                "id": user_data["id"],
                "name": user_data["name"],
                "email": user_data["email"],
                "created_at": user_data["created_at"],
                "updated_at": user_data["updated_at"]
            }
            
            self.client.index(
                index="users",
                id=user_data["id"],
                body=doc
            )
            return True
        except Exception as e:
            print(f"Failed to index user {user_data.get('id')}: {e}")
            return False
    
    def update_user(self, user_data: Dict[str, Any]) -> bool:
        """Update user data in Elasticsearch"""
        try:
            doc = {
                "doc": {
                    "name": user_data["name"],
                    "email": user_data["email"],
                    "updated_at": user_data["updated_at"]
                }
            }
            
            self.client.update(
                index="users",
                id=user_data["id"],
                body=doc
            )
            return True
        except Exception as e:
            print(f"Failed to update user {user_data.get('id')}: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user from Elasticsearch"""
        try:
            self.client.delete(index="users", id=user_id)
            return True
        except Exception as e:
            print(f"Failed to delete user {user_id}: {e}")
            return False
    
    def index_product(self, product_data: Dict[str, Any]) -> bool:
        """Index product data in Elasticsearch"""
        try:
            doc = {
                "id": product_data["id"],
                "name": product_data["name"],
                "description": product_data.get("description", ""),
                "price": float(product_data["price"]),
                "category": product_data.get("category", ""),
                "created_at": product_data["created_at"],
                "updated_at": product_data["updated_at"]
            }
            
            self.client.index(
                index="products",
                id=product_data["id"],
                body=doc
            )
            return True
        except Exception as e:
            print(f"Failed to index product {product_data.get('id')}: {e}")
            return False
    
    def update_product(self, product_data: Dict[str, Any]) -> bool:
        """Update product data in Elasticsearch"""
        try:
            doc = {
                "doc": {
                    "name": product_data["name"],
                    "description": product_data.get("description", ""),
                    "price": float(product_data["price"]),
                    "category": product_data.get("category", ""),
                    "updated_at": product_data["updated_at"]
                }
            }
            
            self.client.update(
                index="products",
                id=product_data["id"],
                body=doc
            )
            return True
        except Exception as e:
            print(f"Failed to update product {product_data.get('id')}: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product from Elasticsearch"""
        try:
            self.client.delete(index="products", id=product_id)
            return True
        except Exception as e:
            print(f"Failed to delete product {product_id}: {e}")
            return False
    
    def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search users in Elasticsearch"""
        try:
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name", "email"],
                        "type": "best_fields"
                    }
                }
            }
            
            response = self.client.search(index="users", body=search_body)
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            print(f"Failed to search users: {e}")
            return []
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search products in Elasticsearch"""
        try:
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name", "description", "category"],
                        "type": "best_fields"
                    }
                }
            }
            
            response = self.client.search(index="products", body=search_body)
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            print(f"Failed to search products: {e}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get Elasticsearch index statistics"""
        try:
            stats = self.client.indices.stats()
            return {
                "total_docs": stats["_all"]["total"]["docs"]["count"],
                "total_size": stats["_all"]["total"]["store"]["size_in_bytes"],
                "indices": list(stats["indices"].keys())
            }
        except Exception as e:
            print(f"Failed to get index stats: {e}")
            return {}

# Global Elasticsearch client instance
es_client = ElasticsearchClient() 