from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

# псевдо-БД с данными пользователей
users = {
    1: {'name': 'Дима', 'age': 25, 'balance': 1000},
    2: {'name': 'Максим', 'age': 24, 'balance': 400}
}

# класс исключения для обработки ситуации "Недостаточно средств на счете"
class NotEnoughFundsError(Exception):
    def __init__(self, balance: int, withdraw: int):
        self.balance = balance
        self.withdraw = withdraw

# модель для обновления данных пользователя
class UserUpdate(BaseModel):
    name: str = Field(min_length=2)
    age: int = Field(ge=1)

# создаем обработчик исключения NotEnoughFundsError
@app.exception_handler(NotEnoughFundsError)
async def not_enough_funds_handler(request: Request, exc: NotEnoughFundsError):
    return JSONResponse(
        status_code=409,
        content={
            'error': 'not_enough_funds',
            'balance': exc.balance,
            'requested': exc.withdraw,
            'message': f'Невозможно снять {exc.withdraw}, доступно только {exc.balance}'
        }
    )

# получение информации о пользователе по ID
@app.get('/users/{user_id}')
async def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return users[user_id]

# обновление информации о пользователе по ID
@app.put('/users/{user_id}')
async def put_user(user_id: int, data: UserUpdate):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    
    users[user_id] = {'name': data.name, 'age': data.age}
    return users[user_id]

# обработка запроса на снятие денег со счета пользователя
@app.post('/users/{user_id}/withdraw')
async def withdraw_money(user_id: int, amount: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    
    user = users[user_id]
    if amount > user['balance']:
        raise NotEnoughFundsError(balance=user['balance'], withdraw=amount)
    
    user['balance'] -= amount
    return {'message': 'Снятие успешно', 'new_balance': user['balance']}