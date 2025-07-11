from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from .database import get_db
from .sync_service import DataSyncService
from .elasticsearch_client import es_client
from .redis_client import redis_client
import time
import json

router = APIRouter(prefix="/admin", tags=["Data Synchronization"])
sync_service = DataSyncService()

@router.post("/sync")
async def sync_all_data(db: Session = Depends(get_db)):
    """Đồng bộ toàn bộ dữ liệu từ PostgreSQL sang Redis và Elasticsearch, đồng thời cache toàn bộ user vào Redis"""
    start_time = time.time()
    
    try:
        # 1. Sync users
        users = db.query(User).all()
        user_sync_count = 0
        user_errors = 0
        
        # 2. Clear Redis cache trước (nếu muốn giữ lại, có thể bỏ dòng này)
        redis_client.clear_cache()
        
        for user in users:
            try:
                # Sync to Redis (luôn luôn cache lại user)
                redis_client.set_user(user.id, {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                })
                
                # Sync to Elasticsearch
                es_client.index_user({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                })
                
                user_sync_count += 1
            except Exception as e:
                user_errors += 1
                print(f"Error syncing user {user.id}: {e}")
        
        # 3. Sync products (if exists)
        products = db.query(Product).all()
        product_sync_count = 0
        product_errors = 0
        
        for product in products:
            try:
                # Sync to Redis
                redis_client.set_product(product.id, {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "category": product.category,
                    "created_at": product.created_at.isoformat(),
                    "updated_at": product.updated_at.isoformat()
                })
                
                # Sync to Elasticsearch
                es_client.index_product({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "category": product.category,
                    "created_at": product.created_at.isoformat(),
                    "updated_at": product.updated_at.isoformat()
                })
                
                product_sync_count += 1
            except Exception as e:
                product_errors += 1
                print(f"Error syncing product {product.id}: {e}")
        
        sync_time = (time.time() - start_time) * 1000
        
        return {
            "sync_status": "completed",
            "postgresql_count": len(users) + len(products),
            "elasticsearch_count": user_sync_count + product_sync_count,
            "redis_cleared": True,
            "sync_time_ms": round(sync_time, 2),
            "details": {
                "users_synced": user_sync_count,
                "users_errors": user_errors,
                "products_synced": product_sync_count,
                "products_errors": product_errors,
                "total_errors": user_errors + product_errors
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.post("/rebuild-index")
async def rebuild_elasticsearch_index():
    """Xây dựng lại toàn bộ Elasticsearch index"""
    start_time = time.time()
    
    try:
        # 1. Delete existing indices
        es_client.delete_users_index()
        es_client.delete_products_index()
        
        # 2. Create new indices with proper mapping
        es_client.create_users_index()
        es_client.create_products_index()
        
        # 3. Trigger full sync
        db = next(get_db())
        sync_result = await sync_all_data(db)
        
        rebuild_time = (time.time() - start_time) * 1000
        
        return {
            "rebuild_status": "completed",
            "indices_rebuilt": ["users", "products"],
            "rebuild_time_ms": round(rebuild_time, 2),
            "sync_result": sync_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")

@router.get("/sync-status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Kiểm tra trạng thái đồng bộ dữ liệu"""
    try:
        # 1. Count records in PostgreSQL
        postgresql_users = db.query(User).count()
        postgresql_products = db.query(Product).count()
        
        # 2. Count records in Elasticsearch
        es_users = es_client.count_users()
        es_products = es_client.count_products()
        
        # 3. Count records in Redis
        redis_users = redis_client.count_users()
        redis_products = redis_client.count_products()
        
        # 4. Check sync logs
        sync_logs = db.query(SyncLog).order_by(SyncLog.created_at.desc()).limit(10).all()
        
        return {
            "data_counts": {
                "postgresql": {
                    "users": postgresql_users,
                    "products": postgresql_products,
                    "total": postgresql_users + postgresql_products
                },
                "elasticsearch": {
                    "users": es_users,
                    "products": es_products,
                    "total": es_users + es_products
                },
                "redis": {
                    "users": redis_users,
                    "products": redis_products,
                    "total": redis_users + redis_products
                }
            },
            "sync_health": {
                "postgresql_elasticsearch": postgresql_users == es_users and postgresql_products == es_products,
                "postgresql_redis": postgresql_users == redis_users and postgresql_products == redis_products,
                "overall_healthy": (postgresql_users == es_users == redis_users) and (postgresql_products == es_products == redis_products)
            },
            "recent_sync_logs": [
                {
                    "id": log.id,
                    "table_name": log.table_name,
                    "record_id": log.record_id,
                    "operation": log.operation,
                    "sync_status": log.sync_status,
                    "created_at": log.created_at.isoformat()
                }
                for log in sync_logs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.post("/clear-cache")
async def clear_all_cache():
    """Xóa toàn bộ cache trong Redis"""
    try:
        redis_client.clear_cache()
        return {
            "cache_cleared": True,
            "message": "All cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@router.get("/data-integrity-check")
async def check_data_integrity(db: Session = Depends(get_db)):
    """Kiểm tra tính toàn vẹn dữ liệu giữa các hệ thống"""
    try:
        integrity_report = {
            "timestamp": time.time(),
            "checks": [],
            "overall_status": "healthy"
        }
        
        # Check 1: User count consistency
        pg_users = db.query(User).count()
        es_users = es_client.count_users()
        redis_users = redis_client.count_users()
        
        user_consistent = pg_users == es_users == redis_users
        integrity_report["checks"].append({
            "check": "user_count_consistency",
            "status": "pass" if user_consistent else "fail",
            "details": {
                "postgresql": pg_users,
                "elasticsearch": es_users,
                "redis": redis_users
            }
        })
        
        # Check 2: Sample user data consistency
        if pg_users > 0:
            sample_user = db.query(User).first()
            pg_data = {
                "id": sample_user.id,
                "name": sample_user.name,
                "email": sample_user.email
            }
            
            es_data = es_client.get_user(sample_user.id)
            redis_data = redis_client.get_user(sample_user.id)
            
            data_consistent = (
                pg_data["name"] == es_data.get("name") == redis_data.get("name") and
                pg_data["email"] == es_data.get("email") == redis_data.get("email")
            )
            
            integrity_report["checks"].append({
                "check": "sample_user_data_consistency",
                "status": "pass" if data_consistent else "fail",
                "details": {
                    "postgresql": pg_data,
                    "elasticsearch": es_data,
                    "redis": redis_data
                }
            })
        
        # Check 3: Elasticsearch index health
        es_health = es_client.get_cluster_health()
        integrity_report["checks"].append({
            "check": "elasticsearch_health",
            "status": "pass" if es_health["status"] == "green" else "fail",
            "details": es_health
        })
        
        # Check 4: Redis connectivity
        redis_ping = redis_client.ping()
        integrity_report["checks"].append({
            "check": "redis_connectivity",
            "status": "pass" if redis_ping else "fail",
            "details": {"ping": redis_ping}
        })
        
        # Overall status
        failed_checks = [check for check in integrity_report["checks"] if check["status"] == "fail"]
        if failed_checks:
            integrity_report["overall_status"] = "unhealthy"
            integrity_report["failed_checks_count"] = len(failed_checks)
        
        return integrity_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrity check failed: {str(e)}")

# Import models
from .models import User, Product, SyncLog 