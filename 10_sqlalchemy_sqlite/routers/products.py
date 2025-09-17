from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProductCreate, ProductOut
from repositories import products_repository

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

@router.get('/', response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return products_repository.get_products(db)

@router.post('/', response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return products_repository.create_product(db, product)