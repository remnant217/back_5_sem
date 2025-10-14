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