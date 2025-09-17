# Тестирование FastAPI-приложений

# Подготовка проекта к тестированию

# Задание № 1 - обновить структуру проекта product_catalog
'''
Для удобства обновим структуру нашего проекта:
product_catalog/
├── src/        # исходный код приложения
├── tests/      # будущие тесты
├── venv/       # виртульное окружение

СОВЕТ ПРЕПОДАВАТЕЛЮ: убедитесь, что все студенты сформировали у себя указанную структуру папок.
Обязательно покажите у себя, что в папке src/ лежат все созданные на предыдущих занятиях папки и файлы.
Можете также еще раз показать процесс формирования и активации виртуального окружения. На текущий момент
в проекте присутствуют следующие зависимости:
- fastapi
- uvicorn
- sqlalchemy
- alembic
- aiosqlite
- pytest

Обратите внимание на pytest, он тоже должен быть установлен.
'''

# Задание № 2 - создать тренировочный тест для проверки работы PyTest

def test_example():
    assert 2 * 2 == 4

'''
Запустим проверку, указав в терминале:
pytest

Можно запустить и более точечно, указав конкретный файл:
python -m pytest tests/test_example.py -v
'''

# Задание № 3 - создать файл tests/test_routes.py

# TestClient - класс для тестирования FastAPI-приложения без запуска сервера
from fastapi.testclient import TestClient
# импортируем объект приложения из main.py
from src.main import app

# клиент, который будет отправлять запросы прямо в приложение
client = TestClient(app)

# функция для проверки работы приложения
def test_app_starts():
    # отправляем GET-запрос к корневому маршруту
    response = client.get('/')
    # проверяем получение статус-кода 200
    assert response.status_code == 200

# Задание № 4 - установить модуль httpx
'''
Перед запуском теста нам понадобится установить модуль httpx, который предоставляет
полноценный HTTP-клиент для обработки запросов:

pip install httpx
'''

# Задание № 5 - создать файл pytest.ini
'''
Мы почти готовы к запуску теста. Однако, если мы выполним просто команду "pytest", то появится ошибка импорта
ModuleNotFoundError: No module named 'database'. Чтобы это исправить, создадим конфигурационный файл 
для наших тестов pytest.ini:

[pytest]
addopts = -v        # всегда подробный вывод
testpaths = tests   # pytest ищет тесты только в папке tests
pythonpath = src    # чтобы можно было писать from src.main import app без ошибок импорта
'''

# Задание № 6 - запустить тест через python -m pytest
'''
Если мы снова попробуем запустить тест через команда pytest, то увидим другую ошибку - ModuleNotFoundError: No module named 'src'
Есть разные решения этой проблемы и для нас сейчас вполне подойдет запуск тестов следующим образом:

python -m pytest

Тогда мы увидим сообщение:
tests/test_routes.py::test_app_starts PASSED

Если же попробуем поменять тест, например строчку с assert:
assert response.status_code == 201

Тогда при запуске теста увидим ошибку:
tests/test_routes.py::test_app_starts FAILED

Вернем строчку с assert в исходное состояние:
assert response.status_code == 200
'''

# -------------------------------------------------------------------------------------------------------------

# Тестирование API

# Задание № 7 - отредактировать импорты в файлах папки scr/
'''
СОВЕТ ПРЕПОДАВАТЕЛЮ: редактируйте импорты вместе с учениками и проверяйте, что все успевают.
Проговаривайте, где указываем абсолютный путь, а где - относительный.

1. src/repositories/products_repository.py

from models import Product
from schemas import ProductCreate, ProductUpdate
↓
from src.models import Product
from src.schemas import ProductCreate, ProductUpdate

2. src/routers/products.py

from database import get_session
from models import Product
from schemas import ProductCreate, ProductOut, ProductUpdate
from repositories import products_repository
↓
from src.database import get_session
from src.models import Product
from src.schemas import ProductCreate, ProductOut, ProductUpdate
from src.repositories import products_repository

3. src/main.py

from routers import products
↓
from .routers import products

4. src/models.py

from database import Base
↓
from .database import Base
'''

# Задание № 8 - создать тестовую БД в tests/test_routes.py

# импортируем asyncio для создания тестовой БД до запуска тестов
import asyncio
# инструменты для создания асинхронного движка и фабрики сессий
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# StaticPool - класс, предоставляющий пул из одного соединения, используемого для всех запросов
# Без него при каждом новом подключении будет создавать новая пустая БД
from sqlalchemy.pool import StaticPool
...
# подключаем Base с метаданными из всех моделей и зависимость get_session()
from src.database import Base, get_session

'''
Далее создадим движок и фабрику сессий, чтобы БД хранилась в памяти программы:
'''
# sqlite+aiosqlite:///:memory: - создаем в памяти текстовую БД SQLite
# poolclass - содержит класс пула соединений, указываем StaticPool
engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)

'''
Затем создадим асинхронную функцию для создания таблиц внутри временной БД.
И укажем ее запуск с помощью asyncio:
'''
# корутина для создания таблиц внутри тестовой БД
async def init_schema():
    # открываем транзакцию на тестовом движке
    async with engine.begin() as conn:
        # запускаем синхронное создание таблиц в асинхронном контексте
        await conn.run_sync(Base.metadata.create_all)
# выполняем созданную корутину и дожидаемся создания всех таблиц в БД
asyncio.run(init_schema())

# корутина для подмены зависимости на тестовую сессию
async def override_get_session():
    async with SessionMaker() as session:
        yield session
# меняем оригинальную зависимости на новую на время тестирования
app.dependency_overrides[get_session] = override_get_session

# Задание № 9 - создать функцию для очищения таблицы и добавления тестовых данных

# подключаем функцию для удаления данных из таблицы БД
from sqlalchemy import delete
# подключаем модель Product для наполнения БД
from src.models import Product
...
# вспомогательная функция для очищения таблицы и добавления тестовых данных
def reset_and_seed():
    # вложенная корутина со всеми действиями с БД
    async def op():
        # открываем асинхронную сессию, привязанную к тестовую движку
        async with SessionMaker() as session:
            # генерируем SQL-запрос для удаления всех строк из таблицы products 
            await session.execute(delete(Product))
            # добавляем тестовые данные в сессию  
            session.add_all([
                Product(name='Телефон', description='Хорошая камера', price=49000, in_stock=True),
                Product(name='Компьютер', description='Игровой', price=90000, in_stock=True),
                Product(name='Наушники', description='Беспроводные', price=12000, in_stock=False),
            ])
            # сохраняем изменения и отправляем данные в БД
            await session.commit()
    # запускаем корутину op() из синхронного теста
    asyncio.run(op())

# Задание № 10 - создать функцию для тестирования запроса GET /products

# подключаем схему ProductOut для проверки формы полученного ответа
from src.schemas import ProductOut
...

# функция для проверки ответа по запросу GET /products
def test_products_shape():
    # очищаем таблицу и добавляем тестовые данные
    reset_and_seed()
    # обращаемся к маршруту /products
    response = client.get('/products')
    # проверка, что эндпоинт отработал успешно
    assert response.status_code == 200
    # преобразуем полученный ответ в Python-объект
    data = response.json()
    # проверяем, что получаем список
    assert isinstance(data, list)
    # получаем названия полей из Pydantic-модели
    expected_keys = ProductOut.model_fields.keys()
    # проверяем, что получили непустой список и что у каждого элемента
    # есть нужные поля (id, name, description, price, in_stock)
    assert data and expected_keys <= set(data[0].keys())