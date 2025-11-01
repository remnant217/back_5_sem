# Роутеры и организация кода

'''
План урока:
1) Введение и повторение кода с предыдущего занятия
2) Знакомство с APIRouter
3) Перенос CRUD-операций в роутер
4) Модификация роутера и хранилища данных
5) Заключение
'''

# -------------------------------------------------------------------------------------------------------------

# Введение и повторение кода с предыдущего занятия
'''
На прошлом занятии мы с вами сделали полноценный CRUD API для каталога товаров.
У нас есть добавление, получение, обновление, удаление товара 
и даже фильтрация списка по цене, наличию и поиску по подстроке, которую вы делали в рамках домашнего задания.

СОВЕТ ПРЕПОДАВАТЕЛЮ: если на предыдущем занятии вы не успели реализовать все эндпоинты
или кто-то из студентов не выполнил ДЗ с предыдущего занятия - крайне рекомендуется выделить время
и дописать программный код. Итоговый код для данного этапа можно найти в папке product_catalog_lesson_8.
Также рекомендуется напомнить студентам логику работы приложения через запуск эндпоинтов в Swagger UI.

А теперь представим, что в нашем проекте появятся новые разделы - например, обработка заказов 
и информация о пользователях. Конечно, можно добавить соответствующие CRUD-операции в имеющийся main.py,
но тогда этот файл станет огромным и будет сложно найти нужный эндпоинт. На предыдущих занятиях мы уже 
учились разбивать код на отдельные слои и модули, чтобы он был понятнее и проще в поддержке.
В FastAPI для этого есть специальный инструмент - роутеры, с помощью которых сегодня
мы научимся делить API на отдельные логические блоки.
'''

# -------------------------------------------------------------------------------------------------------------

# Знакомство с APIRouter

'''
APIRouter - специальный объект в FastAPI, который помогает группировать связанные маршруты
в отдельные файлы или модули. Работает как мини-приложение внутри большого приложения.

Код без роутеров:
- Один большой main.py - сложно искать нужный код
- Все ресурсы (товары, заказы, пользователи и т.д.) перемешаны
- Повышается вероятность сломать что-нибудь при редактировании

Код с роутерами:
- main.py - точка запуска приложения и подключение роутеров
- Логика работы с ресурсами вынесена в отдельные файлы (например, products.py, orders.py и users.py)
- Можно подключить новый роутер одной строчкой
- Можно тестировать отдельные модули API

Представьте, что код без роутеров - это огромный магазин, где перемешаны самые разные товары - еда, одежда,
книги, строительные инструменты и все без разделения на отделы. Код с роутерами в свою очередь 
похож на торговый центр, где main.py - вход в здание, а роутеры - разделы с конкретными товарами.

СОВЕТ ПРЕПОДАВАТЕЛЮ: для кода ниже лучше создать отдельную папку с проектом. 
Цель кода - на простом примере показать создание и подключение роутера.
Код также можно найти в папке routers_demo.

Посмотрим на небольшой пример работы с роутерами. Создадим отдельную папку routers, а внутри файл products.py.
В файле пропишем простую логику работы с товарами:
'''
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

'''
Теперь создадим файл main.py и подключим модуль products.py:
'''

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

'''
Теперь весь код для работы с товарами лежит в routers/products.py.
В main.py достаточно написать app.include_router() для подключения роутера.
В Swagger UI эндпоинты сгруппированы в раздел Products.
'''

# -------------------------------------------------------------------------------------------------------------

# Перенос CRUD-операций в роутер
'''
СОВЕТ ПРЕПОДАВАТЕЛЮ: далее в уроке большую часть времени вы будете редактировать уже существующий код.
Крайне рекомендуется задействовать студентов и проверять, все ли успели отредактировать код.
Не забывайте периодически показывать текущее состояние всего кода, чтобы студенты могли сравнить
свою работу с вашей для самопроверки. Итоговый код, который получится к концу данного занятия,
можно найти в папке product_catalog_lesson_9.

Сейчас мы будем модифицировать код с предыдущего занятия, а конкретно - выносить логику работы с товарами
в отдельный модуль. Добавим в проект папку routers, внутри которой создадим файл products.py.
'''

# Задание № 3 - создать в проекте product_catalog папку routers и файл products.py

'''
product_catalog/
├── main.py
├── data_store.py
├── schemas.py
└── routers/
    └── products.py

В модуле products.py создадим объект router и укажем соответствующие параметры:
'''

# Задание № 4 - создать объект router в модуле products.py 

from fastapi import APIRouter

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

'''
Перенесем вспомогательную функцию get_product_or_404() в products.py,
т.к. эта функция работает с товарами.
'''

# Задание № 5 - перенести вспомогательную функцию get_product_or_404() в products.py

from fastapi import HTTPException
from schemas import Product
from data_store import store

def get_product_or_404(product_id: int) -> Product:
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

'''
Теперь по одному перенесем все CRUD-эндпоинты из main.py в products.py.
Не забывайте, что декораторы будут претерпевать изменения:
- app меняем на router
- в пути убираем '/products', т.к. есть prefix='/products'
'''

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

'''
В main.py остается только базовый код и подключение роутера:
'''

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

'''
Теперь main.py не содержит CRUD-операции, а подключает роутеры.
Если появятся дополнительные роутеры - их можно без проблем подключить в main.py.
'''

# -------------------------------------------------------------------------------------------------------------

# Модификация роутера и хранилища данных
'''
Посмотрим внимательнее на routes/products.py. Внутри эндпоинтов довольно много работы со словарем products,
то есть с хранилищем данных. Это не очень хорошо, т.к. роутер должен отвечать за работу с HTTP-протоколом, 
остальная логика должна быть в других слоях. Лучше вынести логику работы с хранилищем в уже имеющийся
модуль data_store, а именно в класс DataStore, и вот почему:
1. Переиспользование
Если нужно будет использовать созданную логику вне FastAPI, то можно вызывать методы DataStore.
2. Масштабирование
Если нужно переходить на базу данных, то достаточно переписать код DataStore, код роутеров глобально не изменится.
3. Тестирование
Проще писать тесты для DataStore (без запуска FastAPI), логика API тестируется отдельно.

Таким образом, роутер будет "прослойкой" между клиентом (HTTP) и хранилищем данных (DataStore).

Дополним код класса DataStore, прописывая соответствующие методы с логикой создания, получения,
модификации и удаления товаров:
'''

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

'''
Модифицируем модуль products.py, удалив логику, вынесенную в класс DataStore:
'''

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

'''
Теперь роутер только принимает запрос и вызывает соответствующий метод хранилища.
Вся логика по работе с данными находится в DataStore.
Можно заметить, что названия методов класса DataStore и функций в products.py совпадают.
Но важно помнить, что данные функции и методы работают на разных уровнях:
- В роутере - обработчик HTTP-запросов
- В DataStore - работа с данными.
'''