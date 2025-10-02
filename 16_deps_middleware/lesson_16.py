# Зависимости и middleware

# Внедрение зависимостей в FastAPI

# Задание № 1 - создать эндпоинты get_products() и get_users() с похожей структурой 

from fastapi import FastAPI

app = FastAPI()

# получение списка товаров
@app.get('/products')
async def get_products(
    q: str | None = None,   # описание продукта
    page: int = 1,          # № страницы, с которой начинается поиск
    limit: int = 100        # ограничение на количество полученных товаров
) -> dict:
    return {'q': q, 'page': page, 'limit': limit}

# получение списка пользователей
@app.get('/users')
async def get_users(
    q: str | None = None,   # описание пользователя
    page: int = 1,          # № страницы, с которой начинается поиск
    limit: int = 100        # ограничение на количество полученных пользователей
) -> dict:
    return {'q': q, 'page': page, 'limit': limit}


# Задание № 2 - создать функцию-зависимость get_parameters()

async def get_parameters(
    q: str | None = None,
    page: int = 1,
    limit: int = 100
) -> dict:
    return {'q': q, 'page': page, 'limit': limit}


# Задание № 3 - внедрить созданную зависимость в эндпоинты

from fastapi import FastAPI, Depends

@app.get('/products')
async def get_products(parameters: dict = Depends(get_parameters)):
    return parameters

@app.get('/users')
async def get_users(parameters: dict = Depends(get_parameters)):
    return parameters


# Задание № 4 - сохранить зависимость в отдельную переменную

# Annotated - специальный класс, позволяющий указывать дополнительные метаданные в подсказках типов
from typing import Annotated

ParametersDep = Annotated[dict, Depends(get_parameters)] 

@app.get('/products')
async def get_products(parameters: ParametersDep):
    return parameters

@app.get('/users')
async def get_users(parameters: ParametersDep):
    return parameters

# ----------------------------------------------------------------------------------------------------------

# Классы как зависимости

# Задание № 5 - создать класс QueryParameters

class QueryParameters:
    def __init__(
        self,
        q: str | None = None,
        page: int = 1,
        limit: int = 100
    ):
        self.q = q
        self.page = page
        self.limit = limit


# Задание № 6 - создать список products_db

products_db = [
    {'product_name': 'Молоко'},
    {'product_name': 'Хлеб'},
    {'product_name': 'Телефон'},
    {'product_name': 'Куртка'}
]


# Задание № 7 - внедрить класс QueryParameters как зависимость в эндпоинт get_products()

@app.get('/products')
async def get_products(parameters: Annotated[QueryParameters, Depends(QueryParameters)]):
    return parameters


# Задание № 8 - обновить тело эндпоинта get_products()

@app.get('/products')
async def get_products(parameters: Annotated[QueryParameters, Depends(QueryParameters)]):
    response = {}       # словарь с ответом от API
    if parameters.q:    # если был передан параметр q
        response.update({'q': parameters.q})    # добавляем в словарь значение q
    # получаем нужные данные из products_db согласно указанным page и limit
    products = products_db[parameters.page:parameters.page + parameters.limit]
    response.update({'products': products})     # добавляем выгруженные продукты в словарь
    return response     # возвращаем ответ от API

'''
Давайте внимательно взглянем на строчке с внедрением зависимости:
'''
parameters: Annotated[QueryParameters, Depends(QueryParameters)]

'''
Видим, что класс QueryParameters указан дважды.
Важно понимать, что именно 2-е указание QueryParameters, то есть Depends(QueryParameters) - именно тут
FastAPI узнает что именно является зависимостью. Чтобы избежать такого дублирования, когда зависимость - это класс,
который FastAPI будет вызывать для создания экземпляра этого же класса, можно написать так:
'''
parameters: Annotated[QueryParameters, Depends()]

'''
В таком случае FastAPI логика кода сохранится и конструкция будет не такой громоздкой.
'''

# ----------------------------------------------------------------------------------------------------------

# Middleware в FastAPI

# Задание № 9 - создать middleware для замера времени обработки запроса 

# подключаем функцию для измерения времени работы кода
from time import perf_counter
# Request - класс для работы с содержимым HTTP-запроса  
from fastapi import FastAPI, Request

app = FastAPI()

# регистрируем middleware для всего приложения, будет срабатывать с каждым запросом 
@app.middleware('http')
# объявляем middleware-функцию, принимающую запрос и функцию call_next для дальнейшей обработки запроса
async def add_process_time_header(request: Request, call_next):
    # замеряем начало обработки запроса
    start_time = perf_counter()
    # передаем запрос для дальнейшей обработки и получаем ответ
    response = await call_next(request)
    # вычисляем длительность обработки запроса
    process_time = perf_counter() - start_time
    # добавляем в заголовки ответа заголовок X-Process-Time (является общепринятым HTTP-заголовком)
    # по стандарту HTTP заголовки передаются в виде строк
    response.headers['X-Process-Time'] = str(process_time)
    # возвращаем модифицированный ответ клиенту
    return response