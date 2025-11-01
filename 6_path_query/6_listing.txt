# Параметры запроса: Path и Query

# Path-параметры

# Задание № 1 - создать виртуальное окружение проекта, установить библиотеки 
# и объявить экземпляр класса FastAPI в коде
'''
python -m venv venv
venv\scripts\activate
pip install fastapi uvicorn
'''

from fastapi import FastAPI

app = FastAPI()

# Задание № 2 - создать и протестировать эндпоинт с одним Path-параметром

@app.get('/users/{user_id}')
def get_user(user_id: int):
    return {'user_id': user_id}

# Задание № 3 - создать и протестировать эндпоинт с несколькими Path-параметрами

@app.get('/orders/{user_id}/items/{item_id}')
def get_order_item(user_id: int, item_id: int):
    return {'user_id': user_id, 'item_id': item_id}

# Ограничения и особенности Path-параметров

# Задание № 4 - FastAPI не позволяет определять маршруты с одинаковой структурой

# Как не стоит делать:

# получаем пользователя по ID
@app.get('/users/{id}')
def get_user_by_id(id: int):
    return {'id': id}

# получаем пользователя по номеру (num)
@app.get('/users/{num}')
def get_user_by_num(num: int):
    return {'num': num}

# Как лучше делать:

@app.get('/users/by-id/{id}')
def get_user_by_id(id: int):
    return {'id': id}

@app.get('/users/by-num/{num}')
def get_user_by_num(num: int):
    return {'num': num}

# Задание № 5 - конфликт между path-параметрами и статичными путями

# Как не стоит делать:

# получаем пользователя по ID
@app.get('/users/{user_id}')
def get_user(user_id: int):
    return {'user_id': user_id}

# получаем список новых пользователей
@app.get('/users/new')
def get_new_users():
    return {'Список новых пользователей': ['Миша', 'Дима', 'Аня']}

# Задание № 6 - отсутствие значений по умолчанию

# Как не стоит делать:

@app.get('/users/{user_id}')
def get_user(user_id: int = 1):
    return {'user_id': user_id}

# Как лучше делать:

@app.get('/users')
def get_default_user():
    return {'info': 'Информация о пользователе'}

@app.get('/users/{user_id}')
def get_user(user_id: int):
    return {'user_id': user_id}

# -------------------------------------------------------------------------------------------------------------

# Query-параметры

# Задание № 7 - создать и протестировать эндпоинт с одним Query-параметром

@app.get('/search')
def search_items(q: str):
    return {'query': q}

# Задание № 8 - создать и протестировать эндпоинт со значениями Query-параметров по умолчанию

@app.get('/books')
def get_books(genre: str = 'fiction', limit: int = 7):
    return {'genre': genre, 'limit': limit}

# Задание № 9 - познакомиться с функцией fastapi.Query() и классом typing.List

# подключаем функцию Query для явного описания query-параметров 
from fastapi import Query
# подключаем класс List для указания, что в списке должны быть элементы определенного типа
from typing import List

@app.get('/tags')
def get_tags(tag: List[str] = Query(...)):
    return {'tags': tag}

# Задание № 10 - рассмотреть пример fastapi.Query() со значением по умолчанию и описанием 

@app.get('/items/')
def read_items(q: str = Query(
    default='python',   # значение по умолчанию
    min_length=3,       # минимальная длина строки
    max_length=50,      # максимальная длина строки
    description='Поисковый запрос'  # описание эндпоинта, появится в Swagger-документации
)):
    return {'q': q}

# -------------------------------------------------------------------------------------------------------------

# Практическое задание с Path- и Query-параметрами

# Задание № 11 - выполнить практическое задание на создание FastAPI-приложения 
# с эндпоинтом для обработки словаря с данными о статьях
'''
Необходимо создать FastAPI-приложение, которое:
- содержит словарь с данными о статьях (категория, название, автор, кол-во страниц)
- позволяет получать список статей по заданной категории
- позволяет фильтровать статьи по автору и минимальному кол-ву страниц

Полный код с решением выглядит следующим образом:
'''
from fastapi import FastAPI, Query
# класс Optional обозначает, что значение может быть либо заданного типа, либо None
from typing import Optional

app = FastAPI()

# словарь со статьями
articles_data = {
    'science': [
        {'title': 'Что такое квазары?', 'author': 'Петров', 'length': 36},
        {'title': 'Нобелевские лауреаты 2025', 'author': 'Крылова', 'length': 18}
    ],
    'tech': [
        {'title': 'Python 4.0 — чего ждать?', 'author': 'Косенко', 'length': 20},
        {'title': 'История FastAPI', 'author': 'Яковлев', 'length': 13}
    ],
    'culture': [
        {'title': 'Современное искусство', 'author': 'Михеева', 'length': 29}
    ]
}

# эндпоинт для получения информации о статьях
@app.get('/articles/{category}')
def get_articles(
    # категория статьи в виде строки
    category: str,
    # автор статьи (может отсутствовать в запросе)
    author: Optional[str] = Query(None, description='Автор статьи'),
    # минимальная длина статьи (может отсутствовать в запросе)
    min_length: Optional[str] = Query(0, ge=0, description='Минимальная длина статьи (в страницах)')
):
    # если категории нет в словаре
    if category not in articles_data:
        return {'error': 'Категория статьи не найдена'}
    
    # извлекаем список статей из словаря по переданной категории
    filtered = articles_data[category]

    # если указан автор - фильтруем статьи по автору
    if author:
        filtered = [a for a in filtered if a['author'] == author]
    # если min_length > 0 - фильтруем статьи по длине
    if min_length:
        filtered = [a for a in filtered if a['length'] >= min_length]
    
    # возвращаем итоговый ответ
    return {
        'category': category,
        'filters': {'author': author, 'min_length': min_length},
        'results': filtered
    }