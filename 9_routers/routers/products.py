from fastapi import APIRouter, HTTPException, Query
from schemas import Product, ProductUpdate, ProductCreate
from data_store import store
from typing import List

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

def get_product_or_404(product_id: int) -> Product:
    # вызываем метод get_product()
    product = store.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

@router.post('', response_model=Product)
def create_product(product_data: ProductCreate):
    # оставляем только вызов метода create_product()
    return store.create_product(product_data)

# обработка GET-запроса на получение списка товаров по маршруту '/products'
@router.get('/products', response_model=List[Product])
def get_products_list(
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена')
):
    # оставляем только вызов метода get_products_list()
    return store.get_products_list(q, in_stock, min_price, max_price)

# эндпоинт остается в прежнем виде
@router.get('/{product_id}', response_model=Product)
def get_product(product_id: int):
    return get_product_or_404(product_id)

@router.put('/{product_id}', response_model=Product)
def put_product(product_id: int, product_data: ProductCreate):
    # оставляем только проверку наличия в базе и put_product()
    _ = get_product_or_404(product_id)
    return store.put_product(product_id, product_data)

@router.patch('/{product_id}', response_model=Product)
def patch_product(product_id: int, product_data: ProductUpdate):
    # оставляем только проверку наличия в базе и patch_product()
    _ = get_product_or_404(product_id)
    return store.patch_product(product_id, product_data)

@router.delete('/{product_id}')
def delete_product(product_id: int):
    _ = get_product_or_404(product_id)
    # вызываем метод delete_product()
    store.delete_product(product_id)
    return {'message': 'Товар удален'}