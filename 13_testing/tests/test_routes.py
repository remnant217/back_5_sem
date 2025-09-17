import asyncio
import pytest

from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import delete

from src.main import app
from src.database import Base, get_session
from src.models import Product
from src.schemas import ProductOut

# создаем тестовый движок и фабрику сессий
engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)

# корутина для создания таблиц внутри тестовой БД
async def init_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init_schema())

# корутина для подмены зависимости на тестовую сессию
async def override_get_session():
    async with SessionMaker() as session:
        yield session
app.dependency_overrides[get_session] = override_get_session

# клиент, который будет отправлять запросы прямо в приложение
client = TestClient(app)

# вспомогательная функция для очищения таблицы и добавления тестовых данных
def reset_and_seed():
    async def op():
        async with SessionMaker() as session:
            await session.execute(delete(Product))
            session.add_all([
                Product(name='Телефон', description='Хорошая камера', price=49000, in_stock=True),
                Product(name='Компьютер', description='Игровой', price=90000, in_stock=True),
                Product(name='Наушники', description='Беспроводные', price=12000, in_stock=False),
            ])
            await session.commit()
    asyncio.run(op())

# функция для проверки работы приложения
def test_app_starts():
    response = client.get('/')
    assert response.status_code == 200

# функция для проверки ответа по запросу GET /products
def test_products_shape():
    reset_and_seed()
    response = client.get('/products')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    expected_keys = ProductOut.model_fields.keys()
    assert data and expected_keys <= set(data[0].keys())

# задаем несколько тестовых входных данных
@pytest.mark.parametrize(
    'params, expected_names',
    [
        ({}, {'Телефон', 'Компьютер', 'Наушники'}),
        ({'q': 'Ком'}, {'Компьютер'}),
        ({'in_stock': 'true'}, {'Телефон', 'Компьютер'}),
        ({'min_price': 40000, 'max_price': 50000}, {'Телефон'}),
    ],
)
def test_products_filters(params, expected_names):
    # очищаем таблицу и добавляем тестовые данные в БД
    reset_and_seed()
    # отравляем запрос GET /products с указанными параметрами фильтрации
    response = client.get('/products', params=params)
    # проверяем статус ответа
    assert response.status_code == 200
    # сравниваем полученные товары с ожидаемыми
    assert {p['name'] for p in response.json()} == expected_names