# Реализация JWT-авторизации

# --------------------------------------------------------------------------------------

# Установка библиотек для работы с JWT-токенами

# Задание № 1 - установить библиотеку pyjwt

'''
pip install pyjwt 
'''

# Задание № 2 - установить библиотеку pwdlib

'''
pip install "pwdlib[argon2]"
'''

# --------------------------------------------------------------------------------------

# Применение JWT-токенов в проекте

# Задание № 3 - добавить модели Token и TokenData в auth_app/models.py

# auth_app/models.py
...
class Token(BaseModel):
    access_token: str   # значение токена
    token_type: str     # тип токена

class TokenData(BaseModel):
    username: str | None = None     # username, извлеченный из JWT-токена


# Задание № 4 - добавить работу с хэшами в auth_app/security.py

# auth_app/security.py

# PasswordHash - класс для хэширования и проверки паролей
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from auth_app.database import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# создаем экземпляр класса PasswordHash с рекомендованными настройками
password_hash = PasswordHash.recommended()

# функция для хэширования пароля, который пришел от пользователя
def get_password_hash(password):
    return password_hash.hash(password)

# функция для проверки, что полученный пароль соответствует хэшу в БД
def verify_password(plain_password, hashed_password):
    # verify() - метод для проверки, что пароль соответствует указанному хэшу
    return password_hash.verify(plain_password, hashed_password)

# функция для аутентификации и возвращения данных пользователя
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    # если пользователя нет в БД
    if not user:
        return False
    # если указан неверный пароль
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Задание № 5 - добавить работу с JWT-токенами в auth_app/security.py

...
from datetime import datetime, timedelta, timezone
import jwt
...


# в отдельном файле или интерактивной среде

from secrets import token_hex

# пример: efb4d3b0a105afe7b78056264735b37596c40d0840f42c5bb3a4789d3e4662cf
print(token_hex(32))


# auth_app/security.py

...
SECRET_KEY = 'efb4d3b0a105afe7b78056264735b37596c40d0840f42c5bb3a4789d3e4662cf'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
...


# auth_app/security.py

...
# функция для генерации нового JWT-токена
# data - полезная нагрузка токена, expires_delta - на какое время выдавать токен
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # копируем входные данные, чтобы не менять изначальный словарь снаружи
    to_encode = data.copy()
    # если указали expires_delta
    if expires_delta:
        # вычисляем момент истечения токена - текущее время + expires_delta
        expire = datetime.now(timezone.utc) + expires_delta
    # если не указали expires_delta - задаем время жизни токена в 15 минут
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    # добавляем в будущий payload стандартный для JWT заголовок 'exp' (expiration time)
    to_encode.update({'exp': expire})
    # формируем JWT-токен
    encoded_jwt = jwt.encode(
        payload=to_encode,      # итоговая полезная нагрузка
        key=SECRET_KEY,         # секретный ключ для подписи токена
        algorithm=ALGORITHM     # алгоритм шифрования
    )
    return encoded_jwt


# Задание № 6 - обновить зависимость get_current_user() в auth_app/deps.py

# auth_app/deps.py

# обновим импорты
import jwt
from fastapi import HTTPException, Depends
from jwt.exceptions import InvalidTokenError
from auth_app.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from auth_app.database import get_user, users_db
from auth_app.models import User, TokenData

# обновляем функцию-зависимость get_current_user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # отдельно сохраняем исключение для случая, если не удалось подтвердить учетные данные
    credentials_exception = HTTPException(
        status_code = 401,
        detail = 'Не удалось подтвердить учетные данные',
        headers = {'WWW-Authenticate': 'Bearer'}
    )
    # пытаемся декодировать и проверить JWT-токен
    try:
        # декодируем токен и получаем словарь с полезными данными 
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        # достаем поле 'sub', обычно в него кладут идентификатор пользователя,
        # в нашем случае - username
        username = payload.get('sub')
        # если sub отсутствует - токен непригоден для аутентификации
        if username is None:
            raise credentials_exception
        # упаковываем извлеченные данные в Pydantic-модель
        token_data = TokenData(username=username)
    # если при декодировании токена произошла ошибка
    except InvalidTokenError:
        raise credentials_exception
    # ищем пользователя в БД по username из токена
    user = get_user(db=users_db, username=token_data.username)
    # если пользователь не найден
    if user is None:
        raise credentials_exception
    # возвращаем данные пользователя 
    return user

# функция get_current_active_user() останется без изменений
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=403, 
            detail='Пользователь не активен'
        )
    return current_user


# Задание № 7 - обновить эндпоинт login() в auth_app/routers/auth.py

# auth_app/routers/auth.py

# обновим импорты
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException

from auth_app.security import ACCESS_TOKEN_EXPIRE_MINUTES
from auth_app.security import authenticate_user, create_access_token
from auth_app.database import users_db
from auth_app.models import Token

router = APIRouter(tags=['auth'])

# обновляем обработчик запроса POST /token
@router.post('/token')
# указываем, что ответ представляется в виде модели Token
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    # проводим аутентификацию пользователя
    user = authenticate_user(
        db=users_db,
        username=form_data.username,
        password=form_data.password
    )
    # если аутентификация не прошла - возвращаем статус 401
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Неверный логин или пароль',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    # вычисляем срок жизни токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # генерируем JWT-токен
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    # возвращаем объект модели Token
    return Token(access_token=access_token, token_type='bearer')


# Задание № 8 - сгенерировать хэши паролей и добавить их псевдо-БД

# в отдельном файле или интерактивной среде

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
password_1 = 'passworddima'
password_2 = 'passwordmaxim'

hashed_1 = password_hash.hash(password_1)
hashed_2 = password_hash.hash(password_2)

# Хэш для Dima: $argon2id$v=19$m=65536,t=3,p=4$QicTqUD0DIUMxDBcAk6VnQ$b1zYgXTo9fQjFSdIHRQRgLkLdzngmiP1FaK9yq/7l3A
print(f'Хэш для Dima: {hashed_1}')
# Хэш для Maxim: $argon2id$v=19$m=65536,t=3,p=4$3zamDmubR+y8JVnO8S8a6A$gDpxNTbBXRMzN5prFhjaZn1HEximzl/mRus1qD0H1NE
print(f'Хэш для Maxim: {hashed_2}')


# auth_app/database.py
...
users_db: dict[str, dict] = {
    'Dima': {
        'username': 'Dima',                     
        'email': 'dima@mail.ru',
        'is_active': True,
        'hashed_password': '$argon2id$v=19$m=65536,t=3,p=4$QicTqUD0DIUMxDBcAk6VnQ$b1zYgXTo9fQjFSdIHRQRgLkLdzngmiP1FaK9yq/7l3A'
    },
    'Maxim': {
        'username': 'Maxim',
        'email': 'maxim@mail.ru',
        'is_active': False,
        'hashed_password': '$argon2id$v=19$m=65536,t=3,p=4$3zamDmubR+y8JVnO8S8a6A$gDpxNTbBXRMzN5prFhjaZn1HEximzl/mRus1qD0H1NE'
    }
}
...

# Задание № 9 - модифицировать эндпоинт get_users_profile() в auth_app/routers/users.py

# auth_app/routers/users.py
...
@router.get('/users/profile', response_model=User)
...

@router.get('/items')
# укажем зависимость get_current_active_user(), чтобы работало только с активными пользователями
async def get_items(current_user: User = Depends(get_current_active_user)):
    # возвращаем список с данными
    return [{'item_id': '4815162342', 'owner': current_user.username}]