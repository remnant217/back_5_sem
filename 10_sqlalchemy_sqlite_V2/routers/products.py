# Depends - функция для создания зависимостей в FastAPI, пригодится для внедрения сессии базы 
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
# подключаем компоненты из ранее созданных модулей
from database import get_db
from models import Product
from schemas import ProductCreate, ProductOut, ProductUpdate
from repositories import products_repository

# создаем объект роутера
router = APIRouter(
    prefix='/products',
    tags=['Products']
)

# вспомогательная функция для проверки наличия товара
def get_product_or_404(db: Session, product_id: int) -> Product:
    product = products_repository.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

# создание нового товара
# в response_model указываем схему ProductOut, предназначенную для ответа клиенту
@router.post('', response_model=ProductOut)
# FastAPI вызовет get_db(), создаст сессию и передаст ее в функцию
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    return products_repository.create_product(db, product_data)

# получение списка товаров с фильтрацией
@router.get('', response_model=list[ProductOut])
def get_products_list(
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена'),
    db: Session = Depends(get_db)
):
    return products_repository.get_products_list(db, q, in_stock, min_price, max_price)

# получение одного товара по ID
@router.get('/{product_id}', response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(db, product_id)

# полное обновление товара
@router.put('/{product_id}', response_model=ProductOut)
def put_product(product_id: int, product_data: ProductCreate, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    return products_repository.put_product(db, product, product_data)

# частичное обновление товара
@router.patch('/{product_id}', response_model=ProductOut)
def patch_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    return products_repository.patch_product(db, product, product_data)

# удаление товара
@router.delete('/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    products_repository.delete_product(db, product)
    return {'message': 'Товар удален'}