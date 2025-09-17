# подключение необходимых функций и классов
from fastapi import FastAPI, Query
from typing import Optional

# создаем объект приложения
app = FastAPI()

# словарь с данными о фильмах
movies_data = {
    'action': [
        {'title': 'Безумный Макс', 'year': 2015, 'rating': 8.1},
        {'title': 'Джон Уик', 'year': 2014, 'rating': 7.4}
    ],
    'drama': [
        {'title': 'Крестный отец', 'year': 1972, 'rating': 9.2},
        {'title': 'Форрест Гамп', 'year': 1994, 'rating': 8.8}
    ],
    'comedy': [
        {'title': 'Маска', 'year': 1994, 'rating': 6.9},
        {'title': 'Назад в будущее', 'year': 1985, 'rating': 8.5}
    ]
}

# эндпоинт для получения списка фильмов по указанному жанру
@app.get('/movies/{genre}')
def get_movies(
    genre: str,  
    min_rating: float = Query(0.0, ge=0.0, le=10.0),    
    year: Optional[int] = Query(None, ge=1900, le=2025)
):
    # если указанный жанр не найден
    if genre not in movies_data:
        return {'error': 'Жанр не найден'}
    
    # фильтруем фильмы по жанру
    filtered = movies_data[genre]

    # фильтруем фильмы по рейтингу
    filtered = [m for m in filtered if m['rating'] >= min_rating]

    # фильтруем фильмы по году
    if year is not None:
        filtered = [m for m in filtered if m['year'] == year]
    
    return filtered

# эндпоинт для получения информации о фильме по жанру и названию
@app.get('/movies/{genre}/{title}')
def get_movie(
    genre: str,
    title: str
):
    # если указанный жанр не найден
    if genre not in movies_data:
        return {'error': 'Жанр не найден'}
    
    # приводим название к нижнему регистру
    title_lower = title.lower()

    # ищем фильм по названию
    for movie in movies_data[genre]:
        if movie['title'].lower() == title_lower:
            return movie
    
    # если фильм не был найден
    return {'error': 'Фильм не найден'}