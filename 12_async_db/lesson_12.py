# Асинхронность и работа с базой данных

# Асинхронность в Python и FastAPI

# Задание № 1 - создать две асинхронные функции и рассмотреть специфику их выполнения

# asyncio - модуль для работы с асинхронностью
import asyncio

# асинхронная функция "Приготовить суп"
async def cook_soup():
    print('Начинаем готовить суп!')
    # имитация готовки супа
    await asyncio.sleep(3)
    print('Суп готов!')

# асинхронная функция "Убраться на кухне"
async def clean_kitchen():
    print('Начинаем убираться на кухне!')
    # имитация уборки
    await asyncio.sleep(2)
    print('Уборка завершена!')

async def main():
    # gather() - позволяет запускать одновременно несколько асинхронных задач и ожидать их завершения
    await asyncio.gather(cook_soup(), clean_kitchen())

# запускаем выполнение корутины и получаем результат
asyncio.run(main())

# Задание № 2 - создать синхронный и асинхронный эндпоинты, рассмотреть специфику их выполнения

from fastapi import FastAPI
import time
import asyncio

app = FastAPI()

# эндпоинт с блокирующими операциями
@app.get('/sync')
def sync_endpoint():
    # фиксируем начало работы эндпоинта
    start = time.perf_counter()
    # запускаем блокирующие операции
    for _ in range(20):
        time.sleep(1)
    # фиксируем конец выполнения блокирующих операций
    result = time.perf_counter() - start
    # возвращаем результат
    return {'mode': 'sync', 'time': result}

# эндпоинт с неблокирующими операциями
@app.get('/async')
async def async_endpoint():
    start = time.perf_counter()
    # генерируем и запускаем неблокирующие операции
    await asyncio.gather(*[asyncio.sleep(1) for _ in range(20)])
    result = time.perf_counter() - start
    return {'mode': 'async', 'time': result}

'''
Запустим наш код через стандартный запуск:
uvicorn main:app --reload 

Сначала откроем в браузере синхронную версию:
http://127.0.0.1:8000/sync -> увидим примерно {"mode":"sync","time":20.005245400010608}
Операции выполнялись друг за другом, 20 операций по 1 секунде ≈ 20 секунд

Затем откроем асинхронную версию:
http://127.0.0.1:8000/async -> увидим примерно {"mode":"async","time":1.0132027000654489}
'''

# -------------------------------------------------------------------------------------------------------------

# Асинхронный SQLAlchemy

# Задание № 3 - переписать database.py под асинхронный движок для работы с БД 

# Синхронный вариант database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///products.db', echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()       
    try:
        yield db              
    finally:
        db.close() 

# Асинхронный вариант database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

engine = create_async_engine('sqlite+aiosqlite:///products.db', echo=True)

Base = declarative_base()

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# -------------------------------------------------------------------------------------------------------------

# Асинхронные CRUD-операции

# Задание № 4 - переписать routers/products.py для асинхронной работы с БД

from fastapi import APIRouter, HTTPException, Query, Depends
# подключаем класс AsyncSession для работы с асинхронной сессией
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Product
from schemas import ProductCreate, ProductOut, ProductUpdate
from repositories import products_repository

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

# вспомогательная функция для проверки наличия товара
async def get_product_or_404(session: AsyncSession, product_id: int) -> Product:
    product = await products_repository.get_product(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

# создание нового товара
@router.post('', response_model=ProductOut)
async def create_product(product_data: ProductCreate, session: AsyncSession = Depends(get_session)):
    return await products_repository.create_product(session, product_data)

# получение списка товаров с фильтрацией
@router.get('', response_model=list[ProductOut])
async def get_products_list(
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена'),
    session: AsyncSession = Depends(get_session)
):
    return await products_repository.get_products_list(session, q, in_stock, min_price, max_price)

# получение одного товара по ID
@router.get('/{product_id}', response_model=ProductOut)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    return await get_product_or_404(session, product_id)

# полное обновление товара
@router.put('/{product_id}', response_model=ProductOut)
async def put_product(product_id: int, product_data: ProductCreate, session: AsyncSession = Depends(get_session)):
    # при вызове get_product_or_404() тоже ставим await, иначе в product попадет корутина, а не объект Product
    product = await get_product_or_404(session, product_id)
    return await products_repository.put_product(session, product, product_data)

# частичное обновление товара
@router.patch('/{product_id}', response_model=ProductOut)
async def patch_product(product_id: int, product_data: ProductUpdate, session: AsyncSession = Depends(get_session)):
    product = await get_product_or_404(session, product_id)
    return await products_repository.patch_product(session, product, product_data)

# удаление товара
@router.delete('/{product_id}')
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    product = await get_product_or_404(session, product_id)
    await products_repository.delete_product(session, product)
    return {'message': 'Товар удален'}

# Задание № 5 - переписать repositories/products_repository.py для асинхронной работы с БД

# подключаем класс AsyncSession для работы с асинхронной сессией
from sqlalchemy.ext.asyncio import AsyncSession
# select() - функция для конструирования SQL-запроса на чтение данных, работает в асинхронных сессиях, замена query()
from sqlalchemy import select
from models import Product
from schemas import ProductCreate, ProductUpdate

# создать новый товар
async def create_product(session: AsyncSession, product_data: ProductCreate) -> Product:
    new_product = Product(**product_data.model_dump())
    session.add(new_product)
    await session.commit()
    return new_product

# получение списка товаров с фильтрацией
async def get_products_list(
    session: AsyncSession,
    q: str = None,
    in_stock: bool = None,
    min_price: float = None,
    max_price: float = None
) -> list[Product]:

    # меняем query() на select(), result на query для дальнейшего удобства и логики
    query = select(Product)

    # проверка фильтров наличия, макс. и мин. цены
    if in_stock is not None:
        # здесь и далее - меняем filter() на where()
        query = query.where(Product.in_stock == in_stock)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    
    # отправляем запрос в БД и получаем объект класса Result
    result = await session.execute(query)
    # превращаем объект Result в список объектов Product
    products = result.scalars().all()
    
    if q:
        low_q = q.lower()
        products = [p for p in products if low_q in p.name.lower()]
    
    return products

# получение товара по ID
async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

# полное обновление товара
async def put_product(session: AsyncSession, product: Product, product_data: ProductCreate) -> Product:
    for field, value in product_data.model_dump().items():
        setattr(product, field, value)
    await session.commit()
    return product

# частичное обновление товара
async def patch_product(session: AsyncSession, product: Product, product_data: ProductUpdate) -> Product:
    updates = product_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)
    await session.commit()
    return product

# удаление товара
async def delete_product(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.commit()

'''
Если мы сейчас попробуем запустить приложение через uvicorn main:app --reload,
то увидим ошибку AttributeError: 'AsyncEngine' object has no attribute '_run_ddl_visitor'.
Все дело в строчке Base.metadata.create_all(bind=engine) в main.py - здесь выполняется синхроный вызов 
на асинхронном движке. Мы можем переписать эту строчку, но есть решение проще - просто удалить данную конструкцию.
Дело в том, что мы с предыдущего занятия используем Alembic, с помощью которого сохраняется вся структура БД.
При этом, несмотря на асинхронный движок, в Alembic мы все также используем синхронную версию sqlite:///./products.db,
так и должно быть. После удаления строчки Base.metadata.create_all(bind=engine) мы можем запустить и протестировать наше приложение.

СОВЕТ ПРЕПОДАВАТЕЛЮ: если у вас также появилось предупреждение насчет orm_mode = True в sсhemas.py, то можно показать
студентам, что в современной версии Pydantic конструкцию:
class Config:    
    orm_mode = True 

стоит заменить на:
from pydantic import ConfigDict

class ProductOut(ProductCreate):
...
    model_config = ConfigDict(from_attributes=True)

Если предупреждение не появилось, то все равно рекомендуется переписать этот код для соответствия стилю Pydantic v2.
'''