from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from .models import User, Product, SyncLog
from .redis_client import redis_client
from .elasticsearch_client import es_client
import json
from datetime import datetime

class DataSyncService:
    """Service to ensure data integrity across PostgreSQL, Redis, and Elasticsearch"""
    
    def __init__(self):
        self.max_retries = 3
    
    def create_user_with_sync(self, db: Session, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user with synchronization across all systems"""
        sync_log = None
        
        try:
            # Start database transaction
            db.begin()
            
            # Create user in PostgreSQL
            user = User(**user_data)
            db.add(user)
            db.flush()  # Get the ID without committing
            
            # Create sync log entry
            sync_log = SyncLog(
                table_name="users",
                record_id=user.id,
                operation="INSERT",
                sync_status="PENDING"
            )
            db.add(sync_log)
            db.flush()
            
            # Sync to Redis
            redis_success = redis_client.set_user(user.id, {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })
            
            # Sync to Elasticsearch
            es_success = es_client.index_user({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })
            
            # Update sync log
            sync_log.redis_sync = redis_success
            sync_log.elasticsearch_sync = es_success
            sync_log.sync_status = "SUCCESS" if (redis_success and es_success) else "PARTIAL"
            
            # Commit transaction
            db.commit()
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                },
                "sync_status": {
                    "redis": redis_success,
                    "elasticsearch": es_success
                }
            }
            
        except Exception as e:
            # Rollback transaction
            db.rollback()
            
            if sync_log:
                sync_log.sync_status = "FAILED"
                sync_log.error_message = str(e)
                db.add(sync_log)
                db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "sync_status": {
                    "redis": False,
                    "elasticsearch": False
                }
            }
    
    def update_user_with_sync(self, db: Session, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user with synchronization across all systems"""
        sync_log = None
        
        try:
            # Start database transaction
            db.begin()
            
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Update user in PostgreSQL
            for key, value in user_data.items():
                setattr(user, key, value)
            user.updated_at = datetime.now()
            
            # Create sync log entry
            sync_log = SyncLog(
                table_name="users",
                record_id=user.id,
                operation="UPDATE",
                sync_status="PENDING"
            )
            db.add(sync_log)
            db.flush()
            
            # Sync to Redis
            redis_success = redis_client.set_user(user.id, {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })
            
            # Sync to Elasticsearch
            es_success = es_client.update_user({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })
            
            # Update sync log
            sync_log.redis_sync = redis_success
            sync_log.elasticsearch_sync = es_success
            sync_log.sync_status = "SUCCESS" if (redis_success and es_success) else "PARTIAL"
            
            # Commit transaction
            db.commit()
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                },
                "sync_status": {
                    "redis": redis_success,
                    "elasticsearch": es_success
                }
            }
            
        except Exception as e:
            # Rollback transaction
            db.rollback()
            
            if sync_log:
                sync_log.sync_status = "FAILED"
                sync_log.error_message = str(e)
                db.add(sync_log)
                db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "sync_status": {
                    "redis": False,
                    "elasticsearch": False
                }
            }
    
    def delete_user_with_sync(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Delete user with synchronization across all systems"""
        sync_log = None
        
        try:
            # Start database transaction
            db.begin()
            
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Create sync log entry
            sync_log = SyncLog(
                table_name="users",
                record_id=user.id,
                operation="DELETE",
                sync_status="PENDING"
            )
            db.add(sync_log)
            db.flush()
            
            # Delete from Redis
            redis_success = redis_client.delete_user(user_id)
            
            # Delete from Elasticsearch
            es_success = es_client.delete_user(user_id)
            
            # Delete from PostgreSQL
            db.delete(user)
            
            # Update sync log
            sync_log.redis_sync = redis_success
            sync_log.elasticsearch_sync = es_success
            sync_log.sync_status = "SUCCESS" if (redis_success and es_success) else "PARTIAL"
            
            # Commit transaction
            db.commit()
            
            return {
                "success": True,
                "sync_status": {
                    "redis": redis_success,
                    "elasticsearch": es_success
                }
            }
            
        except Exception as e:
            # Rollback transaction
            db.rollback()
            
            if sync_log:
                sync_log.sync_status = "FAILED"
                sync_log.error_message = str(e)
                db.add(sync_log)
                db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "sync_status": {
                    "redis": False,
                    "elasticsearch": False
                }
            }
    
    def get_user_with_cache(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user with cache-first strategy"""
        # Try Redis cache first
        cached_user = redis_client.get_user(user_id)
        if cached_user:
            return cached_user
        
        # If not in cache, get from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        
        # Cache the result
        redis_client.set_user(user_id, user_data)
        
        return user_data
    
    def search_users_with_elasticsearch(self, query: str) -> Dict[str, Any]:
        """Search users using Elasticsearch"""
        try:
            results = es_client.search_users(query)
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }
    
    # Product methods
    def create_product_with_sync(self, db: Session, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create product with synchronization across all systems"""
        sync_log = None
        
        try:
            # Start database transaction
            db.begin()
            
            # Create product in PostgreSQL
            product = Product(**product_data)
            db.add(product)
            db.flush()  # Get the ID without committing
            
            # Create sync log entry
            sync_log = SyncLog(
                table_name="products",
                record_id=product.id,
                operation="INSERT",
                sync_status="PENDING"
            )
            db.add(sync_log)
            db.flush()
            
            # Sync to Redis
            redis_success = redis_client.set_product(product.id, {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "category": product.category,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            })
            
            # Sync to Elasticsearch
            es_success = es_client.index_product({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "category": product.category,
                "created_at": product.created_at.isoformat(),
                "updated_at": product.updated_at.isoformat()
            })
            
            # Update sync log
            sync_log.redis_sync = redis_success
            sync_log.elasticsearch_sync = es_success
            sync_log.sync_status = "SUCCESS" if (redis_success and es_success) else "PARTIAL"
            
            # Commit transaction
            db.commit()
            
            return {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "category": product.category,
                    "created_at": product.created_at.isoformat(),
                    "updated_at": product.updated_at.isoformat()
                },
                "sync_status": {
                    "redis": redis_success,
                    "elasticsearch": es_success
                }
            }
            
        except Exception as e:
            # Rollback transaction
            db.rollback()
            
            if sync_log:
                sync_log.sync_status = "FAILED"
                sync_log.error_message = str(e)
                db.add(sync_log)
                db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "sync_status": {
                    "redis": False,
                    "elasticsearch": False
                }
            }
    
    def get_product_with_cache(self, db: Session, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product with cache-first strategy"""
        # Try Redis cache first
        cached_product = redis_client.get_product(product_id)
        if cached_product:
            return cached_product
        
        # If not in cache, get from database
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "category": product.category,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
        
        # Cache the result
        redis_client.set_product(product_id, product_data)
        
        return product_data
    
    def search_products_with_elasticsearch(self, query: str) -> Dict[str, Any]:
        """Search products using Elasticsearch"""
        try:
            results = es_client.search_products(query)
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }
    
    def get_sync_status(self, db: Session) -> Dict[str, Any]:
        """Get synchronization status and statistics"""
        try:
            # Get sync log statistics
            total_syncs = db.query(SyncLog).count()
            successful_syncs = db.query(SyncLog).filter(SyncLog.sync_status == "SUCCESS").count()
            failed_syncs = db.query(SyncLog).filter(SyncLog.sync_status == "FAILED").count()
            
            # Get cache statistics
            cache_stats = redis_client.get_cache_stats()
            
            # Get Elasticsearch statistics
            es_stats = es_client.get_index_stats()
            
            return {
                "sync_statistics": {
                    "total_syncs": total_syncs,
                    "successful_syncs": successful_syncs,
                    "failed_syncs": failed_syncs,
                    "success_rate": (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
                },
                "cache_statistics": cache_stats,
                "elasticsearch_statistics": es_stats
            }
        except Exception as e:
            return {
                "error": str(e)
            }

# Global sync service instance
sync_service = DataSyncService() 