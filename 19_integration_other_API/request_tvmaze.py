'''
Если у вас не установлена библиотека requests, то выполните в терминале:
pip install requests
'''

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