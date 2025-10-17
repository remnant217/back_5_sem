from contextlib import asynccontextmanager
from fastapi import FastAPI
# импортируем класс TVMazeClient из созданного ранее модуля
from tv_client import TVMazeClient
from tv_router import router

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

app.include_router(router)