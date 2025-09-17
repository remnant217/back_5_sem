from fastapi import FastAPI, Query
from typing import List

app = FastAPI()

@app.get('/users')
def get_default_user():
    return {'info': 'Информация о пользователе'}

@app.get('/users/{user_id}')
def get_user(user_id: int):
    return {'user_id': user_id}

@app.get('/search')
def search_items(q: str):
    return {'query': q}

@app.get('/books')
def get_books(genre: str = 'fiction', limit: int = 7):
    return {'genre': genre, 'limit': limit}

@app.get('/tags')
def get_tags(tag: List[str] = Query(...)):
    return {'tags': tag}

@app.get('/items/')
def read_items(q: str = Query(
    default='python',   # значение по умолчанию
    min_length=3,       # минимальная длина строки
    max_length=50,      # максимальная длина строки
    description='Поисковый запрос'  # описание эндпоинта, появится в Swagger-документации
)):
    return {'q': q}

# from fastapi import FastAPI, Query
# # класс Optional обозначает, что может быть либо заданного типа, либо None
# from typing import Optional

# app = FastAPI()

# # словарь со статьями
# articles_data = {
#     'science': [
#         {'title': 'Что такое квазары?', 'author': 'Петров', 'length': 36},
#         {'title': 'Нобелевские лауреаты 2025', 'author': 'Крылова', 'length': 18}
#     ],
#     'tech': [
#         {'title': 'Python 4.0 — чего ждать?', 'author': 'Косенко', 'length': 20},
#         {'title': 'История FastAPI', 'author': 'Яковлев', 'length': 13}
#     ],
#     'culture': [
#         {'title': 'Современное искусство', 'author': 'Михеева', 'length': 29}
#     ]
# }

# # эндпоинт для получения информации о статьях
# @app.get('/articles/{category}')
# def get_articles(
#     # категория статьи в виде строки
#     category: str,
#     # автор статьи (может отсутствовать в запросе)
#     author: Optional[str] = Query(None, description='Автор статьи'),
#     # минимальная длина статьи (может отсутствовать в запросе)
#     min_length: Optional[int] = Query(0, ge=0, description='Минимальная длина статьи (в страницах)')
# ):
#     # если категории нет в словаре
#     if category not in articles_data:
#         return {'error': 'Категория статьи не найдена'}
    
#     # извлекаем список статей из словаря по переданной категории
#     filtered = articles_data[category]

#     # если указан автор - фильтруем статьи по автору
#     if author:
#         filtered = [a for a in filtered if a['author'] == author]
#     # если min_length > 0 - фильтруем статьи по длине
#     if min_length:
#         filtered = [a for a in filtered if a['length'] >= min_length]
    
#     # возвращаем итоговый ответ
#     return {
#         'category': category,
#         'filters': {'author': author, 'min_length': min_length},
#         'results': filtered
#     }