# Основы аутентификации и авторизации

# OAuth2 в FastAPI

# Задание № 1 - создать базовую структуру проекта
'''
auth_app/ 
├── main.py         # точка входа в приложение
├── security.py     # работа с токенами
└── routers/        # папка с роутерами
    └── users.py    # пользовательские эндпоинты
'''

# Задание № 2 - создать базовое наполнение для auth_app/security.py

# auth_app/security.py

# OAuth2PasswordBearer - класс для аутентификации по паролю через протокол OAuth2.
# Экземпляр класса определяет URL для получения токена и обрабатывает извлечение 
# специального токена Bearer (носитель) из запросов.
from fastapi.security import OAuth2PasswordBearer

# Создаем экземпляр класса OAuth2PasswordBearer. Параметр tokenUrl='token' содержит URL, 
# который клиент будет использовать для отправки username и password, чтобы получить токен 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# Задание № 3 - создать базовое наполнение для auth_app/routers/users.py

# auth_app/routers/users.py

# импортируем инструменты для создания роутера и внедрения зависимости
from fastapi import APIRouter, Depends
# импортируем oauth2_scheme для использования в роли зависимости внутри эндпоинта
from auth_app.security import oauth2_scheme

# создаем роутер с тегом users
router = APIRouter(tags=['users'])

# обрабатываем GET-запрос по маршруту /items
@router.get('/items')
# указываем oauth2_scheme как зависимость для получения токена из заголовка Authorization: Bearer
async def get_items(token: str = Depends(oauth2_scheme)):
    # для демонстрационного примера просто возвращаем полученный токен
    return {'token': token}


# Задание № 4 - создать базовое наполнение для auth_app/main.py

# auth_app/main.py

from fastapi import FastAPI
# импортируем модуль users.py из папки routers/
from auth_app.routers import users

app = FastAPI()

# подключаем роутер из модуля users.py
app.include_router(users.router)

'''
Минимальный код готов, запустим и протестируем наше приложение:
uvicorn auth_app.main:app --reload
'''

# ----------------------------------------------------------------------------------------------------

# Получение информации о пользователе

# Задание № 5 - создать файл auth_app/models.py

# auth_app/models.py

from pydantic import BaseModel

# Pydantic-модель пользователя для возвращения в ответе
class User(BaseModel):
    username: str                   # username пользователя
    email: str | None = None        # адрес электронной почты
    is_active: bool | None = None   # пользователь активен в системе или нет


# Задание № 6 - дополнить файл auth_app/security.py

# auth_app/security.py
...
# подключаем модель User для валидации данных пользователя
from auth_app.models import User
...
# функция для имитации декодирования токена и возвращения данных о пользователе
def decode_token(token: str):
    return User(
        username=token + 'decoded',
        email='dima@mail.ru'
    )


# Задание № 7 - создать файл auth_app/deps.py

# auth_app/deps.py

# импортируем необходимые функции для организации зависимости и получения данных пользователя
from fastapi import Depends
from auth_app.security import oauth2_scheme, decode_token

# указываем oauth2_scheme как зависимость для получения токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # получаем и возвращаем данные о пользователе по указанному токену
    user = decode_token(token)
    return user


# Задание № 8 - дополнить файл auth_app/routers/users.py

# auth_app/routers/users.py
...
# импортируем get_current_user() для использования в качестве зависимости
from auth_app.deps import get_current_user
# импортируем модель User для использования в зависимости
from auth_app.models import User
...
# обрабатываем GET-запрос по маршруту /users/profile
@router.get('/users/profile')
# передаем get_current_user() в качестве зависимости для получения данных о пользователе
async def get_users_profile(current_user: User = Depends(get_current_user)):
    # возвращаем данные о пользователе
    return current_user