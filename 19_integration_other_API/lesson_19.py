# Интеграция с внешними API

# Задание № 1 - написать эндпоинт для обращения к внешнему API через requests

from fastapi import FastAPI
import requests

app = FastAPI()

# получаем данные о всех шоу с указанным названием
@app.get('/search')
async def sync_search_shows(q: str):
    # отправляем GET-запрос к TVMaze и получаем ответ
    response = requests.get(
        url='https://api.tvmaze.com/search/shows',
        params={'q': q}
    )
    # возвращаем ответ в формате JSON
    return response.json()

# ---------------------------------------------------------------------------------------------------------

# Работа с httpx

# Задание № 2 - переписать код с использованием httpx

from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

@app.get('/search')
async def async_search_shows(q: str):
    try:
        # открываем асинхронный контекстный менеджер клиента
        # при выходе созданные соединения будут автоматически закрыты
        async with httpx.AsyncClient() as client:
            # отправляем неблокирующий GET-запрос и получаем ответ
            response = await client.get(
                url='https://api.tvmaze.com/search/shows',
                params={'q': q}
            )
            # если код ответа 4xx/5xx - выбросим исключение httpx.HTTPStatusError
            # удобно для единой реакции на статусы 4xx/5xx
            response.raise_for_status()
            return response.json()
    # если превышен таймаут - возвращаем статус 504 Gateway Timeout
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail='TVMaze timeout')
    # ловим исключения, выброшенные через raise_for_status()
    except httpx.HTTPStatusError as exc:
        # показываем статус-код и текст исключения
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

# ---------------------------------------------------------------------------------------------------------

# Использование одного клиента во всем приложении

# Задание № 3 - реализовать файл tv_client.py

import httpx

# базовый URL TVMaze API, в дальнейшем можно дополнять для разных эндпоинтов
TVMAZE_BASE = 'https://api.tvmaze.com'

# класс-обертка над httpx.AsyncClient
class TVMazeClient:
    def __init__(self):
        # создаем и настраиваем экземпляр httpx.AsyncClient
        # можно настраивать много параметров, нам хватит пока base_url
        self._client = httpx.AsyncClient(
            base_url=TVMAZE_BASE   # URL, использующийся как основа при построении URL в запросах
        )

    # закрываем клиент при завершении работы
    async def close(self):
        await self._client.aclose()
    
    # получаем список шоу по указанному названию
    async def search_shows(self, film_name: str) -> list[dict]:
        response = await self._client.get(
            url='/search/shows',    # указываем более короткую версию URL за счет base_url в _client
            params={'q': film_name}
        )
        response.raise_for_status()
        return response.json()


# Задание № 4 - частично реализовать файл main.py

# asynccontextmanager - декоратор для создания асинхронного контекстного менеджера из обычной корутины
from contextlib import asynccontextmanager
from fastapi import FastAPI
# импортируем класс TVMazeClient из созданного ранее модуля
from tv_client import TVMazeClient

# определяем функцию, которую FastAPI будет вызывать при запуске и корректно завершать 
# при остановке приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # создаем экзмемпляр класса TVMazeClient и кладем в app.state (общий контейнер для ресурсов приложения)
    # так клиент будет один на все приложение, что хорошо экономит ресурсы
    app.state.tv_client = TVMazeClient()
    # после создания клиента приложение живет своей жизнью
    try:
        yield
    # закрываем клиент при остановке приложения
    finally:
        await app.state.tv_client.close()

# подключаем созданный lifespan-менеджер через параметр lifespan
app = FastAPI(lifespan=lifespan)


# Задание № 5 - реализовать файл tv_router.py

from fastapi import APIRouter, Request, HTTPException, Depends
import httpx

from tv_client import TVMazeClient

# роутер для эндпоинтов, работающих с TVMaze
router = APIRouter(prefix='/tv')

# функция-зависимость для работы с клиентом TVMazeClient
def get_tvmaze_client(request: Request) -> TVMazeClient:
    # возвращаем общий экземпляр TVMazeClient, который мы ранее положили 
    # в app.state.tv_client при старте приложения через lifespan
    return request.app.state.tv_client

# получение списка шоу по указанному названию
@router.get('/search')
async def search_shows(q: str, client: TVMazeClient = Depends(get_tvmaze_client)):
    # обращаемся к внешнему API и получаем список шоу
    try:
        return await client.search_shows(film_name=q)
    # обрабатываем исключения при таймаутах и статусах 4xx/5xx
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail='TVMaze timeout')
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)


# Задание № 6 - закончить реализацию файла main.py

...
from tv_router import router

...
app.include_router(router)