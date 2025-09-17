# Работа с CRUD API

# Подготовка проекта

# Задание № 3 - создать виртуальное окружение и сохранить зависимости проекта
'''
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn
pip freeze > requirements.txt
'''

# -------------------------------------------------------------------------------------------------------------

# Работа с schemas.py

# Задание № 4 - реализовать класс ProductCreate

from pydantic import BaseModel, Field

# схема для создания товара
class ProductCreate(BaseModel):
    # обязательное поле длиной от 1 до 200 символов
    name: str = Field(min_length=1, max_length=200)
    # необязательное поле, может быть строкой или объектом None
    description: str | None = None
    # обязательное поле, цена должна быть > 0
    price: float = Field(gt=0)
    # необязательное поле, по умолчанию True (если клиент не прислал - считаем, что товар "в наличии")
    in_stock: bool = True

# Задание № 5 - реализовать класс Product

# схема ответа (что возвращаем клиенту), наследуемся от ProductCreate
class Product(ProductCreate):
    # ID добавляем только в ответ клиенту (генерируется на стороне БД)
    id: int

# Задание № 6 - реализовать класс ProductUpdate

# схема для обновления данных о товаре
class ProductUpdate(BaseModel):
    # все поля опциональны - клиент может прислать только то, что хочет изменить
    # если поле не прислано вовсе - оно считается 'unset', важно для будущего эндпоинта
    # default=None - поле может быть передано как null
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    # значение по умолчанию делаем None, а не True, чтобы при PATCH-запросе, если клиент
    # не прислал in_stock, оно не считалось присланным как True, что может привести к путанице
    in_stock: bool | None = None

# -------------------------------------------------------------------------------------------------------------

# Работа с data_store.py

# Задание № 7 - реализовать класс DataStore

from schemas import Product

# класс для реализации хранилища товаров
class DataStore:
    def __init__(self):
        # инициализация словаря с товарами и счетчика ID
        self.products: dict[int, Product] = {}
        self.current_id: int = 1
    
    # метод для увеличения значения счетчика ID на 1
    def next_id(self) -> int:
        value = self.current_id
        self.current_id += 1
        return value

# создаем экземпляр DataStore
store = DataStore()

# -------------------------------------------------------------------------------------------------------------

# Работа с main.py

# Задание № 8 - прописать необходимые начальные импорты (все, кроме List и HTTPException) 
from fastapi import FastAPI, HTTPException
from typing import List
# подключаем все компоненты из созданных ранее модулей
from schemas import ProductCreate, Product, ProductUpdate
from data_store import store

app = FastAPI()

# Задание № 12 - реализовать вспомогательную функцию get_product_or_404()
# вспомогательная функция для получения товара по ID (если товара нет - возвращает статус 404)
def get_product_or_404(product_id: int) -> Product:
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

# Задание № 9 - реализовать эндпоинт root()
# эндпоинт для обработки GET-запроса к корневому элементу (базовая проверка работы приложения)
@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

# Задание № 10 - реализовать эндпоинт create_product()
# эндпоинт для обработки POST-запроса на создание нового товара
# response_model - определяет структуру ответа, возвращаемого эндпоинтом
@app.post('/products', response_model=Product)
def create_product(product_data: ProductCreate):
    # передаем в модель значения полей для создания нового товара
    product = Product(id=store.next_id(), **product_data.model_dump())
    store.products[product.id] = product
    return product

# Задание № 11 - подключить typing.List и реализовать эндпоинт get_products_list()
# эндпоинт для получения списка со всеми товарами
@app.get('/products', response_model=List[Product])
def get_products_list():
    return list(store.products.values())

# Задание № 13 - реализовать эндпоинт get_product()
# эндпоинт для обработки GET-запроса на получение товара по ID
@app.get('/products/{product_id}', response_model=Product)
def get_product(product_id: int):
    return get_product_or_404(product_id)

# Задание № 14 - реализовать эндпоинт put_product()
# эндпоинт для обработки PUT-запроса на полную замену данных о товаре по ID
@app.put('/products/{product_id}', response_model=Product)
def put_product(product_id: int, product_data: ProductCreate):
    # проверка наличия товара (если нет - функция завершит свою работу)
    _ = get_product_or_404(product_id)
    updated = Product(id=product_id, **product_data.model_dump())
    store.products[product_id] = updated
    return updated

# Задание № 15 - реализовать эндпоинт patch_product()
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

# Задание № 16 - реализовать эндпоинт delete_product()
# эндпоинт для обработки DELETE-запроса на удаление данных о товаре по ID
@app.delete('/products/{product_id}')
def delete_product(product_id: int):
    _ = get_product_or_404(product_id)
    del store.products[product_id]
    return {'message': 'Товар удален'}