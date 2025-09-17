from fastapi import FastAPI, HTTPException, Query
from typing import List
from schemas import ProductCreate, Product, ProductUpdate
from data_store import store

app = FastAPI()

def get_product_or_404(product_id: int) -> Product:
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

@app.post('/products', response_model=Product)
def create_product(product_data: ProductCreate):
    product = Product(id=store.next_id(), **product_data.model_dump())
    store.products[product.id] = product
    return product

@app.get('/products', response_model=List[Product])
def get_products_list(
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена')
):
    result = list(store.products.values())

    if q is not None:
        q_low = q.lower()
        result = [p for p in result if q_low in p.name.lower()]
    
    if in_stock is not None:
        result = [p for p in result if p.in_stock is in_stock]
    
    if min_price is not None:
        result = [p for p in result if p.price >= min_price]
    
    if max_price is not None:
        result = [p for p in result if p.price <= max_price]
    
    return result

@app.get('/products/{product_id}', response_model=Product)
def get_product(product_id: int):
    return get_product_or_404(product_id)

@app.put('/products/{product_id}', response_model=Product)
def put_product(product_id: int, product_data: ProductCreate):
    _ = get_product_or_404(product_id)
    updated = Product(id=product_id, **product_data.model_dump())
    store.products[product_id] = updated
    return updated

@app.patch('/products/{product_id}', response_model=Product)
def patch_product(product_id: int, product_data: ProductUpdate):
    current = get_product_or_404(product_id)
    updates = product_data.model_dump(exclude_unset=True)
    product_data_updated = current.model_copy(update=updates)
    store.products[product_id] = product_data_updated
    return product_data_updated

@app.delete('/products/{product_id}')
def delete_product(product_id: int):
    _ = get_product_or_404(product_id)
    del store.products[product_id]
    return {'message': 'Товар удален'}