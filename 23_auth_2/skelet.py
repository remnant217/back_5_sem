# Основы аутентификации и авторизации 2

# Хэширование паролей
'''
На предыдущем занятии мы начали выстраивать систему аутентификации и авторизации
внутри FastAPI-приложения. Сегодня мы продолжим работу над проектом с предыдущего
занятия и в первой части урока добавим псевдо-БД с данными пользователей, а также
напишем код для возможности отправки username и password на сервер.

Прежде, чем мы создадим псевдо-БД с данными пользователей, обсудим вопрос хранения
паролей пользователей. В реальной разработке некоторые данные пользователей, в том
числе и пароли, хранятся в зашифрованном виде, а точнее - в виде хэшей. 
С хэширование вы должны быть знакомы с курса по алгоритмам и структурам данных,
но давайте вспомним основные моменты.

Хэширование - процесс преобразования данных в строку фиксированной длины,
которая называется хэшем.
Цель хэширования - создать уникальный "слепок" данных, который однозначно
идентифицирует исходный объект. При этом восстановление исходной информации
по хэшу практически невозможно.

Теперь посмотрим как это работает с паролями. Например, у нас есть пароль
в виде строки и мы хотим получить его хэш. Для примера нам достаточно
встроенной функции hash():
'''
password = 'qwerty12345'
hash_password = hash(password)
print(hash_password)        # что-то вроде 753960335293711223

'''
Если мы поменяем хотя бы 1 символ в пароле, то хэш будет другим:
'''
password = 'qwerty12345'
new_password = 'qwerty123456'
hash_password = hash(password)
hash_new_password = hash(new_password)
print(hash_password)        # что-то вроде 4744082833861004866
print(hash_new_password)    # что-то вроде -5111911851106947240

'''
Но если мы найдем хэш для двух одинаковых паролей, то увидим, что они совпадают:
'''
password = 'qwerty12345'
new_password = 'qwerty12345'
hash_password = hash(password)
hash_new_password = hash(new_password)
print(hash_password)        # что-то вроде 8265879366869058671
print(hash_new_password)    # тот же хэш   8265879366869058671

'''
На основании этих механизмов и происходит проверка пароля пользователя:
1. Пользователь вводит username и password на сайте через форму
2. Данные из формы передаются на сервер
3. Ведется поиск username в базе данных
4. Вычисляется хэш из переданного password
5. Если хэш из password совпал с хэшем в БД - проверка пройдена
6. При успешной проверке сервер генерирует токен доступа и отправляет его клиенту

Возникает только один вопрос - зачем в БД хранить хэши, а не пароли в явном виде?
Все дело в безопасности. Если по какой-нибудь причине данные из БД будут украдены,
то злоумышленник не получит явные пароли ваших пользователей, только хэши.
А декодировать хэш и получить пароль обратно, как мы знаем, практически невозможно.
Итог - злоумышленник не сможет воспользоваться украденными данными, чтобы, например,
войти в аккаунты ваших пользователей.
'''

# --------------------------------------------------------------------------------------

# Добавление ввода username и password

# Задание № 1 - добавить в auth_app/models.py модель UserInDB

'''
С концепцией хранения паролей в виде хэшей разобрались, теперь перейдем к реализации этой идеи.
В файле models.py добавим еще одну Pydantic-модель, которая будет хранить те же поля, что и User,
но с добавлением пароля в виде хэша:
'''

# auth_app/models.py
...
# модель для хранения информации о пользователе в БД
class UserInDB(User):
    hashed_password: str


# Задание № 2 - создать и заполнить файл auth_app/database.py

'''
Модель для хранения данных пользователя в БД готова, теперь можем реализовать саму псевдо-БД.
Для этого создадим новый файл - database.py. Внутри файла создадим словарь users_db, где также
в виде словарей будут храниться данные пользователей. Также создадим функцию get_user(), которая
будет возвращать данные из БД для указанного пользователя, если он есть в БД:
'''

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

'''
С database.py разобрались, теперь оформим работу с псевдо-хэшированием в файле security.py - 
модифицируем уже имеющуюся функцию decode_token() и создадим новую функцию hash_password()
для псевдо-хэширования паролей. Полный код будет выглядеть следующим образом:
'''

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

'''
Замечательно, с модулем security.py также разобрались. Теперь двинемся к реализации проверки username
и password. То есть пользователь будет заполнять форму на сайте и когда нажмет кнопку "Отправить" - сработает
POST-запрос к нашему API для валидации данных. Для реализации данной логики в папке routers/ мы создадим
отдельный модуль auth.py, в котором реализуем эндпоинт для принятия и валидации username и password от
пользователя:
'''

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

'''
Новый роутер и эндпоинт готовы, сразу подключим их в файле main.py:
'''

# auth_app/main.py

# импортируем модуль auth
from auth_app.routers import users, auth
...
# подключаем роутер из модуля auth.py
app.include_router(auth.router)


# Задание № 6 - обновить функции-зависимости в auth_app/deps.py

'''
Теперь поработаем с зависимостями в файле deps.py.
Пока что там есть только одна зависимость - get_current_user(). Мы обновим ее,
добавив возвращение HTTPException, если пользователь не был найден в БД.
Также мы добавим новую зависимость get_current_active_user(), которая проверять, является
ли пользователь активным. То есть после аутентификации личность может быть подтверждена,
но доступ к ресурсу запрещен, т.к. учетная запись пользователя отключена.
Полный код файла deps.py будет выглядеть так:
'''

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

'''
Осталось обновить зависимость в эндпоинте get_users_profile() из модуля routers/users.py, 
чтобы мы возвращали данные только активных пользователей. Достаточно вместо get_current_user 
указать get_current_active_user:
'''

# auth_app/routers/users.py
...
# вместо get_current_user импортируем get_current_active_user
from auth_app.deps import get_current_active_user
...
# вместо get_current_user указываем get_current_active_user
async def get_users_profile(current_user: User = Depends(get_current_active_user)):...

# --------------------------------------------------------------------------------------

# Тестирование проекта

'''
Давайте протестируем наше приложение и посмотрим как работает аутентификация.

СОВЕТ ПРЕПОДАВАТЕЛЮ: если при запуске приложения появилась ошибка "RuntimeError: Form data requires "python-multipart" to be installed.",
то установите дополнительно модуль python-multipart с помощью команды pip install python-multipart.
Этот модуль нужен для обработки запросов с данными, например, из форм.

Нажмем на кнопку "Authorize" сверху справа и попробуем ввести данные пользователя из нашей БД:
username: Dima
password: passworddima

Затем нажмем снизу зеленую кнопку "Authorize". После этого появится окно с введенными данными и строкой "Authorized".
Значит аутентификация прошла успешно! Закроем это окно и попробуем воспользовался эндпоинтом GET /users/profile.
В результате в Response body увидим следующее:
{
  "username": "Dima",
  "email": "dima@mail.ru",
  "is_active": true,
  "hashed_password": "hashedpassworddima"
}

Мы успешно получили данные пользователя. Если же мы снова нажмем на кнопку "Authorize" сверху справа и выйдем из учетной записи с помощью
кнопки "Logout", то повторный тест эндпоинта GET /users/profile закончится статусом 401, а в Response body увидим:
{
  "detail": "Not authenticated"
}

Теперь попробуем зайти под неактивным пользователем, у нас в БД это Maxim:
username: Maxim
password: passwordmaxim

Если теперь протестируем эндпоинт GET /users/profile, то появится статус 403, а в Response body увидим:
{
  "detail": "Пользователь не активен"
}

Теперь у нас есть инструменты для аутентификации и авторизации через username и password, используя
протокол OAuth2. Финальная вещь, которую нам нужно доделать - это безопасное хэширование паролей
и использование так называемых JWT-токенов.
'''