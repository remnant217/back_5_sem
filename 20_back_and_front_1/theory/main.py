from fastapi import FastAPI
# StaticFiles - класс для работы со статическими файлами
from fastapi.staticfiles import StaticFiles
# подключаем роутер из файла routers/products.py
from products import router

app = FastAPI()

# mount() - метод, позволяющий "вмонтировать под-приложение" в основное FastAPI-приложение
# добавляем папку со статическими файлами под именем static
app.mount(
    path='/static',
    app=StaticFiles(directory='./static'),
    name='static'
)

# подключаем роутер
app.include_router(router=router)