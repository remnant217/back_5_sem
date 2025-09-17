# Работа с SQLAlchemy и SQLite

# Настройка SQLAlchemy и создание модели

# Задание № 1 - создать новый проект с виртуальным окружением, установить библиотеки fastapi, uvicorn и sqlalchemy
'''
СОВЕТ ПРЕПОДАВАТЕЛЮ: рекомендуется перед установкой SQLAlchemy создать отдельную папку с проектом,
создать и активировать виртуальное окружение, и установить fastapi и uvicorn.
Можно показать установку сразу трех библиотек одной командой:
pip install fastapi uvicorn sqlalchemy

В терминале:
pip install sqlalchemy
'''

# Задание № 2 - с помощью sqlalchemy создать движок для работы с SQLite 

# импортируем функцию для создания движка 
from sqlalchemy import create_engine

# создаем соединение с SQLite (файл products.db в текущей папке)
# echo=True - SQLAlchemy будет выводить все выполняемые SQL-запросы
engine = create_engine('sqlite:///products.db', echo=True)

# Задание № 3 - создать базовый класс Base для работы с моделями

# импортируем функцию для создания класса Base
from sqlalchemy.orm import declarative_base

# создаем базовый класс для моделей
Base = declarative_base()

# Задание № 4 - создать фабрику сессий для работы с новыми сессиями

# импортируем класс для управления сессиями
from sqlalchemy.orm import sessionmaker

# создаем фабрику сессий - специальный объект, из которого можно создавать новые сессии
# bind=engine - привязываем сессию к базе данных
SessionLocal = sessionmaker(bind=engine)

# Задание № 5 - создать модель Product для работы с товарами

# импортируем классы для создания колонок таблицы с определенными типами
from sqlalchemy import Column, Integer, String, Float, Boolean

# класс для создания таблицы "Товары"
class Product(Base):
    # указываем имя таблицы в БД
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)  # первичный ключ
    name = Column(String, nullable=False)               # название товара, обязательное поле
    price = Column(Float, nullable=False)               # цена товара, обязательное поле
    in_stock = Column(Boolean, default=True)            # в наличии, по умолчанию = True

# Задание № 6 - создать таблицу products в базе данных

# создаем все таблицы в базе данных (если их еще нет)
Base.metadata.create_all(bind=engine)

# -------------------------------------------------------------------------------------------------------------

# CRUD-операции с SQLAlchemy

# Задание № 7 - создать новую сессию с помощью объекта SessionLocal 

session = SessionLocal()

# Задание № 8 - научиться создавать новые данные и добавлять их в БД

# создаем новый товар
new_product = Product(name='Ноутбук', price=60000, in_stock=True)

# добавляем товар в сессию
session.add(new_product)

# сохраняем изменения в базе
session.commit()

# выводим сообщение о создании товара
print(f'Создан товар: {new_product.id}, {new_product.name}, {new_product.price}')

# Задание № 9 - создать еще 2 новых товара и добавить их в БД

# создаем объекты для телефона и наушников
phone = Product(name='Телефон', price=35000, in_stock=True)
headphones = Product(name='Наушники', price=10000, in_stock=False)

# добавляем объекты в сессию
session.add(phone)
session.add(headphones)

# можно сразу добавить список объектов
session.add_all([phone, headphones])

# сохраняем изменения в базе
session.commit()

# Задание № 10 - научиться извлекать данные из БД разными способами

# получить все товары
# all() - метод для преобразования всех данных, полученных с помощью query(), в список
products_all = session.query(Product).all()
for product in products_all:
    print(product.name, product.price)

# получить один товар из таблицы по ID
# get() - возвращает объект по его PRIMARY KEY, если записи нет - возвращается None
product = session.get(Product, 1)
print(product.name, product.price)

# получить товары, цена которых выше 20000
# filter() - метод для фильтрации записей по указанному критерию (работает как WHERE в SQL)
products_expensive = session.query(Product).filter(Product.price > 20000).all()
for product in products_expensive:
    print(product.name, product.price)

# Задание № 11 - научиться обновлять данные в БД

# найдем товар с ID=2
product = session.get(Product, 2)
print(f'До изменения: {product.name}, {product.price}')

# меняем цену товара и сохраняем изменения
product.price = 32000
session.commit()

print(f'После изменения: {product.name}, {product.price}')

# Задание № 12 - научиться удалять данные из БД

# находим товар
# first() - возвращает первый результат поиска или None, если объект не был найден
product = session.query(Product).filter(Product.name == 'Наушники').first()

# удаляем товар и сохраняем изменения
session.delete(product)
session.commit()

# -------------------------------------------------------------------------------------------------------------

# Интеграция с FastAPI и модификация проекта product_catalog

# Задание № 14 - реализовать файл database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///products.db', echo=True)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

'''
Мы знаем, что в SQLAlchemy для работы с БД нужна сессия.
Можно было бы в каждом эндпоинте писать подобный код:
'''
session = SessionLocal()                    # создаем сессию
products = session.query(Product).all()     # выполняем операцию с БД
session.close()                             # закрываем сессию

'''
Но тогда приходим к следующим проблемам:
- много повторяющегося кода
- можно забыть закрыть сессию
- код эндпоинтов становится "переполненным"

Решение проблемы - FastAPI позволяет вынести работу с сессией в отдельную функцию-зависимость:
'''
def get_db():
    db = SessionLocal()       # создаем новую сессию
    try:
        yield db              # отдаем ее в эндпоинт
    finally:
        db.close()            # после завершения запроса закрываем соединение

# Задание № 15 - реализовать файл models.py

from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)               
    price = Column(Float, nullable=False)            
    in_stock = Column(Boolean, default=True)

# Задание № 16 - модифицировать файл schemas.py

from pydantic import BaseModel, Field

# схема для создания нового товара
class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(gt=0)
    in_stock: bool = True

# модифицируем схему для возврата данных клиенту
class ProductOut(ProductCreate):
    id: int
    # Сonfig - специальный вложенный класс для настроек Pydantic-модели
    class Config:
        # позволяет возвращать ORM-объекты как JSON
        orm_mode = True 

# схема для частичного обновления
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    in_stock: bool | None = None

# Задание № 17 - реализовать файл repositories/products_repository.py

# подключаем класс Session для указания типа объекта сессии 
from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate, ProductUpdate

# создать новый товар
def create_product(db: Session, product_data: ProductCreate) -> Product:
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    return new_product

# получение списка товаров с фильтрацией
def get_products_list(
    db: Session,
    q: str = None,
    in_stock: bool = None,
    min_price: float = None,
    max_price: float = None
) -> list[Product]:
    # получаем объект Query, который будем дополнять с каждым выполнением .filter(),
    # формируя под капотом оптимизированный SQL-запрос
    result = db.query(Product)

    # проверка фильтров наличия, макс. и мин. цены
    if in_stock is not None:
        result = result.filter(Product.in_stock == in_stock)
    if min_price is not None:
        result = result.filter(Product.price >= min_price)
    if max_price is not None:
        result = result.filter(Product.price <= max_price)
    
    result = result.all()
    '''
    Проверка фильтра q реализуется уже со списком 
    в силу ограничений SQLite на работу с регистром символов кириллицы.
    Ниже приведено не самое оптимальное, но работающее решение.
    '''
    # если передана непустая подстрока для поиска
    if q:
        # все приводим к нижнему регистру и формируем список с совпадениями
        low_q = q.lower()
        result = [p for p in result if low_q in p.name.lower()]
    
    return result

# получение товара по ID
def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()

# полное обновление товара  
# здесь и далее - на вход принимаем не ID товара, а ссылку на объект класса Product,
# что позволяет избежать дублирующихся запросов к БД (сначала в роутере, потом в репозитории)
def put_product(db: Session, product: Product, product_data: ProductCreate) -> Product:
    # превращаем модель в словарь и перебираем все пары ключ-значение 
    for field, value in product_data.model_dump().items():
        # обновляем все атрибуты объекта product
        setattr(product, field, value)
    db.commit()
    return product

# частичное обновление товара
def patch_product(db: Session, product: Product, product_data: ProductUpdate) -> Product:
    updates = product_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)
    db.commit()
    return product

# удаление товара
def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()

# Задание № 18 - реализовать файл routers/products.py

# Depends - функция для создания зависимостей в FastAPI, пригодится для внедрения сессии базы 
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
# подключаем компоненты из ранее созданных модулей
from database import get_db
from models import Product
from schemas import ProductCreate, ProductOut, ProductUpdate
from repositories import products_repository

# создаем объект роутера
router = APIRouter(
    prefix='/products',
    tags=['Products']
)

# вспомогательная функция для проверки наличия товара
def get_product_or_404(db: Session, product_id: int) -> Product:
    product = products_repository.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return product

# создание нового товара
# в response_model указываем схему ProductOut, предназначенную для ответа клиенту
@router.post('', response_model=ProductOut)
# FastAPI вызовет get_db(), создаст сессию и передаст ее в функцию
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    return products_repository.create_product(db, product_data)

# получение списка товаров с фильтрацией
@router.get('', response_model=list[ProductOut])
def get_products_list(
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена'),
    db: Session = Depends(get_db)
):
    return products_repository.get_products_list(db, q, in_stock, min_price, max_price)

# получение одного товара по ID
@router.get('/{product_id}', response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(db, product_id)

# полное обновление товара
@router.put('/{product_id}', response_model=ProductOut)
def put_product(product_id: int, product_data: ProductCreate, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    return products_repository.put_product(db, product, product_data)

# частичное обновление товара
@router.patch('/{product_id}', response_model=ProductOut)
def patch_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    return products_repository.patch_product(db, product, product_data)

# удаление товара
@router.delete('/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_or_404(db, product_id)
    products_repository.delete_product(db, product)
    return {'message': 'Товар удален'}

# Задание № 19 - реализовать файл main.py

from fastapi import FastAPI
from database import Base, engine
from routers import products

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

app.include_router(products.router)

'''
При тестировании приложения можно увидеть, что данные действительно выгружаются
и добавляются в таблицу products.
'''