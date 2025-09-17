from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate

# возвращение всех товаров из БД
def get_products(db: Session):
    return db.query(Product).all()

# создание нового товара в БД
def create_product(db: Session, product: ProductCreate):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    return new_product