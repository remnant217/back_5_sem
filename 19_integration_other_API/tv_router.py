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