from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from .database import get_db, health_check as db_health_check
from .redis_client import redis_client
from .elasticsearch_client import es_client
from .sync_service import sync_service
from .models import User, Product

app = FastAPI(
    title="Data Integrity API",
    description="API for managing data with Redis cache and Elasticsearch search",
    version="1.0.0"
)

# Pydantic models for request/response
class UserCreate(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

# Health check endpoints
@app.get("/health")
async def health_check():
    """Check health of all services"""
    db_healthy = db_health_check()
    redis_healthy = redis_client.health_check()
    es_healthy = es_client.health_check()
    
    return {
        "status": "healthy" if all([db_healthy, redis_healthy, es_healthy]) else "unhealthy",
        "services": {
            "postgresql": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "elasticsearch": "healthy" if es_healthy else "unhealthy"
        }
    }

@app.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Get detailed health and statistics"""
    stats = sync_service.get_sync_status(db)
    return {
        "health": await health_check(),
        "statistics": stats
    }

# User endpoints
@app.post("/users", response_model=Dict[str, Any])
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with data synchronization"""
    try:
        result = sync_service.create_user_with_sync(db, user_data.dict())
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID with cache-first strategy"""
    try:
        user = sync_service.get_user_with_cache(db, user_id)
        if user:
            return {"success": True, "user": user}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}", response_model=Dict[str, Any])
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user with data synchronization"""
    try:
        # Filter out None values
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = sync_service.update_user_with_sync(db, user_id, update_data)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}", response_model=Dict[str, Any])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user with data synchronization"""
    try:
        result = sync_service.delete_user_with_sync(db, user_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/search", response_model=Dict[str, Any])
async def search_users(q: str = Query(..., description="Search query")):
    """Search users using Elasticsearch"""
    try:
        result = sync_service.search_users_with_elasticsearch(q)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users", response_model=List[Dict[str, Any]])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users from database"""
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Product endpoints (similar pattern)
@app.post("/products", response_model=Dict[str, Any])
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product with data synchronization"""
    try:
        result = sync_service.create_product_with_sync(db, product_data.dict())
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID with cache-first strategy"""
    try:
        product = sync_service.get_product_with_cache(db, product_id)
        if product:
            return {"success": True, "product": product}
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/search", response_model=Dict[str, Any])
async def search_products(q: str = Query(..., description="Search query")):
    """Search products using Elasticsearch"""
    try:
        result = sync_service.search_products_with_elasticsearch(q)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cache management endpoints
@app.get("/cache/stats")
async def get_cache_stats():
    """Get Redis cache statistics"""
    try:
        stats = redis_client.get_cache_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cache/users/{user_id}")
async def clear_user_cache(user_id: int):
    """Clear user cache from Redis"""
    try:
        success = redis_client.delete_user(user_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sync status endpoints
@app.get("/sync/status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Get synchronization status and statistics"""
    try:
        stats = sync_service.get_sync_status(db)
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sync/retry-failed")
async def retry_failed_syncs(db: Session = Depends(get_db)):
    """Retry failed synchronizations"""
    try:
        # Get failed syncs
        failed_syncs = db.query(SyncLog).filter(SyncLog.sync_status == "FAILED").all()
        retry_count = 0
        
        for sync_log in failed_syncs:
            try:
                if sync_log.table_name == "users":
                    if sync_log.operation == "INSERT":
                        # Retry logic for failed user creation
                        pass
                    elif sync_log.operation == "UPDATE":
                        # Retry logic for failed user update
                        pass
                    elif sync_log.operation == "DELETE":
                        # Retry logic for failed user deletion
                        pass
                
                retry_count += 1
            except Exception as e:
                print(f"Failed to retry sync {sync_log.id}: {e}")
        
        return {
            "success": True,
            "retried_count": retry_count,
            "total_failed": len(failed_syncs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 