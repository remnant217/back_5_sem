# Тестирование бизнес-логики и моделей

# Структура тестов
'''
В корне нашего проекта создадим папку tests/, там будут храниться наши тесты:

fastapi_workshop/  
├─ alembic/ 
├─ app/         
├─ logs/    
├─ tests/ 
├─ venv/   
...

Сразу создадим внутри папки tests/ следующие файлы, пока что пустые:

tests/
  ├─ test_database.py               # настройка тестовой БД
  ├─ conftest.py                    # общие фикстуры
  ├─ test_repository_users.py       # тесты бизнес-логики пользователей
  └─ test_repository_products.py    # тесты бизнес-логики продуктов

Не забудьте про фреймворк PyTest, его также необходимо установить в виртиальное окружение нашего проекта:
pip install pytest

Также нам понадобится pytest-asyncio - плагин для фреймворка pytest, который нужен для корректной работы асинхронных тестов:
pip install pytest-asyncio
'''

# ---------------------------------------------------------------------------------------------------

# Создание tests/test_database.py

# tests/test_database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# StaticPool гарантирует, что все сессии используют одно и то же соединение,
# чтобы одна и та же in-memory БД была доступна во всех тестах
from sqlalchemy.pool import StaticPool

# подключение к in-memory SQLite для асинхронного движка
TEST_DATABASE_ASYNC = 'sqlite+aiosqlite:///:memory:'

# отдельный движок для тестов
test_engine = create_async_engine(url=TEST_DATABASE_ASYNC, echo=False, poolclass=StaticPool)

# фабрика асинхронных сессий для тестовой БД
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

# ---------------------------------------------------------------------------------------------------

# Создание tests/conftest.py

# tests/conftest.py

# импортируем pytest_asyncio для работы с асинхронными фикстурами
import pytest_asyncio

# подключаем наши ORM-модели, которые содержатся в Base
from app.models import Base

# подключаем движок и фабрику асинхронных сессий для тестов
from tests.test_database import test_engine, TestSessionLocal

# scope='session' - движок создается один раз на всю сессию тестов
# autouse=True - фикстура активируется для всех тестов, которые могут ее видеть,
# значит не нужно указывать ее явно, фикстура запустится сама
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

# ---------------------------------------------------------------------------------------------------

# Создание tests/test_repository_users.py

# tests/test_repository_users.py

import pytest

# подключаем необходимые для тестирования функции и модели
from app.repositories.users import (
    create_user,
    update_user,
    authenticate,
)
from app.models.users import UserCreate, UserUpdate

# pytest.mark.asyncio - указываем, что данная тестовая функция - корутина, ее нужно выполнить
# через event loop и разрешить внутри await
@pytest.mark.asyncio
# тестируем, что пользователь корректно создается в БД:
# - id генерируется
# - username сохраняется без изменений
# - password сохраняется в виде хэша
# - is_active по умолчанию True
# - is_superuser по умолчанию False
# в качестве параметра указываем session - как назвали функцию в conftest.py
async def test_create_user(session):
    # подготавливаем данные
    user_data = UserCreate(username='Dima', password='Dima1234')
    # вызываем бизнес-логику
    user = await create_user(session=session, user_create=user_data)
    # проверяем результаты
    assert user.id is not None
    assert user.username == 'Dima'
    # пароль в базе не должен совпадать с открытым паролем
    assert user.hashed_password != 'Dima1234'
    assert user.is_active == True
    assert user.is_superuser == False

# тестируем успешную аутентификацию
@pytest.mark.asyncio
async def test_authenticate_user_success(session):
    # создаем пользователя
    user_data = UserCreate(username='Maks', password='Maks6789')
    await create_user(session=session, user_create=user_data)
    # проверяем аутентификацию
    user = await authenticate(session=session, username='Maks', password='Maks6789')
    assert user is not None
    assert user.username == 'Maks'

# тестируем возвращение None при неверном вводе пароле
@pytest.mark.asyncio
async def test_authenticate_wrong_password(session):
    user_data = UserCreate(username='Misha', password='Misha2007')
    await create_user(session=session, user_create=user_data)
    # проверяем аутентификацию
    user = await authenticate(session=session, username='Misha', password='Misha7002')
    assert user is None  

# тестируем обновление данных - меняем full_name, остальные поля не должны меняться
@pytest.mark.asyncio
async def test_update_user_full_name(session):
    user_data = UserCreate(username='Mike', password='Mike2016', full_name='Mike Wheeler')
    user = await create_user(session=session, user_create=user_data)
    update = UserUpdate(full_name='Michael Wheeler')
    updated_user = await update_user(session=session, user_db=user, user_update=update)
    assert updated_user.full_name == 'Michael Wheeler'
    assert updated_user.username == 'Mike'
    assert updated_user.is_active == True
    assert updated_user.is_superuser == False

# ---------------------------------------------------------------------------------------------------

# Создание tests/test_repository_products.py

import pytest

# подключаем необходимые для тестирования функции и модели
from app.repositories.products import(
    create_product,
    update_product,
    get_product_by_id
)
from app.models.products import ProductCreate, ProductUpdate

# тестируем создание продукта
@pytest.mark.asyncio
async def test_create_product(session):
    product_data = ProductCreate(name='Ноутбук', price=55000)
    product = await create_product(session=session, product_create=product_data)
    assert product.id is not None
    assert product.name == 'Ноутбук'
    assert product.price == 55000
    assert product.in_stock is True

# тестируем обновление продукта
@pytest.mark.asyncio
async def test_update_product_price(session):
    product_data = ProductCreate(name='Телефон', price=45000)
    product = await create_product(session=session, product_create=product_data)
    update = ProductUpdate(price=50000)
    updated_product = await update_product(session=session, product_db=product, product_update=update)
    assert updated_product.price == 50000
    assert updated_product.name == 'Телефон'

# тестируем получение None при попытке получить несуществующий продукт
@pytest.mark.asyncio
async def test_get_product_by_id_not_found(session):
    product = await get_product_by_id(session, product_id=1)
    assert product is None