from fastapi import FastAPI
from database import Base, engine
from routers import products

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'API каталога товаров готов к работе'}

app.include_router(products.router)