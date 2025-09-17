from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate, ProductUpdate

def create_product(db: Session, product_data: ProductCreate) -> Product:
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    return new_product

def get_products_list(
    db: Session,
    q: str = None,
    in_stock: bool = None,
    min_price: float = None,
    max_price: float = None
) -> list[Product]:

    result = db.query(Product)

    if in_stock is not None:
        result = result.filter(Product.in_stock == in_stock)
    if min_price is not None:
        result = result.filter(Product.price >= min_price)
    if max_price is not None:
        result = result.filter(Product.price <= max_price)
    
    result = result.all()

    if q:
        low_q = q.lower()
        result = [p for p in result if low_q in p.name.lower()]
    
    return result

def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()

def put_product(db: Session, product: Product, product_data: ProductCreate) -> Product:
    for field, value in product_data.model_dump().items():
        setattr(product, field, value)
    db.commit()
    return product

def patch_product(db: Session, product: Product, product_data: ProductUpdate) -> Product:
    updates = product_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)
    db.commit()
    return product

def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()