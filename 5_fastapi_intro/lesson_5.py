# Введение в FastAPI

# Установка и первый запуск FastAPI

# Задание № 2 - создать и активировать виртуальное окружение venv
'''
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\scripts\activate     # Windows
'''

# Задание № 2 - установить библиотеки fastapi и uvicorn
'''
pip install fastapi uvicorn
'''

# Задание № 2 - сохранить зависимости проекта
'''
pip freeze > requirements.txt
'''

# Задание № 3 - создать первое FastAPI-приложение

# импортируем класс FastAPI
from fastapi import FastAPI

# создаем объект приложения
app = FastAPI()

# указываем маршрут для корневой папки и функцию для возвращения сообщения
@app.get('/')
def root():
    return {'message': 'Hello, FastAPI!'}

# Задание № 3 - запустить приложение за сервере uvicorn
'''
uvicorn main:app --reload
'''

# Задание № 4 - добавить и протестировать новый эндпоинт

# импортируем класс FastAPI
from fastapi import FastAPI

# создаем объект приложения
app = FastAPI()

# указываем маршрут для корневой папки и функцию для возвращения сообщения
@app.get('/')
def root():
    return {'message': 'Hello, FastAPI!'}

# получение данных объекта по указанному ID
@app.get('/items/{item_id}')
def get_item(item_id: int):
    return {'item_id': item_id}

# -------------------------------------------------------------------------------------------------------------

# Асинхронное программирование в FastAPI

# Задание № 5 - добавить async в функции имеющегося приложения

# импортируем класс FastAPI
from fastapi import FastAPI

# создаем объект приложения
app = FastAPI()

# указываем маршрут для корневой папки и функцию для возвращения сообщения
@app.get('/')
async def root():
    return {'message': 'Hello, FastAPI!'}

# получение данных объекта по указанному ID
@app.get('/items/{item_id}')
async def get_item(item_id: int):
    return {'item_id': item_id}

# -------------------------------------------------------------------------------------------------------------

# Практическое задание

# Задание № 6 - выполнить практическое задание на создание FastAPI-приложения с 3 эндпоинтами
'''
Необходимо создать FastAPI-приложение с 3 эндпоинтами:
1) GET /
Возвращает приветственное сообщение
Пример ответа:
{"message": "Добро пожаловать в мое FastAPI-приложение!"}

2) GET /user/{username}
Принимает имя пользователя (строка) и возвращает приветствие для указанного имени
Пример входных параметров:
Миша
Пример ответа:
{"username": "Миша", "message": "Привет, Миша!"}

3) GET /profile/{username}
Принимает имя пользователя (строка) и возвращает профиль пользователя со следующей информацией:
- ID (генерируется случайно от 1 до 999)
- username
- age (генерируется случайно от 18 до 99)
- role (генерируется случайно между 'user' и 'admin')
Пример входных параметров:
Дима
Пример ответа:
{
  "id": 156,
  "username": "Дима",
  "age": 27,
  "role": admin
}

Код выполненного задания выглядит следующим образом:
'''
# импортируем класс FastAPI
from fastapi import FastAPI
# импортируем функции для генерации случайных чисел и случайного выбора
from random import randint, choice

# создаем объект приложения 
app = FastAPI()

# приветствие в приложении
@app.get('/')
async def root():
    return {'message': 'Добро пожаловать в мое FastAPI-приложение!'}

# приветствие пользователя по имени
@app.get('/user/{username}')
async def greet_user(username: str):
    return {'username': username, 'message': f'Привет, {username}!'}

# отправка данных профиля пользователя
@app.get('/profile/{username}')
async def get_profile(username: str):
    user_id = randint(1, 999)
    age = randint(18, 99)
    role = choice(['user', 'admin'])
    return {
        'id': user_id,
        'username': username,
        'age': age,
        'role': role
    }