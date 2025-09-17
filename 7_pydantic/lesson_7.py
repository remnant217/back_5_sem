# Pydantic и валидация данных

# Повторение JSON

# Задание № 1 - загрузить и выгрузить обратно данные из JSON-файла с помощью модуля json 

import json

# словарь с данными пользователя
user_data = {
    'username': 'Дима',
    'email': 'dima12348@mail.ru',
    'age': 27
}

# сохраняем данные в JSON-файл с учетом кириллицы
with open('user.json', 'w', encoding='utf-8') as f:
    json.dump(user_data, f, indent=2, ensure_ascii=False)

# загружаем данные из JSON-файла в программу
with open('user.json', encoding='utf-8') as f:
    data = json.load(f)

# выводим загруженные данные в терминал
print(data)     # {'username': 'Дима', 'email': 'dima12348@mail.ru', 'age': 27}

# Задание № 2 - посмотреть на пример ошибки при обработке JSON-файла

user_data = {
    'username': 'Дима',
    'age': 'двадцать семь'
}

# функция для обработки данных пользователя
def greet_user(data):
    return f'{data['username']} - возраст: {int(data['age'])}'

print(greet_user(user_data))

# -------------------------------------------------------------------------------------------------------------

# Введение в библиотеку Pydantic

# Задание № 3 - познакомиться с классом BaseModel и на его основе создать модель User

# BaseModel - базовый класс, от которого нужно наследоваться, чтобы создать свою Pydantic-модель
from pydantic import BaseModel

# создаем класс User, наследник класса BaseModel
class User(BaseModel):
    # указываем аннотации атрибутов
    username: str
    email: str
    age: int

# создаем экземпляр класса User, при этом Pydantic проверяет переданные значения на соответствие типам (str, str, int)
user = User(username='Дима', email='dima12348@mail.ru', age=27)
print(user.username)        # Дима

# Задание № 4 - познакомиться с методами для преобразования модели в словарь и JSON

# model_dump() - метод для преобразования указанной модели в словарь
print(user.model_dump())        # {'username': 'Дима', 'email': 'dima12348@mail.ru', 'age': 27}
# model_dump_json() - метод для преобразования указанной модели в JSON
print(user.model_dump_json())   # {"username":"Дима","email":"dima12348@mail.ru","age":27}

# Задание № 5 - посмотреть на автоматическое приведение типов и пример ошибки валидации

# Pydantic попробует автоматически привести тип age к int, если это возможно
user_1 = User(username='Дима', email='dima12348@mail.ru', age='27')
print(user_1.age, type(user_1.age))     # 27 <class 'int'>

# если возникает ошибка при валидации данных, Pydantic вызовет ValidationError с подробным описанием
user_2 = User(username='Дима', email='dima12348@mail.ru', age='абв')

# -------------------------------------------------------------------------------------------------------------

# Дополнительные возможности Pydantic

# Задание № 6 - модифицировать поля модели User с помощью функции Field()

from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., min_length=2, max_length=30, description='Имя пользователя от 2 до 30 символов')
    age: int = Field(..., ge=14, le=120, description='Возраст от 14 до 120 лет')
    email: str = Field(..., description='Электронная почта')

user_with_fields = User(username='Дима', email='dima12348@mail.ru', age=27)     # OK
user_with_fields = User(username='Дима', email='dima12348@mail.ru')             # Field required
user_with_fields = User(username='Д', email='dima12348@mail.ru', age=27)        # String should have at least 2 characters
user_with_fields = User(username='Дима', email='dima12348@mail.ru', age=127)    # Input should be less than or equal to 120

# Задание № 7 - добавить в модель User валидацию email через EmailStr

from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., min_length=2, max_length=30, description='Имя пользователя от 2 до 30 символов')
    age: int = Field(..., ge=14, le=120, description='Возраст от 14 до 120 лет')
    email: EmailStr = Field(..., description='Электронная почта')

user_with_email = User(username='Дима', email='dima12348@mail.ru', age=27)     # OK
print(user_with_email.email)   # dima12348@mail.ru

user_with_email = User(username='Дима', email='dima12348@mail', age=27)        # value is not a valid email address

# Задание № 8 - добавить в модель User пользовательскую валидацию с помощью @field_validator

from pydantic import BaseModel, Field, EmailStr, field_validator

class User(BaseModel):
    username: str = Field(..., min_length=2, max_length=30, description='Имя пользователя от 2 до 30 символов')
    age: int = Field(..., ge=14, le=120, description='Возраст от 14 до 120 лет')
    email: EmailStr = Field(..., description='Электронная почта')

    # валидируем поле username
    @field_validator('username')
    # создаем классовый метод, поэтому вместо self указываем cls
    def username_no_spaces(cls, value):
        if ' ' in value:
            raise ValueError('Имя пользователя не должно содержать пробелы')
        return value

user = User(username='Дима', email='dima12348@mail.ru', age=27)     # ОК
user = User(username='Ди ма', email='dima12348@mail.ru', age=27)    # Value error, Имя пользователя не должно содержать пробелы

# -------------------------------------------------------------------------------------------------------------

# Интеграция Pydantic с FastAPI

# Задание № 9
'''
Создадим FastAPI-приложение, которое принимает JSON с информацией о пользователе, 
валидирует его через Pydantic-модель User, сохраняет результат в оперативной памяти (в словарь) 
и возвращает структурированный ответ.

Внутри приложения необходимо реализовать следующую Pydantic-модель User со следующими полями:
- username
- age
- email
- bio - информация о пользователе (опционально)

Также внутри приложения должны быть 3 эндпоинта:
1) POST /users/
Создание пользователя и сохранение его в словарь

2) GET /users/{user_id}
Получение информации о пользователе по ID

3) GET /users/
Получение списка с информацией о всех пользователях
'''

# импортируем класс FastAPI для создания объекта приложения и HTTPException для обработки HTTP-ошибок
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr, field_validator
# импортируем Optional для создания необязательного поля в User("о себе"), Dict для создания словаря
from typing import Optional, Dict

class User(BaseModel):
    username: str = Field(..., min_length=2, max_length=30, description='Имя пользователя от 2 до 30 символов')
    age: int = Field(..., ge=14, le=120, description='Возраст от 14 до 120 лет')
    email: EmailStr = Field(..., description='Электронная почта')
    bio: Optional[str] = None   # Поле "о себе" (например, "Изучаю Python")

    @field_validator('username')
    def username_no_spaces(cls, value):
        if ' ' in value:
            raise ValueError('Имя пользователя не должно содержать пробелы')
        return value

app = FastAPI()

# "База данных" в виде словаря для хранения пользователей
users: Dict[int, User] = {}
# ID пользователя
next_id: int = 1

# эндпоинт для обработки POST-запроса на создание пользователя и сохранения в словарь
@app.post('/users/')
async def create_user(user: User):
    global next_id
    user_id = next_id
    users[user_id] = user
    next_id += 1
    return {
        'message': f'Пользователь {user.username} создан',
        'id': user_id,
        'data': user.model_dump()
    }

# эндпоинт для обработки GET-запроса на получение информации об одном пользователе по ID
@app.get('/users/{user_id}')
async def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return {
        'id': user_id, 
        'data': users[user_id].model_dump()
    }

# эндпоинт для обработки GET-запроса на получение списка всех пользователей
@app.get('/users/')
async def get_users_list():
    return [
        {'id': id, 'data': user.model_dump()}
        for id, user in users.items()
    ]