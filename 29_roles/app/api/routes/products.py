from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.products import ProductOut, ProductCreate, ProductUpdate
from app.repositories.products import (
    get_product_by_id, 
    create_product as create_product_repo,
    update_product as update_product_repo
)

router = APIRouter(prefix='/products', tags=['products'])

# получаем продукт по ID
@router.get('/{product_id}', response_model=ProductOut)
async def get_product(session: SessionDep, product_id: int):
    product = await get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Продукт не найден')
    return product

# создаем новый продукт
@router.post('/', response_model=ProductOut)
async def create_product(session: SessionDep, product_data: ProductCreate):
    new_product = await create_product_repo(session=session, product_create=product_data)
    return new_product

# обновляем продукт
@router.put('/{product_id}', response_model=ProductOut)
async def update_product(session: SessionDep, product_id: int, product_data: ProductUpdate):
    product_db = await get_product_by_id(session=session, product_id=product_id)
    if not product_db:
        raise HTTPException(
            status_code=404,
            detail='Продукт не найден',
        )
    
    updated_product = await update_product_repo(
        session=session,
        product_db=product_db,
        product_update=product_data,
    )
    return updated_product