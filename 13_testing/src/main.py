from fastapi import FastAPI
from .routers import products

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

app.include_router(products.router)