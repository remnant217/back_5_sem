from time import perf_counter
from fastapi import FastAPI, Request
from loguru import logger

# функция-обертка для запуска middleware
def setup_middleware(app: FastAPI):
    # создаем middleware для добавления времени выполнения запроса в заголовок ответа
    @app.middleware('http')
    async def add_process_time_header(request: Request, call_next):
        start_time = perf_counter()
        response = await call_next(request)
        # вычисляем время работы запроса в милисекундах
        process_time = (perf_counter() - start_time) * 1000
        logger.info(f'{request.method} {request.url.path} выполнялся {process_time:.2f} мс')
        response.headers['X-Process-Time-ms'] = f'{process_time:.2f}'
        return response