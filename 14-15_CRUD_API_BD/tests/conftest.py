import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_session
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
@pytest.fixture(scope='session')
def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    yield engine
    asyncio.run(engine.dispose())

# создаем фабрику сессий
@pytest.fixture(scope='session')
def test_sessionmaker(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False)

# подготовка базы перед каждым тестом
@pytest.fixture
def prepare_db(test_engine, test_sessionmaker):
    async def _setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with test_sessionmaker() as session:
            session.add_all([Movie(title=t, genre=g, year=y, rating=r) for (t, g, y, r) in MOVIES_TEST])
            await session.commit()

    asyncio.run(_setup())
    yield

# создаем тестовый клиент
@pytest.fixture
def client(prepare_db, test_sessionmaker):
    async def override_get_session():
        async with test_sessionmaker() as session:
            yield session
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.pop(get_session, None)
