from fastapi import FastAPI
# подключаем роутер для работы с товарами
from routers import products

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

# подключаем роутер
app.include_router(products.router)