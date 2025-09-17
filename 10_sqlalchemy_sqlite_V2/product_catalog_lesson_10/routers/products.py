from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Product
from schemas import ProductCreate, ProductOut, ProductUpdate
from repositories import products_repository

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

def get_product_or_404(db: Session, product_id: int) -> Product:
    product = products_repository.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

@router.post('', response_model=ProductOut)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    return products_repository.create_product(db, product_data)

@router.get('', response_model=list[ProductOut])
def get_products_list(
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена'),
    db: Session = Depends(get_db)
):
    return products_repository.get_products_list(db, q, in_stock, min_price, max_price)

@router.get('/{product_id}', response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(db, product_id)

@router.put('/{product_id}', response_model=ProductOut)
def put_product(product_id: int, product_data: ProductCreate, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    return products_repository.put_product(db, product, product_data)

@router.patch('/{product_id}', response_model=ProductOut)
def patch_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    return products_repository.patch_product(db, product, product_data)

@router.delete('/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    products_repository.delete_product(db, product)
    return {'message': 'Товар удален'}