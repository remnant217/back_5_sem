# Воркшоп. Разработка CRUD API с БД и валидацией
'''
Идея проекта - каталог фильмов с CRUD-операциями и хранением данных в БД.
'''

# Подготовка проекта
'''
Задание № 1 - создать новую папку проекта (movies_api)

Задание № 2 - создать и активировать виртуальное окружение:
python -m venv venv
venv\scripts\activate

Задание № 3 - установить необходимые библиотеки:
pip install fastapi uvicorn sqlalchemy alembic aiosqlite pytest httpx

Задание № 4 - сохранить зависимости в файл:
pip freeze > requirements.txt

Задание № 5 - создать базовую структуру каталогов:
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

СОВЕТ ПРЕПОДАВАТЕЛЮ: файл README.md пока оставьте пустым, он пригодится после второго занятия,
для выполнения домашнего задания.

Задание № 6 - написать минимальный код для проверки запуска приложения:
'''
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Movies API готов к работе!'}

'''
Задание № 7 - запустить сервер:
uvicorn src.main:app --reload

http://127.0.0.1:8000 → {"message":"Movies API готов к работе!"}
'''

# -------------------------------------------------------------------------------------------------------------

# Модель БД

'''
Задание № 8 - создать файл src/models/__init__.py
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
Задание № 9 - создать модель Movie в файле src/models/movie.py
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

    # __table_args__ - специальный атрибут для доп. настроек и ограничений на уровне всей таблицы
    __table_args__ = (
        # ограничения на рейтинг (0...10) и год выпуска фильма (>= 1888)
        # name помогает при отладке, чтении ошибок БД и работе с Alembic
        CheckConstraint('rating >= 0 AND rating <= 10', name='check_movie_rating_range'),
        CheckConstraint('year >= 1888', name='check_movie_year_ge_1888')
    )

# -------------------------------------------------------------------------------------------------------------

# БД и сессии
'''
Задание № 10 - создать файл src/database.py 
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
Задание № 11 - инициализировать alembic:
alembic init alembic

Задание № 12 - в alembic.ini задать URL для БД:
sqlalchemy.url = sqlite:///./movies.db

Задание № 13 - в alembic/env.py добавить путь к src и метаданны:
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
Задание № 14 - сгенерировать и применить миграцию:
alembic revision --autogenerate -m "init movies"
alembic upgrade head
'''

# -------------------------------------------------------------------------------------------------------------

# Pydantic-схемы
'''
Задание № 15 - создать файл src/schemas/__init__.py
Сначала создаем пустой src/schemas/__init__.py, что папка schemas/ считалась пакетом Python.

Задание № 16 - создать файл src/schemas/movie.py
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
Задание № 16 - создать файл src/repositories/movies.py
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
Задание № 17 - создать файл src/routers/movies.py
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
Задание № 18 - создать файл src/main.py
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
Задание № 19 - модифицировать файл src/repositories/movies.py
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
Задание № 20 - модифицировать эндпоинт get_movies_list() в файле src/routers/movies.py
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

# -------------------------------------------------------------------------------------------------------------

# Создание файла tests/conftest.py

'''
Задание № 21 - создать файл tests/conftest.py
В папке tests создадим файл test/conftest.py для настройки будущих тестов. 
Pytest устроен так, что автоматически ищет файл conftest.py в папке с тестами и во всех родительских папках.
Все, что определено в conftest.py, автоматически становится доступно во всех тестах.
Импортировать conftest.py вручную не нужно - pytest сделает все сам.
Необходимая логика будет в функциях, снаружи обернутых фикстурами @pytest.fixture.
Фикстуры позволят нам автоматически готовить окружение перед тестами, делая будущие тесты
короче, удобнее и надежнее.

СОВЕТ ПРЕПОДАВАТЕЛЮ: студенты уже работали с фикстурами на курсе по тестированию.
Учитывайте это при написании кода.
'''
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

# экземпляр тестируемого приложения
from src.main import app
# асинхронный движок SQLAlchemy
from src.database import get_session
# метаданные всех моделей для создания и удаления таблиц
from src.models import Base, Movie

# список с тестовыми фильмами
MOVIES_TEST = [
    ('Интерстеллар', 'Научная фантастика', 2014, 8.3),
    ('Гладиатор', 'Исторический', 2000, 8.6),
    ('Форрест Гамп', 'Драма', 1994, 8.1),
    ('Унесенные призраками', 'Аниме', 2001, 8.0),
    ('Шрэк', 'Мультфильм', 2001, 7.7),
    ('Престиж', 'Триллер', 2006, 7.6),
    ('Тайна Коко', 'Мультфильм', 2017, 7.8),
]

# создаем тестовый SQLite-движок, общий для всех тестов
# scope='session' - движок создается один раз всю сессию тестов
@pytest.fixture(scope='session')
def test_engine():
    # SQLite-движок, где база живет в памяти программы, не на диске
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    yield engine
    # engine.dispose() - закрываем движок в конце тестов
    asyncio.run(engine.dispose())

# создаем фабрику сессий
@pytest.fixture(scope='session')
# при вызове test_sessionmaker() pytest сначала вызовет test_engine(), если движок еще не создан
def test_sessionmaker(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False)

# подготовка базы перед каждым тестом
# без scope='session', чтобы фикстура выполнялась перед каждым тестом (в данном случае - чтобы тест работал с чистой БД)
@pytest.fixture
# перед вызовом prepare_db() сначала вызовутся test_engine() и test_sessionmaker()
def prepare_db(test_engine, test_sessionmaker):
    # служебная внутренняя функция для очистки и заполнения тестовой БД
    async def _setup():
        # открываем соединение с базой
        async with test_engine.begin() as conn:
            # удаляем все таблицы
            await conn.run_sync(Base.metadata.drop_all)
            # создаем таблицы заново
            await conn.run_sync(Base.metadata.create_all)

        # создаем сессию
        async with test_sessionmaker() as session:
            # добавляем тестовые фильмы в БД
            session.add_all([Movie(title=t, genre=g, year=y, rating=r) for (t, g, y, r) in MOVIES_TEST])
            await session.commit()
    # вызываем корутину _setup() внутри синхронной функции (т.к. pytest-фикситуры по умолчанию синхронные)
    asyncio.run(_setup())
    # в момент выполнения yield pytest запускает тест, где используется фикстура
    yield

# создаем тестовый клиент
@pytest.fixture
# перед вызовом client() сначала вызовутся prepare_db() и test_sessionmaker()
def client(prepare_db, test_sessionmaker):
    # замена зависимости, чтобы API использовал тестовую, а не реальную БД
    async def override_get_session():
        async with test_sessionmaker() as session:
            yield session
    # если запросят зависимость get_session - будем отдавать override_get_session
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        # отдаем тестовый клиент в тест
        yield c
    # после завершения теста убираем подмену, чтобы get_session снова указывал на нужную функцию
    app.dependency_overrides.pop(get_session, None)

'''
Задание № 22 - обсудить логику вызова созданных фикстур
При вызове client() в тестах порядок вызова фикстур будет примерно такой:
1. Pytest идет client() - нужны prepare_db() и test_sessionmaker()
2. Pytest идет в prepare_db() - нужны test_engine() и test_sessionmaker()
3. Pytest идет в test_engine() - создает и возвращает движок
4. Pytest идет в test_sessionmaker() - берет готовый test_engine, создает и возвращает фабрику сессий
5. Pytest идет обратно в prepare_db() - выполняет _setup()
6. Pytest идет обратно client() - меняет зависимости, создается TestClient(app) и возвращается объект клиента в тест
7. Выполняется тест через client
8. Завершение теста - в client() очищается dependency_overrides
'''

# -------------------------------------------------------------------------------------------------------------

# Создание файла test/test_movies.py
'''
Задание № 21 - создать файл test/test_movies.py
Остался финальный шаг - создать файл с тестами. Будем проверять работу фильтрации, сортировки,
пагинации и CRUD-операций.

СОВЕТ ПРЕПОДАВАТЕЛЮ: при добавлении каждоый новой функции запускайте процесс тестирования через python -m pytest,
обсуждайте со студентами полученные результаты. Если остается время, то покажите студентам примеры, когда тесты
могут сломаться.
'''

import pytest

# тестирование фильтрации
@pytest.mark.parametrize(
    'params, expected_titles',
    [
        ({}, {'Интерстеллар', 'Гладиатор', 'Форрест Гамп', 'Унесенные призраками', 'Шрэк', 'Престиж', 'Тайна Коко'}),
        ({'year_min': 2010}, {'Интерстеллар', 'Тайна Коко'}),
        ({'year_max': 2001}, {'Гладиатор', 'Форрест Гамп', 'Унесенные призраками', 'Шрэк'}),
        ({'min_rating': 8.2}, {'Интерстеллар', 'Гладиатор'}),
        ({'year_min': 2000, 'year_max': 2006, 'min_rating': 7.8}, {'Гладиатор', 'Унесенные призраками'})
    ]
)
def test_movies_filters(client, params, expected_titles):
    response = client.get('/movies', params=params)
    assert response.status_code == 200
    assert {movie['title'] for movie in response.json()} == expected_titles


# тестирование сортировки и пагинации
def test_order_and_pagination(client):
    # пример некорректного order_by (API должен понять, что такой сортировки нет и применить вариант по умолчанию -rating)
    response = client.get('/movies', params={'order_by': '123', 'limit': 7})
    assert response.status_code == 200
    titles = [movie['title'] for movie in response.json()]
    # проверяем, что список названий фильмов отсортирован по рейтингу (от большего к меньшему)
    assert titles == [
        'Гладиатор',
        'Интерстеллар',
        'Форрест Гамп',
        'Унесенные призраками',
        'Тайна Коко',
        'Шрэк',
        'Престиж'
    ]

    # сортировка по title (лексикографическая) и проверка пагинации
    # сортируем по алфавиту и берем первые 2 фильма
    response_1 = client.get('/movies', params={'order_by': 'title', 'limit': 2, 'offset': 0})
    # сортируем по алфавиту, пропускаем первые 2 фильма, берем следующие 2
    response_2 = client.get('/movies', params={'order_by': 'title', 'limit': 2, 'offset': 2})
    assert [movie['title'] for movie in response_1.json()] == ['Гладиатор', 'Интерстеллар']
    assert [movie['title'] for movie in response_2.json()] == ['Престиж', 'Тайна Коко']

# тестирование CRUD-операций
def test_crud(client):
    # тестируем create
    data = {'title': 'Дюна', 'genre': 'Научная фантастика', 'rating': 7.7, 'year': 2021}
    response = client.post('/movies', json=data)
    assert response.status_code in (200, 201)
    created_movie = response.json()
    movie_id = created_movie['id']

    # тестируем patch
    response = client.patch(f'/movies/{movie_id}', json={'rating': 7.0})
    assert response.status_code == 200
    assert response.json()['rating'] == 7.0

    # тестируем read
    response = client.get(f'/movies/{movie_id}')
    assert response.status_code == 200
    assert response.json()['year'] == 2021

    # тестируем delete
    response = client.delete(f'/movies/{movie_id}')
    assert response.status_code in (200, 204)

    # тестируем read удаленного фильма
    response = client.get(f'/movies/{movie_id}')
    assert response.status_code == 404