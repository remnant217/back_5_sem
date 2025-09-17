# Роутеры и организация кода

# Знакомство с APIRouter

# Задание № 1 - написать отдельный модуль с использованием роутеров

# подключаем класс APIRouter
from fastapi import APIRouter

router = APIRouter(
    # prefix - общий путь для всех маршрутов роутера 
    prefix='/products', # все маршруты в роутере будут начинаться с /products
    # tags - метка, по которой маршруты будут сгруппированы в Swagger UI
    tags=['Products']
)

# обработка GET-запроса по пути /products/
@router.get('/')
def get_product():
    return {'id': 123, 'name': 'Название продукта'}

# обработка POST-запроса по пути /products/
@router.post('/')
def create_product():
    return {'message': 'Продукт создан'}

# Задание № 2 - подключить роутер к файлу main.py

from fastapi import FastAPI
# подключаем модуль с роутером
from routers import products

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'API работает'}

# include_router() - метод для подключения роутера
app.include_router(products.router)

# -------------------------------------------------------------------------------------------------------------

# Перенос CRUD-операций в роутер

# Задание № 3 - создать в проекте product_catalog папку routers и файл products.py

'''
product_catalog/
├── main.py
├── data_store.py
├── schemas.py
└── routers/
    └── products.py
'''

# Задание № 4 - создать объект router в модуле products.py 

from fastapi import APIRouter

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

# Задание № 5 - перенести вспомогательную функцию get_product_or_404() в products.py

from fastapi import HTTPException
from schemas import Product
from data_store import store

def get_product_or_404(product_id: int) -> Product:
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

# Задание № 6 - перенести все CRUD-эндпоинты из main.py в products.py

from typing import List
from fastapi import Query
from schemas import ProductCreate, ProductUpdate

# обработка POST-запроса на создание товара по маршруту '/products'
@router.post('', response_model=Product)
def create_product(product_data: ProductCreate):
    product = Product(id=store.next_id(), **product_data.model_dump())
    store.products[product.id] = product
    return product

# обработка GET-запроса на получение списка товаров по маршруту '/products'
@router.get('/products', response_model=List[Product])
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

# обработка GET-запроса на получение товара по маршруту '/products/{product_id}'
@router.get('/{product_id}', response_model=Product)
def get_product(product_id: int):
    return get_product_or_404(product_id)

# обработка PUT-запроса на полное обновление товара по маршруту '/products/{product_id}'
@router.put('/{product_id}', response_model=Product)
def put_product(product_id: int, product_data: ProductCreate):
    _ = get_product_or_404(product_id)
    updated = Product(id=product_id, **product_data.model_dump())
    store.products[product_id] = updated
    return updated

# обработка PATCH-запроса на частичное обновление товара по маршруту '/products/{product_id}'
@router.patch('/{product_id}', response_model=Product)
def patch_product(product_id: int, product_data: ProductUpdate):
    current = get_product_or_404(product_id)
    updates = product_data.model_dump(exclude_unset=True)
    product_data_updated = current.model_copy(update=updates)
    store.products[product_id] = product_data_updated
    return product_data_updated

# обработка DELETE-запроса на удаление товара по маршруту '/products/{product_id}'
@router.delete('/{product_id}')
def delete_product(product_id: int):
    _ = get_product_or_404(product_id)
    del store.products[product_id]
    return {'message': 'Товар удален'}

# Задание № 7 - подключаем роутер из products.py к main.py

from fastapi import FastAPI
# подключаем роутер для работы с товарами
from routers import products

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

# подключаем роутер
app.include_router(products.router)

# -------------------------------------------------------------------------------------------------------------

# Модификация роутера и хранилища данных

# Задание № 8 - дополнить код класса DataStore

from schemas import Product, ProductCreate, ProductUpdate

class DataStore:
    # инициализация словаря с товарами и счетчика ID
    def __init__(self):
        self.products: dict[int, Product] = {}
        self.current_id: int = 1
    
    # метод для увеличения значения счетчика ID на 1
    def next_id(self) -> int:
        value = self.current_id
        self.current_id += 1
        return value

    # создание нового продукта
    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(id=self.next_id(), **product_data.model_dump())
        self.products[product.id] = product
        return product
    
    # получение списка товаров с фильтрацией
    def get_products_list(
        self,
        q: str = None,
        in_stock: bool = None,
        min_price: float = None,
        max_price: float = None
    ) -> list[Product]:
        
        result = list(self.products.values())

        if q is not None:
            q_low = q.lower()
            result = [p for p in result if q_low in p.name.lower()]
        
        if in_stock is not None:
            result = [p for p in result if p.in_stock == in_stock]
        
        if min_price is not None:
            result = [p for p in result if p.price >= min_price]
        
        if max_price is not None:
            result = [p for p in result if p.price <= max_price]

        return result
    
    # получение товара по ID
    def get_product(self, product_id: int) -> Product | None:
        return self.products.get(product_id)
    
    # полное обновление товара
    def put_product(self, product_id: int, product_data: ProductCreate) -> Product:
        updated = Product(id=product_id, **product_data.model_dump())
        self.products[product_id] = updated
        return updated
    
    # частичное обновление товара
    def patch_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        current = get_product_or_404(product_id)
        updates = product_data.model_dump(exclude_unset=True)
        product_data_updated = current.model_copy(update=updates)
        self.products[product_id] = product_data_updated
        return product_data_updated
    
    # удаление товара
    def delete_product(self, product_id: int) -> None:
        del self.products[product_id]

# Задание № 9 - модифицировать файл products.py

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