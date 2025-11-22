# Воркшоп. Архитектура и авторизация API

# Установка зависимостей проекта
'''
Начнем, как и всегда - создадим пустую папку для работы с проектом. Внутри создадим и активируем виртуальное окружение:

В терминале:
python -m venv venv
venv\scripts\activate

Теперь установим в виртуальное окружение необходимые библиотеки. Их будет немало, поэтому чуть позже мы сделаем
одно дополнительне действие:

В терминале:
pip install fastapi uvicorn sqlalchemy alembic aiosqlite loguru pyjwt python-multipart "pwdlib[argon2]" 

После установки сохраним все наши зависимости в файл requirements.txt:

В терминале:
pip freeze > requirements.txt

Теперь, если кто-нибудь другой захочет запустить наш проект у себя, то ему достаточно будет взять файл
requirements.txt и выполнить команду:

В терминале:
pip install -r requirements.txt

Супер, папка venv и файл requirements.txt готовы. На данный момент содержимое нашего проекта выглядит так:

fastapi_workshop/           
├─ venv/   
└─ requirements.txt                        
'''

# -----------------------------------------------------------------------------------------------------------

# Products. Создание моделей
'''
Как вы заметили ранее, исходные файлы нашего приложения будут распределены по отдельным файлам и папкам.
Для начала создадим папку app/, где будут лежать исходные файлы нашего приложения:

fastapi_workshop/  
├─ app/          
├─ venv/   
└─ requirements.txt                        

Большую часть времени мы будем проводить именно в папке app/.

В начале мы создадим файлы, связанные с товарами (Products). Начнем с моделей данных,
для этого внутри папки app/ создадим папку /models:

app/
└─ models/

Внутри папки models/ для начала создадим файл __init__.py, где создадим класс Base 
для дальнейшего переиспользования в файлах внутри папки models/:
'''

# app/models/__init__.py

from sqlalchemy.orm import DeclarativeBase

# базовый класс для создания ORM-моделей таблиц 
class Base(DeclarativeBase):
    pass

'''
Готово, теперь создадим файл products.py внутри папки models/.
Там мы создадим SQLAlchemy-модель будущей таблицы "Продукты" и 
Pydantic-модели для операций с продуктами:
'''

# app/models/products.py

from sqlalchemy import Column, Integer, String, Float, Boolean
from pydantic import BaseModel, Field
from app.models import Base

# модель таблицы "Продукты"
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)

# базовая модель продукта
class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    price: float = Field(ge=0)
    in_stock: bool = True

# модель продукта при его создании
class ProductCreate(ProductBase):
    pass

# модель продукта при его обновлении
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=128)
    price: float | None = Field(default=None, ge=0)
    in_stock: bool | None = None

# модель продукта при его возвращении по API
class ProductOut(ProductBase):
    id: int
    model_config = {'from_attributes': True}

# -----------------------------------------------------------------------------------------------------------

# Создание app/core/database.py
'''
Прежде, чем мы двинемся дальше в работе с products, нам необходимы создать объекты для работы с БД.
Для этого внутри папки app/ создадим новую папку - core/, где будут лежать базовые технические
компоненты нашего приложения. Без них API и другие элементы не заработают:

app/  
├─ core/   
└─ models/          

Внутри папки core/ создадим файл database.py, где и опишем необходимые для работы с БД объекты:
'''

# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# асинхронное подключение для работы с API
DATABASE_ASYNC = 'sqlite+aiosqlite:///./products.db'
# синхронное подключение для работы с alembic
DATABASE_SYNC = 'sqlite:///./products.db'

# асинхронный движок для работы с БД
engine = create_async_engine(url=DATABASE_ASYNC, echo=False)
# фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

'''
Готово, database.py создан, его содержимым мы сейчас будем пользоваться
при работе с продуктами.
'''

# -----------------------------------------------------------------------------------------------------------

# Products. Работа с БД
'''
Возвращаемся к работе с products. Внутри папки app/ создадим еще одну новую папку repositories/, где будет
храниться логика доступа к данным через БД. 

app/
├─ core/
├─ models/
└─ repositories/

Внутри папки repositories/ создадим файл products.py, где опишем функции для создания, обновления и получения
продукта по ID:
'''

# app/repositories/products.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product, ProductCreate, ProductUpdate

# создание нового продукта
async def create_product(session: AsyncSession, product_create: ProductCreate) -> Product:
    product_data = product_create.model_dump()
    new_product = Product(**product_data)
    session.add(new_product)
    await session.commit()
    return new_product

# обновление данных продукта
async def update_product(session: AsyncSession, product_db: Product, product_update: ProductUpdate) -> Product:
    product_data = product_update.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        setattr(product_db, key, value)
    session.add(product_db)
    await session.commit()
    return product_db

# получение продукта по ID
async def get_product_by_id(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)

# -----------------------------------------------------------------------------------------------------------

# Создание app/api/deps.py
'''
Перед тем, как мы будем описывать эндпоинты для продуктов, нам необходимо создать функцию-зависимость
для генерации новой сессии с БД. Все зависимости нашего проекта мы будем выносить в отдельный файл.
Поэтому сначала создадим папку api/, где будет храниться логика работы эндпоинтов и необходимые для их
работы зависимостей:

app/
├─ api/
├─ core/
├─ models/
└─ repositories/

Внутри папки api/ создадим файл deps.py, где будут содержаться зависимости, необходимые для 
работы наших эндпоинтов. Сейчас пока что создадим только функцию-зависимость для генерации новой сессии с БД:
'''

# app/api/deps.py

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal

# функция-зависимость для генерации новой сессии
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# создаем краткую версию зависимости для использования в других модулях
SessionDep = Annotated[AsyncSession, Depends(get_session)]

'''
Зависимость готова, можно переходить к созданию эндпоинтов для работы с продуктами.
'''

# -----------------------------------------------------------------------------------------------------------

# Products. Создание роутера
'''
У нас все готово к тому, чтобы создать эндпоинты для работы с продуктами и объединить их в один роутер.
Для этого внутри папки api/ создадим папку routes/, где будут содержаться файлы со всеми роутерами и эндпоинтами
нашего приложения.

api/
├─ routes/
└─ deps.py

В папке routes/ создадим файл products.py, где укажем роутер и эндпоинты для работы с товарами.
Опираться будем на созданные модели и функции для работы с БД:
'''

# app/api/routes/products.py

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.products import ProductOut, ProductCreate, ProductUpdate
from app.repositories.products import (
    get_product_by_id, 
    create_product as create_product_repo,
    update_product as update_product_repo
)

router = APIRouter(prefix='/products', tags=['products'])

# получаем продукт по ID
@router.get('/{product_id}', response_model=ProductOut)
async def get_product(session: SessionDep, product_id: int):
    product = await get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Продукт не найден')
    return product

# создаем новый продукт
@router.post('/', response_model=ProductOut)
async def create_product(session: SessionDep, product_data: ProductCreate):
    new_product = await create_product_repo(session=session, product_create=product_data)
    return new_product

# обновляем продукт
@router.put('/{product_id}', response_model=ProductOut)
async def update_product(session: SessionDep, product_id: int, product_data: ProductUpdate):
    product_db = await get_product_by_id(session=session, product_id=product_id)
    if not product_db:
        raise HTTPException(
            status_code=404,
            detail='Продукт не найден',
        )
    
    updated_product = await update_product_repo(
        session=session,
        product_db=product_db,
        product_update=product_data,
    )
    return updated_product

# -----------------------------------------------------------------------------------------------------------

# Настройка Alembic

'''
Перед тем как идти к тестированию созданных эндпоинтов, нам необходимо инициализировать работу с Alembic и создать
файл БД. Для начала из корневой папки проекта, в терминале, выполним следующую команду:

В терминале:
alembic init alembic

После этого в нашем проекте появятся следующие файлы Alembic:

fastapi_workshop/
├─ alembic.ini
├─ alembic/
│  ├─ env.py
│  ├─ README
│  ├─ script.py.mako
│  └─ versions/

Далее нам нужно подготовить файл app/models/__init__.py, чтобы Alembic видел все таблицы. 
Для этого укажем импорты таблиц User и Product после объявления класса Base:
'''

# app/models/__init__.py
...
# импорты моделей для корректной работы Alembic
from app.models.products import Product
from app.models.users import User

'''
Готово! Далее нам необходимо корректно настроить файл alembic/env.py.
Что нужно сделать:
1) Импортировать DATABASE_SYNC и Base
2) Указать target_metadata = Base.metadata
3) В run_migrations_offline и run_migrations_online использовать DATABASE_SYNC
'''

# alembic/env.py
...
# импортируем настройки БД и Base из нашего приложения
from app.core.database import DATABASE_SYNC
from app.models import Base
...
# указываем Base.metadata
target_metadata = Base.metadata
...
def run_migrations_offline() -> None:
    # указываем URL нашей БД
    url = DATABASE_SYNC
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
...
def run_migrations_online() -> None:
    # переопределяем URL из alembic.ini на наш DATABASE_SYNC
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = DATABASE_SYNC

    connectable = engine_from_config(
        # указываем созданную конфигурацию
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
...
'''
Теперь мы готовы создать первую миграцию. Для этого, из корневой папки проекта, в терминале, выполним следующую команду:

В терминале:
alembic revision --autogenerate -m "init db"

Если все настроено верно, то Alembic:
- подключится к sqlite:///./products.db
- прочитает Base.metadata
- создаст файл в migrations/versions/ с SQL для создания таблиц Users и Products

Также при этом появится файл products.db в корневой папке нашего проекта.

Можно проверить файл миграций в migrations/versions/ - там должен быть код для создания таблиц.

Финальный шаг - применим миграции к базе, для этого выполним команду:

В терминале:
alembic upgrade head

Так мы создадим файл products.db и внутри появятся все таблицы.
Супер, мы настроили Alebmic и можем двигаться дальше работать с products.
'''

# -----------------------------------------------------------------------------------------------------------

# Подключение products в main.py
'''
Базовый код для работы с продуктами мы написали, теперь проверим его работоспособность.
Для этого создадим файл main.py в папке app/ на уровне с существующими папками:

app/
├─ api/
├─ core/
├─ models/
├─ repositories/
└─ main.py

Внутри main.py создадим экземпляр класса FastAPI и подключим роутер из app/api/routes/products.py:
'''

# app/main.py

from fastapi import FastAPI
from app.api.routes import products

app = FastAPI()

app.include_router(products.router)

'''
Теперь можно запустить наше приложение с помощью привычной команды:

uvicorn app.main:app --reload

Перейдем к документации по адресу http://127.0.0.1:8000/docs и протестируем созданные эндпоинты.
'''

# -----------------------------------------------------------------------------------------------------------

# Users. Создание моделей
'''
Итак, код для работы с продуктами мы написали, а также реализовали работу с БД через Alembic.
Сейчас мы приступаем к реализации логики, связанной с пользователями (Users). Будем идти
по такому же сценарию, как и с продуктами, поэтому начнем с создания моделей. Внутри папки models/
создадим файл users.py. Там мы создадим SQLAlchemy-модель будущей таблицы "Пользователи" и 
Pydantic-модели для операций с пользователями:

models/ 
├─ __init__.py 
├─ products.py 
└─ users.py
'''

# app/models/users.py

from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field
from app.models import Base

# модель таблицы "Пользователи"
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    full_name = Column(String(128), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

# базовая модель пользователя
class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=128)

# модель пользователя при регистрации
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)

# модель пользователя при обновлении
class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=64)
    password: str | None = Field(default=None, min_length=8, max_length=64)
    full_name: str | None = Field(default=None, max_length=128)

# модель пользователя при его возвращении по API
class UserOut(UserBase):
    id: int
    model_config = {'from_attributes': True}

# -----------------------------------------------------------------------------------------------------------

# Создание app/models/tokens.py

'''
Прежде, чем двигаться к реализации функций и эндпоинтов для работы с пользователями, нам также нужно
прописать логику для работы с аутентификацией и авторизацией. Начнем с того, что создадим Pydantic-модели
для работы с токенами. Для этого создадим файл tokens.py в папке models/:

models/ 
├─ __init__.py 
├─ products.py 
├─ tokens.py 
└─ users.py
'''

# app/models/tokens.py

from pydantic import BaseModel

# модель токена доступа
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

# модель содержимого JWT-токена 
class TokenData(BaseModel):
    sub: str | None = None

# -----------------------------------------------------------------------------------------------------------

# Создание app/core/security.py
'''
Модели с токенами готовы, теперь реализуем необходимые функции, связанные с генерацией хэшем пароля,
сравнением пароля с предполагаемым хэшем и созданием JWT-токена. Для этого в папке core/ создадим
файл security.py:

core/ 
├─ database.py 
└─ security.py
'''

# app/core/secutiry.py

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

SECRET_KEY = 'a1e1abda8dd3079c07cd9a0f7b7e348476ee1b2c16dbe44d1653bd342f17f287'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

# вычислить хэш для пароля
def get_password_hash(password):
    return password_hash.hash(password)

# сравнить пароль с предполагаемым хэшем
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

# создать JWT-токен
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,      
        key=SECRET_KEY,         
        algorithm=ALGORITHM    
    )
    return encoded_jwt

# -----------------------------------------------------------------------------------------------------------

# Users. Работа с БД

'''
Вернемся к работе непосредственно c users.
Внутри папки repositories/ создадим файл users.py, где опишем функции для регистрации, аутентификации, 
обновления и получения данных о пользователе по username и ID:

repositories/ 
├─ users.py 
└─ products.py
'''

# app/repositories/users.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models.users import User, UserCreate, UserUpdate

# регистрация нового пользователя
async def create_user(session: AsyncSession, user_create: UserCreate) -> User:
    user_data = user_create.model_dump(exclude={'password'})
    new_user = User(
        **user_data,
        hashed_password=get_password_hash(user_create.password)
    )
    session.add(new_user)
    await session.commit()
    return new_user

# обновление данных пользователя
async def update_user(session: AsyncSession, user_db: User, user_update: UserUpdate) -> User:
    user_data = user_update.model_dump(exclude_unset=True)
    if 'password' in user_data:
        new_password = user_data.pop('password')
        user_db.hashed_password = get_password_hash(new_password)
    for key, value in user_data.items():
        setattr(user_db, key, value)
    session.add(user_db)
    await session.commit()
    return user_db
    
# получение пользователя по username
async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    return user

# получение пользователя по ID
async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

# аутентификация пользователя
async def authenticate(session: AsyncSession, username: str, password: str) -> User | None:
    user_db = await get_user_by_username(session=session, username=username)
    if not user_db:
        return None
    if not verify_password(password, user_db.hashed_password):
        return None
    return user_db

# -----------------------------------------------------------------------------------------------------------

# Дополнение app/api/deps.py
'''
Перед тем, как создавать роутер и эндпоинты для users, дополним файл deps.py логикой получения текущего пользователя:
'''

# app/api/deps.py

...
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from app.core.security import SECRET_KEY, ALGORITHM
from app.models.tokens import TokenData
from app.models.users import User
from app.repositories.users import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login/access-token')
...
# получаем текущего пользователя
async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code = 401,
        detail = 'Не удалось подтвердить учетные данные',
        headers = {'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        token_data = TokenData(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    
    user = await get_user_by_username(session=session, username=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Неактивный пользователь')
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

# -----------------------------------------------------------------------------------------------------------

# Users. Создание роутера
'''
Теперь можем переходим обратно к Users.
В папке routes/ создадим файл users.py, где укажем роутер и эндпоинты для работы с пользователями.
Опираться будем на созданные модели и функции для работы с БД:

routes/ 
├─ products.py
└─ users.py
'''

# app/api/routes/users.py

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep, CurrentUserDep
from app.models.users import UserCreate, UserUpdate, UserOut
from app.repositories.users import (
    create_user as create_user_repo,
    update_user as update_user_repo,
    get_user_by_username,
    get_user_by_id
)

router = APIRouter(prefix='/users', tags=['users'])

# получить текущего пользователя
@router.get('/me', response_model=UserOut)
async def get_user_me(current_user: CurrentUserDep):
    return current_user

# получить пользователя по username
@router.get('/{username}', response_model=UserOut)
async def get_user(session: SessionDep, username: str):
    user = await get_user_by_username(session=session, username=username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )
    return user

# создать нового пользователя
@router.post('/', response_model=UserOut)
async def create_user(session: SessionDep, user_data: UserCreate):
    new_user = await create_user_repo(session=session, user_create=user_data)
    return new_user

# обновить данные пользователя по id
@router.put('/{user_id}', response_model=UserOut)
async def update_user(user_id: int, user_data: UserUpdate, session: SessionDep) -> UserOut:
    user_db = await get_user_by_id(session=session, user_id=user_id)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )

    updated_user = await update_user_repo(
        session=session,
        user_db=user_db,
        user_update=user_data,
    )
    return updated_user

# -----------------------------------------------------------------------------------------------------------

# Users. Вход в систему и получение токена

'''
Финальный шаг при работе с пользователями - реализуем логику входа пользователя в систему и получения токена.
Для этого в папке routes/ создадим создадим файл login.py, где создадим роутер и эндпоинт для реализации
описанной логики:

routes/
├─ login.py
├─ products.py
└─ users.py
'''

# app/api/routers/login.py

from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token
from app.api.deps import SessionDep
from app.models.tokens import Token
from app.repositories.users import authenticate

router = APIRouter(tags=['login'])

# вход в систему и получение токена
@router.post("/login/access-token")
async def login_access_token(
    session: SessionDep, 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user = await authenticate(
        session=session,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Неверный логин или пароль',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail='Неактивный пользователь')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type='bearer')

# -----------------------------------------------------------------------------------------------------------

# Подключение users и login в main.py

'''
Внутри main.py подключим роутеры из app/api/routes/users.py и app/api/routes/login.py:
'''

# app/main.py

from app.api.routes import products, users, login
...
app.include_router(users.router)
app.include_router(login.router)

'''
Теперь можно запустить наше приложение и протестируем созданные эндпоинты
для работы с пользователями.
'''

# -----------------------------------------------------------------------------------------------------------

# Создание app/core/logging.py

'''
Нам осталось реализовать логирование в нашем проекте и работу с middleware. Начнем с логирования,
т.к. его мы будем в будущем middleware. Для этого в папке core/ создадим файл logging.py, где
опишем функцию с настройкой источников логирования для проекта. Нам достаточно указать
логика сохранения логов в отдельную папку logs/. В терминал логи выводить необязательно,
с этим пока хорошо справляется сам FastAPI:

core/ 
├─ database.py 
├─ logging.py 
└─ security.py 
'''

# app/core/logging.py

import os
from loguru import logger

# настройка источников логирования для проекта
def setup_logging():
    logger.remove()

    # подготавливаем папку для хранения лог-файлов
    os.makedirs('logs', exist_ok=True)

    # логирование в logs/app.log (все логи)
    logger.add(
        sink='logs/app.log',
        level='INFO',
        format='{time:HH:mm:ss} | {level:8} | {name}:{function}:{line} | {message}',
        rotation='10 MB',    
        retention='7 days',    
        compression='zip',
    )

# -----------------------------------------------------------------------------------------------------------

# Добавление логирования в app/api/routes/login.py
'''
Добавим минимальное логирование в наш проект - в файле login.py добавим вывод логов в файл
для следующих ситуаций:
- Неудачная попытка входа
- Неактивный пользователь попытался войти в систему
- Пользователь успешно вошел в систему
'''

# app/api/routes/login.py
...
if not user:
    logger.warning(f'Неудачная попытка входа: username={form_data.username}')
    raise HTTPException(
    ...
...
elif not user.is_active:
    logger.warning(f'Неактивный пользователь попытался войти в систему: username={user.username}')
    ...
...
logger.info(f'Пользователь успешно вошел в систему: username={user.username}')
return Token(access_token=access_token, token_type='bearer')

# -----------------------------------------------------------------------------------------------------------

# Создание app/core/middleware.py

'''
Логирование готово, теперь создадим middleware, с помощью которого будем замерять время выполнения запроса.
Для этого создадим файл middleware.py в папке core/.
Вычисленное время будет сохраняться в логи и возвращаться в ответе:

core/ 
├─ database.py 
├─ logging.py 
├─ middleware.py 
└─ security.py
'''

# app/core/middleware.py

from time import perf_counter
from fastapi import FastAPI, Request
from loguru import logger

# функция-обертка для запуска middleware
def setup_middleware(app: FastAPI):
    # создаем middleware для добавления времени выполнения запроса в заголовок ответа
    @app.middleware('http')
    async def add_process_time_header(request: Request, call_next):
        start_time = perf_counter()
        response = await call_next(request)
        # вычисляем время работы запроса в миллисекундах
        process_time = (perf_counter() - start_time) * 1000
        logger.info(f'{request.method} {request.url.path} выполнялся {process_time:.2f} мс')
        response.headers['X-Process-Time-ms'] = f'{process_time:.2f}'
        return response

# -----------------------------------------------------------------------------------------------------------

# Подключение логирования и middleware в main.py

'''
Логирование и middleware готовы, подключим их в main.py:
'''

# app/main.py
...
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
...
setup_logging()
...
setup_middleware(app)

'''
Замечательно, друзья! Наш по истине огромный проект завершен! Можем протестировать
его возможности через Swagger UI, проверить логи в папке logs/, а также при желании
просмотреть содержимое нашей БД products.db.
'''