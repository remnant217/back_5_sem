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