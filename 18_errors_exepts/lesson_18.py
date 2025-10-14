# Обработка ошибок и исключений в FastAPI

# Введение в работу с ошибками в FastAPI

# Задание № 1 - посмотреть на пример "плохого" API

from fastapi import FastAPI

app = FastAPI()

# псевдо-БД с данными пользователей
users = {
    1: {'name': 'Дима', 'age': 25},
    2: {'name': 'Максим', 'age': 24}
}

# получение информации о пользователе по ID
@app.get('/users/{user_id}')
async def get_user(user_id: int):
    return users[user_id]

# обновление всей информации о пользователе по ID
@app.put('/users/{user_id}')
async def put_user(user_id: int, new_name: str, new_age: int):
    users[user_id] = {'name': new_name, 'age': new_age}
    return users[user_id]

# -----------------------------------------------------------------------------------------------------------------

# Исключения и HTTP-ошибки

# Задание № 2 - добавить в эндпоинт get_user() проверку на отсутствие пользователя

from fastapi import HTTPException

@app.get('/users/{user_id}')
async def get_user(user_id: int):
    # если ID не найден - возвращаем статус 404 с пояснением
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return users[user_id]

# Задание № 3 - добавить в эндпоинт put_user() обработку несуществующего пользователя и проверку длины имени

@app.put('/users/{user_id}')
async def put_user(user_id: int, new_name: str, new_age: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    
    # если имя слишком короткое (без учета пробельных символов) - возвращаем статус 422 с пояснением
    if len(new_name.strip()) < 2:
        raise HTTPException(status_code=422, detail='Имя слишком короткое, должно быть минимум 2 символа')

    # обновляем имя без учета пробельных символов
    users[user_id] = {'name': new_name.strip(), 'age': new_age}
    return users[user_id]

# Задание № 4 - создать модель UserUpdate и внедрить ее в эндпоинт put_user()

from pydantic import BaseModel, Field

# модель для обновления данных пользователя
class UserUpdate(BaseModel):
    # обязательное строковое поле, минимальная длина 2
    name: str = Field(min_length=2)
    # обязательно целочисленное поле, значение не менее 1
    age: int = Field(ge=1)

# обновляем эндпоинт, внедряя модель UserUpdate
@app.put('/users/{user_id}')
async def put_user(user_id: int, data: UserUpdate):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    
    # обращаемся к данным из объекта модели UserUpdate
    users[user_id] = {'name': data.name, 'age': data.age}
    return users[user_id]

# -----------------------------------------------------------------------------------------------------------------

# Создание собственных исключений

# Задание № 5 - добавить в словарь users поле balance

users = {
    1: {'name': 'Дима', 'age': 25, 'balance': 1000},
    2: {'name': 'Максим', 'age': 24, 'balance': 400}
}

# Задание № 6 - создать класс NotEnoughFundsError

# класс исключения для обработки ситуации "Недостаточно средств на счете"
class NotEnoughFundsError(Exception):
    def __init__(self, balance: int, withdraw: int):
        self.balance = balance
        self.withdraw = withdraw

# Задание № 7 - создать обработчик исключения NotEnoughFundsError через декоратор @app.exception_handler()

# класс для автоматической сериализации данных в JSON и возвращения ответа в виде application/json
from fastapi.responses import JSONResponse
from fastapi import Request

# создаем обработчик исключения NotEnoughFundsError
@app.exception_handler(NotEnoughFundsError)
async def not_enough_funds_handler(request: Request, exc: NotEnoughFundsError):
    # возвращаем статус 409, т.к. запрос невозможно выполнить из-за текущего состояния баланса
    return JSONResponse(
        status_code=409,
        content={
            'error': 'not_enough_funds',
            'balance': exc.balance,
            'requested': exc.withdraw,
            'message': f'Невозможно снять {exc.withdraw}, доступно только {exc.balance}'
        }
    )

# Задание № 8 - создать эндпоинт withdraw_money()

# обработка запроса на снятие денег со счета пользователя
@app.post('/users/{user_id}/withdraw')
async def withdraw_money(user_id: int, amount: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    
    user = users[user_id]
    # если на балансе недостаточно средств для снятия указанной суммы
    if amount > user['balance']:
        raise NotEnoughFundsError(balance=user['balance'], withdraw=amount)
    
    # уменьшаем значение баланса пользователя и возвращаем ответ клиенту
    user['balance'] -= amount
    return {'message': 'Снятие успешно', 'new_balance': user['balance']}