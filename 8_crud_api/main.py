from fastapi import FastAPI, HTTPException
from schemas import ProductCreate, Product, ProductUpdate
from data_store import store
from typing import List

app = FastAPI()

# функция для получения товара по ID (если товара нет - возвращается статус 404)
def get_product_or_404(product_id: int) -> Product:
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

# эндпоинт для обработки POST-запроса на создание нового товара
# response_model - определяет структуру ответа, возвращаего эндпоинтом
@app.post('/products', response_model=Product)
def create_product(product_data: ProductCreate):
    product = Product(id=store.next_id(), **product_data.model_dump())
    store.products[product.id] = product
    return product

# эндпоинт для получения списка со всеми товарами
@app.get('/products', response_model=List[Product])
def get_products_list():
    return list(store.products.values())

# эндпоинт для обработки GET-запроса на получение товара по ID
@app.get('/products/{product_id}', response_model=Product)
def get_product(product_id: int):
    return get_product_or_404(product_id)

# эндпоинт для обработки PUT-запроса на полную замену данных о товаре по ID
@app.put('/products/{product_id}', response_model=Product)
def put_product(product_id: int, product_data: ProductCreate):
    # проверка наличия товара (если нет - функция завершит свою работу)
    _ = get_product_or_404(product_id)
    updated = Product(id=product_id, **product_data.model_dump())
    store.products[product_id] = updated
    return updated

# эндпоинт для обработки PATCH-запроса на частичное обновление данных о товаре по ID
@app.patch('/products/{product_id}', response_model=Product)
def patch_product(product_id: int, product_data: ProductUpdate):
    current = get_product_or_404(product_id)
    # exclude_unset=True - меняем только присланные поля
    updates = product_data.model_dump(exclude_unset=True)
    # model_copy() - возвращает копию Pydantic-модели
    product_data_updated = current.model_copy(update=updates)
    store.products[product_id] = product_data_updated
    return product_data_updated

# эндпоинт для обработки DELETE-запроса на удаление данных о товаре по ID
@app.delete('/products/{product_id}')
def delete_product(product_id: int):
    _ = get_product_or_404(product_id)
    del store.products[product_id]
    return {'message': 'Товар удален'}