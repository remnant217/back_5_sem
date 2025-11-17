# Основы аутентификации и авторизации 2

# Хэширование паролей

password = 'qwerty12345'
hash_password = hash(password)
print(hash_password)        # что-то вроде 753960335293711223


password = 'qwerty12345'
new_password = 'qwerty123456'
hash_password = hash(password)
hash_new_password = hash(new_password)
print(hash_password)        # что-то вроде 4744082833861004866
print(hash_new_password)    # что-то вроде -5111911851106947240


password = 'qwerty12345'
new_password = 'qwerty12345'
hash_password = hash(password)
hash_new_password = hash(new_password)
print(hash_password)        # что-то вроде 8265879366869058671
print(hash_new_password)    # тот же хэш   8265879366869058671

# --------------------------------------------------------------------------------------

# Добавление ввода username и password

# Задание № 1 - добавить в auth_app/models.py модель UserInDB

# auth_app/models.py
...
# модель для хранения информации о пользователе в БД
class UserInDB(User):
    hashed_password: str


# Задание № 2 - создать и заполнить файл auth_app/database.py

# auth_app/database.py

# импортируем модель UserInDB для валидации данных внутри функции
from auth_app.models import UserInDB

# псевдо-БД с данными
# пока что для простоты хэши составляются из пароля и строки hashed слева
users_db: dict[str, dict] = {
    'Dima': {
        'username': 'Dima',                     
        'email': 'dima@mail.ru',
        'is_active': True,
        'hashed_password': 'hashedpassworddima'
    },
    'Maxim': {
        'username': 'Maxim',
        'email': 'maxim@mail.ru',
        'is_active': False,
        'hashed_password': 'hashedpasswordmaxim'
    }
}

# получение данных указанного пользователя, если он есть в БД
def get_user(db: dict[str, dict], username: str) -> UserInDB | None:
    if username in db:
        # получаем данные о пользователе из БД
        user_dict = db[username]
        # распаковываем словарь и передаем значения в соответствующие поля модели UserInDB
        return UserInDB(**user_dict)


# Задание № 3 - добавить в auth_app/security.py работу с псевдо-хэшированием

# auth_app/security.py

from fastapi.security import OAuth2PasswordBearer
# импортируем инструменты для работы с нашей псевдо-БД
from auth_app.database import users_db, get_user
# вместо User используем модель UserInDB
from auth_app.models import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# функция для псевдо-хэширования пароля (просто добавляем слева к паролю строку 'hashed')
def hash_password(password: str) -> str:
    return 'hashed' + password

# добавляем использование get_user() для извлечения данных из БД 
# и валидацию через модель UserInDB
def decode_token(token) -> UserInDB | None:
    user = get_user(users_db, token)
    return user


# Задание № 4 - создать и заполнить файл auth_app/routers/auth.py

# auth_app/routers/auth.py

# OAuth2PasswordRequestForm - класс-зависимость, работающий с телом формы
# для аутентификации по протоколу OAuth2
from fastapi.security import OAuth2PasswordRequestForm
# импортируем инструменты для создания роутера, внедрения зависимости и 
# генерации исключения, если пользователя нет в БД или введен неверный пароль
from fastapi import APIRouter, Depends, HTTPException

# импортируем созданные нами инструменты для работы с данными БД и хэшированием пароля
from auth_app.security import hash_password
from auth_app.database import users_db
from auth_app.models import UserInDB

# создаем роутер с тегом auth
router = APIRouter(tags=['auth'])

# обработка POST-запроса по маршруту /token
@router.post('/token')
# принимаем данные из формы через зависимость в виде OAuth2PasswordRequestForm
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # username - поле объекта OAuth2PasswordRequestForm, где хранится отправленный username
    # получаем данные из нашей БД по ключу username
    user_dict = users_db.get(form_data.username)
    # если пользователя нет в БД - возвращаем ошибку со статусом "Неверный логин или пароль"
    if not user_dict:
        raise HTTPException(
            status_code=400,
            detail='Неверный логин или пароль'
        )
    # валидируем полученные данные через Pydantic-модель UserInDB
    user = UserInDB(**user_dict)
    # password - поле объекта OAuth2PasswordRequestForm, где хранится отправленный password
    # генерируем хэш на основании отправленного пароля
    hashed_password = hash_password(form_data.password)
    # если хэши не совпали - возвращаем ошибку со статусом "Неверный логин или пароль"
    if hashed_password != user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail='Неверный логин или пароль'
        )
    # возвращаем токен пользователю, пока для простоты - это username
    # явно указываем, что тип токена - 'bearer'
    return {'access_token': user.username, 'token_type': 'bearer'}


# Задание № 5 - подключить новый роутер в auth_app/main.py

# auth_app/main.py

# импортируем модуль auth
from auth_app.routers import users, auth
...
# подключаем роутер из модуля auth.py
app.include_router(auth.router)


# Задание № 6 - обновить функции-зависимости в auth_app/deps.py

# auth_app/deps.py

# дополнительно импортируем HTTPException
from fastapi import Depends, HTTPException
from auth_app.security import oauth2_scheme, decode_token
# импортируем модель User для использовании в зависимости
from auth_app.models import User

# обновляем get_current_user()
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    # если пользователь не был найден - возвращаем ошибку со статусом "Неверные данные аутентификации"
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Неверные данные аутентификации',
            # указываем заголовок 'WWW-Authenticate': 'Bearer', этого требует спецификация OAuth2
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return user

# новая зависимость для проверки активности пользователя
# внедряем get_current_user() как зависимость, чтобы не дублировать код 
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    # если пользователь неактивен - возвращаем ошибку со статусом "Пользователь неактивен"
    if not current_user.is_active:
        raise HTTPException(
            status_code=403, 
            detail='Пользователь неактивен'
        )
    # возвращаем данные активного пользователя
    return current_user


# Задание № 7 - обновить зависимость в эндпоинте get_users_profile()

# auth_app/routers/users.py
...
# вместо get_current_user импортируем get_current_active_user
from auth_app.deps import get_current_active_user
...
# вместо get_current_user указываем get_current_active_user
async def get_users_profile(current_user: User = Depends(get_current_active_user)):...