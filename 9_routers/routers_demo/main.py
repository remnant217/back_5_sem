from fastapi import FastAPI
# подключаем модуль с роутером
from routers import products

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'API работает'}

# include_router() - метод для подключения роутера
app.include_router(products.router)