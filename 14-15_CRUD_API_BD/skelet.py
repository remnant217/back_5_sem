# Воркшоп. Разработка CRUD API с БД и валидацией
'''
Идея проекта - каталог фильмов с CRUD-операциями и хранением данных в БД.
'''

# Подготовка проекта
'''
1. Создать новую папку проекта (movies_api)
2. Создать и активировать виртуальное окружение:
python -m venv venv
venv\scripts\activate

3. Установить библиотеки:
pip install fastapi uvicorn sqlalchemy alembic aiosqlite pytest httpx

4. Сохранить зависимости в файл:
pip freeze > requirements.txt

5. Создаем базовую структуру каталогов:
movies_api/
│── requirements.txt       # зависимости
│── README.md              # описание проекта
│
├── src/                   # исходники приложения
│   ├── main.py            # точка входа
│   ├── database.py        # подключение к БД
│   ├── models/            # SQLAlchemy-модели
│   ├── schemas/           # Pydantic-схемы
│   ├── routers/           # роутеры FastAPI
│   └── repositories/      # бизнес-логика CRUD
│
└── tests/                 # тесты

6. Пропишем минимальный код для проверки запуска приложения:
'''
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Movies API готов к работе!'}

'''
7. Запустим сервер:
uvicorn src.main:app --reload

http://127.0.0.1:8000 → {"message":"Movies API готов к работе!"}
'''

# -------------------------------------------------------------------------------------------------------------

# Модель БД

'''
Создаем src/models/__init__.py
Файл __init__.py делает папку пакетом Python. Так Python будет рассматривать папку models как модуль,
из которого можно импортировать код. Для более чистой структуры проекта и облегчения работы Alembic,
внутри __init__.py создадим класс Base:
'''
from sqlalchemy.orm import DeclarativeBase

# создаем класс Base для работы с моделями
class Base(DeclarativeBase):
    pass

# чтобы Alembic увидел таблицу при генерации миграций
from .movie import Movie

# явно указываем что будет импортироваться при выполнении from src.models import *
__all__ = ['Base', 'Movie']

'''
Создаем модель Movie в файле src/models/movie.py
'''
# CheckConstraint - класс для валидации значений на уровне БД
from sqlalchemy import Column, Integer, String, Float, CheckConstraint
from . import Base

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    # index=True для ускорения поиска по заголовкам
    title = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    year = Column(Integer, nullable=False)

    __table_args__ = (
        # ограничения на рейтинг (0...10) и год выпуска фильма (>= 1888)
        # name помогает при отладке, чтении ошибок БД и работе с Alembic
        CheckConstraint('rating >= 0 AND rating <= 10', name='check_movie_rating_range'),
        CheckConstraint('year >= 1888', name='check_movie_year_ge_1888')
    )

# -------------------------------------------------------------------------------------------------------------

# БД и сессии
'''
Наполняем src/database.py 
'''
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite:///./shows.db', echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
# -------------------------------------------------------------------------------------------------------------

# Alembic
'''
Инициализация alembic:
alembic init alembic

В alembic.ini задать URL для БД (синхронный):
sqlalchemy.url = sqlite:///./movies.db

В alembic/env.py добавим путь к src и метаданные.
Когда Alembic запускает миграции, он запускает свое окружение (файлы внутри папки alembic/).
По умолчанию Python видит только саму папку alembic/ и ее родителей, но не знает, что в соседнем src/ лежат исходники приложения.
Нам нужно вручную добавить папку src/ в sys.path, чтобы Python мог импортировать src.models, src.database и другие модули:
'''
import sys, pathlib
...
# __file__ - переменная с путем к текущему файлу (env.py)
# pathlib.Path(__file__).resolve() - преобразует путь к файлу в абсолютный
# parents[1] - корень нашего проекта (папка movies_api/)
# / 'src' - к пути добавляется подпапка src
# str - превращаем путь в строку
# sys.path.append() - добавляем полученный путь в список путей модулей Python
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / 'src'))

'''
Указываем, какие модели отслеживать и по каким таблицам генерировать миграции:
'''
from src.models import Base
...
target_metadata = Base.metadata

'''
Генерируем и применяем миграцию:
alembic revision --autogenerate -m "init movies"
alembic upgrade head
'''

# -------------------------------------------------------------------------------------------------------------

# Pydantic-схемы
'''
Сначала создаем пустой src/schemas/__init__.py, что папка schemas/ считалась пакетом Python.

Затем создаем и наполняем src/schemas/movie.py:
'''
# подключаем класс date для работы с текущей датой
from datetime import date
# подключаем field_validator для проверки значения года
from pydantic import BaseModel, Field, ConfigDict, field_validator

# базовая модель фильма
class MovieBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    genre: str = Field(min_length=2, max_length=100)
    rating: float = Field(ge=0, le=10)
    year: int

    # валидация моля year
    @field_validator('year')
    @classmethod
    def year_in_range(cls, year: int) -> int:
        # проверяем что год между 1888 и текущим годом
        if not (1888 <= year <= date.today().year):
            raise ValueError(f'Год должен быть между 1888 и {date.today().year}')
        return year

# модель для создания фильма через POST-запрос
class MovieCreate(MovieBase):
    pass

# модель для обновления данных о фильме через PUT/PATCH-запросы
class MovieUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    genre: str | None = Field(default=None, min_length=2, max_length=100)
    rating: float | None = Field(default=None, ge=0, le=10)
    year: int | None = None

# модель для ответа клиенту
class MovieOut(MovieBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# -------------------------------------------------------------------------------------------------------------

# Репозиторий
'''
Пропишем логику взаимодействия с БД в файле src/repositories/movies.py:
'''
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Movie
from src.schemas.movie import MovieCreate, MovieUpdate

# создание фильма 
async def create_movie(session: AsyncSession, data: MovieCreate) -> Movie:
    new_movie = Movie(**data.model_dump())
    session.add(new_movie)
    await session.commit()
    return new_movie

# получение одного фильма по ID
async def get_movie(session: AsyncSession, movie_id: int) -> Movie | None:
    return await session.get(Movie, movie_id)

# получение списка фильмов
async def get_list_movies(
    session: AsyncSession,
    # сколько фильмов вернуть за один запрос
    limit: int = 50,
    # с какой позиции начинать выборку
    offset: int = 0,
) -> list[Movie]:
    # ограничение на кол-во фильмов в списке (1...100)
    limit = max(1, min(limit, 100))
    # ограничение на смещение, чтобы не было отрицательным
    offset = max(0, offset)
    # select(Movie) - запрос на выборку всех фильмов
    # order_by(Movie.id.asc()) - сортировка по ID (по возрастанию)
    # offset(offset).limit(limit) - пагинация (смещение + ограничение)
    query = select(Movie).order_by(Movie.id.asc()).offset(offset).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())

# полное обновление фильма
async def put_movie(session: AsyncSession, movie_id: int, movie_data: MovieCreate) -> Movie | None:
    movie = await session.get(Movie, movie_id)
    # если фильма нет в базе
    if not movie:
        return None
    # обновляем поля и значения указанного фильма
    for field, value in movie_data.model_dump().items():
        setattr(movie, field, value)
    await session.commit()
    return movie

# частичное обновление фильма
async def patch_movie(session: AsyncSession, movie_id: int, movie_data: MovieUpdate) -> Movie | None:
    movie = await session.get(Movie, movie_id)
    if not movie:
        return None
    for field, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)
    await session.commit()
    return movie

# удаления фильма по ID
async def delete_movie(session: AsyncSession, movie_id: int) -> bool:
    movie_to_delete = await session.get(Movie, movie_id)
    if not movie_to_delete:
        return False
    await session.delete(movie_to_delete)
    await session.commit()
    return True

# -------------------------------------------------------------------------------------------------------------

# Роутер
'''
Пропишем код репозитория в src/routers/movies.py:
'''
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.movie import MovieCreate, MovieUpdate, MovieOut
from src.repositories import movies as repo

router = APIRouter(
    prefix='/movies',
    tags=['Movies']
)

# получаем список фильмов
@router.get('/', response_model=list[MovieOut])
async def get_movies_list(
    session: AsyncSession = Depends(get_session),
    limit: int = 50, 
    offset: int = 0
):
    return await repo.get_list_movies(session, limit, offset)

# получаем фильм по ID
@router.get('/{movie_id}', response_model=MovieOut)
async def get_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    movie = await repo.get_movie(session, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail='Фильм не найден')
    return movie

# создаем запись с новым фильмов в БД
@router.post('/', response_model=MovieOut)
async def create_movie(movie_data: MovieCreate, session: AsyncSession = Depends(get_session)):
    return await repo.create_movie(session, movie_data)

# полностью обновляем данные о фильме
@router.put('/{movie_id}', response_model=MovieCreate)
async def put_movie(movie_id: int, movie_data: MovieCreate, session: AsyncSession = Depends(get_session)):
    movie = await repo.put_movie(session, movie_id, movie_data)
    if not movie:
        raise HTTPException(status_code=404, detail='Фильм не найден')
    return movie

# частично обновляем данные о фильме
@router.patch('/{movie_id}', response_model=MovieUpdate)
async def patch_movie(movie_id: int, movie_data: MovieUpdate, session: AsyncSession = Depends(get_session)):
    movie = await repo.put_movie(session, movie_id, movie_data)
    if not movie:
        raise HTTPException(status_code=404, detail='Фильм не найден')
    return movie

# удаляем фильм из БД
@router.delete('/{movie_id}')
async def delete_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    is_deleted = await repo.delete_movie(session, movie_id)
    if not is_deleted:
        raise HTTPException(status_code=404, detail='Фильм не найден')

# -------------------------------------------------------------------------------------------------------------

# Точка входа в приложение
'''
Модифицируем код в main.py, добавив подключение роутера:
'''
from fastapi import FastAPI
from src.routers.movies import router as movie_router 

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Movies API готов к работе!'}

app.include_router(movie_router)

# -------------------------------------------------------------------------------------------------------------

# Фильтрация и сортировка в GET /movies
'''
Модифицируем функцию get_list_movies() из файла src/repositories/movies.py, реализовав продвинутую
выборку фильмов с фильтрацией, поиском и сортировкой:
'''
# создаем словарь с разрешенными сортировками, для удобства и безопасности
# ключи - строки, которые может передать пользователь (понятные названия, чтобы клиент не думал про SQL)
# значения - SQLAlchemy-выражения для сортировки (по возрастанию и убыванию)
# если указан минус (-) в начале - сортировка по убыванию 
ALLOWED_ORDERS = {
    'title': Movie.title.asc(),
    '-title': Movie.title.desc(),
    'year': Movie.year.asc(),
    '-year': Movie.year.desc(),
    'rating': Movie.rating.asc(),
    '-rating': Movie.rating.desc(),
    'id': Movie.id.asc(),
    '-id': Movie.id.desc()
}

# добавляем параметры фильтрации и сортировки в функцию
async def get_list_movies(
    session: AsyncSession,
    year_min: int | None = None,        # минимальный год фильма
    year_max: int | None = None,        # максимальный год фильма
    min_rating: float | None = None,    # минимальный рейтинг
    order_by: str | None = '-rating',   # параметр сортировки (по умолчанию сортируем по рейтингу)
    limit: int = 50, 
    offset: int = 0,
) -> list[Movie]:
    
    # пока формируем базовый SQL-запрос "выбрать все фильмы"
    query = select(Movie)
    # фильтрация по годам
    if year_min is not None:
        query = query.where(Movie.year >= year_min)
    if year_max is not None:
        query = query.where(Movie.year <= year_max)
    # фильтрация по минимальному рейтингу
    if min_rating is not None:
        query = query.where(Movie.rating >= min_rating)
    
    # ключ сортировки (order_by, если указан, по умолчанию'-rating')
    key = order_by or '-rating'
    # проверка, что передан корректный параметр сортировки (если передано некорректное значение - сортируем по убыванию рейтинга)
    primary_order = ALLOWED_ORDERS.get(key, Movie.rating.desc())
    # вторичная сортировка по ID (если у двух фильмов одинаковый рейтинг или год)
    query = query.order_by(primary_order, Movie.id.asc())

    # применяем пагинацию
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    query = query.offset(offset).limit(limit)

    # выполняем запрос и получаем список фильмов
    result = await session.execute(query)
    return list(result.scalars().all())

'''
Обновляем эндпоинт get_movies_list():
'''

# добавляем в эндпоинт новые параметры сортировки и фильтрации
@router.get('/', response_model=list[MovieOut])
async def get_movies_list(
    year_min: int | None = None,
    year_max: int | None = None,
    min_rating: float | None = None,
    order_by: str | None = '-rating',
    session: AsyncSession = Depends(get_session),
    limit: int = 50, 
    offset: int = 0
):
    return await repo.get_list_movies(session, year_min, year_max, min_rating, order_by, limit, offset)