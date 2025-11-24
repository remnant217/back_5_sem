import pytest_asyncio

# подключаем наши ORM-модели, которые содержатся в Base
from app.models import Base

# подключаем движок и фабрику асинхронных сессий для тестов
from tests.test_database import test_engine, TestSessionLocal

# scope='session' - движок создается один раз на всю сессию тестов
# autouse=True - фикстура активируется для всех тестов, которые могут ее видеть,
# значит не нужно указывать ее явно, фикситура запустится сама
@pytest_asyncio.fixture(scope='session', autouse=True)
# создаем структуру БД для тестов и удаляем ее после завершения всех тестов
async def prepare_database():
    # создаем все таблицы в тестовой БД
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # передаем управление тестам
    yield
    # после завершения тестов БД исчезнет сама, т.к. хранится в оперативной памяти

# асинхронная фикстура, возвращающая новую асинхронную сессию для каждого теста
@pytest_asyncio.fixture()
async def session():
    async with TestSessionLocal() as session:
        yield session