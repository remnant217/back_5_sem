from fastapi import APIRouter, HTTPException, Query, Depends
# подключаем класс AsyncSession для работы с асинхронной сессией
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Product
from schemas import ProductCreate, ProductOut, ProductUpdate
from repositories import products_repository

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

# вспомогательная функция для проверки наличия товара
async def get_product_or_404(session: AsyncSession, product_id: int) -> Product:
    product = await products_repository.get_product(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

# создание нового товара
@router.post('', response_model=ProductOut)
async def create_product(product_data: ProductCreate, session: AsyncSession = Depends(get_session)):
    return await products_repository.create_product(session, product_data)

# получение списка товаров с фильтрацией
@router.get('', response_model=list[ProductOut])
async def get_products_list(
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена'),
    session: AsyncSession = Depends(get_session)
):
    return await products_repository.get_products_list(session, q, in_stock, min_price, max_price)

# получение одного товара по ID
@router.get('/{product_id}', response_model=ProductOut)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    return await get_product_or_404(session, product_id)

# полное обновление товара
@router.put('/{product_id}', response_model=ProductOut)
async def put_product(product_id: int, product_data: ProductCreate, session: AsyncSession = Depends(get_session)):
    # при вызове get_product_or_404() тоже ставим await, иначе в product попадет корутина, а не объект Product
    product = await get_product_or_404(session, product_id)
    return await products_repository.put_product(session, product, product_data)

# частичное обновление товара
@router.patch('/{product_id}', response_model=ProductOut)
async def patch_product(product_id: int, product_data: ProductUpdate, session: AsyncSession = Depends(get_session)):
    product = await get_product_or_404(session, product_id)
    return await products_repository.patch_product(session, product, product_data)

# удаление товара
@router.delete('/{product_id}')
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    product = await get_product_or_404(session, product_id)
    await products_repository.delete_product(session, product)
    return {'message': 'Товар удален'}