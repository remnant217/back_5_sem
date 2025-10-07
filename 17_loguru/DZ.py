from fastapi import FastAPI, Depends, Request
from typing import Annotated
from time import perf_counter
from loguru import logger

app = FastAPI()

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    # логирование начала работы middleware
    logger.info(f'Middleware начал работу: {request.method} {request.url.path}')
    start_time = perf_counter()
    # пробуем выполнить запрос
    try:
        response = await call_next(request)
        process_time = (perf_counter() - start_time) * 1000
        # если запрос обработан успешно
        if 200 <= response.status_code < 300:
            logger.info(f'Запрос выполнен успешно - Статус: {response.status_code}')
        # если запрос был перенаправлен
        elif 300 <= response.status_code < 400:
            logger.info(f'Перенаправление - Статус: {response.status_code}')
        # если возникла ошибка на стороне клиента
        elif 400 <= response.status_code < 500:
            logger.warning(f'Ошибка на стороне клиента - Статус: {response.status_code}')
        # если возникла ошибка на стороне сервера
        elif response.status_code >= 500:
            logger.error(f'Ошибка на стороне сервера - Статус: {response.status_code}')

        response.headers['X-Process-Time'] = f'{process_time} ms.'
        # логируем время обработки запроса
        logger.info(f'Запрос был обработан за {process_time} мс.')
        return response
    # если при выполнении запроса возникло исключение
    except Exception as e:
        process_time = perf_counter() - start_time
        # выводим сообщение о вызванном исключении
        logger.error(f'Во время обработки запроса было вызвано исключение: {e}')
        # выводим информацию о времени, спустя которое возникло исключение
        logger.info(f'Запрос завершился вызовом исключения спустя {process_time} с.')

async def get_parameters(
    q: str | None = None,
    page: int = 1,
    limit: int = 100
) -> dict:
    return {'q': q, 'page': page, 'limit': limit}

ParametersDep = Annotated[dict, Depends(get_parameters)] 

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

products_db = [
    {'product_name': 'Молоко'},
    {'product_name': 'Хлеб'},
    {'product_name': 'Телефон'},
    {'product_name': 'Куртка'}
]

@app.get('/products')
async def get_products(parameters: Annotated[QueryParameters, Depends()]):
    response = {}      
    if parameters.q:    
        response.update({'q': parameters.q})    
    products = products_db[parameters.page:parameters.page + parameters.limit]
    response.update({'products': products})     
    return response     

@app.get('/users')
async def get_users(parameters: ParametersDep):
    return parameters