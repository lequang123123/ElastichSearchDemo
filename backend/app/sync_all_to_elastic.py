from database import SessionLocal
from models import User, Product
from elasticsearch_client import es_client


def sync_all_users():
    db = SessionLocal()
    users = db.query(User).all()
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        es_client.index_user(user_data)
    db.close()
    print("Đã sync toàn bộ users lên Elasticsearch!")

def sync_all_products():
    db = SessionLocal()
    products = db.query(Product).all()
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "category": product.category,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
        es_client.index_product(product_data)
    db.close()
    print("Đã sync toàn bộ products lên Elasticsearch!")

if __name__ == "__main__":
    sync_all_users()
    sync_all_products() 