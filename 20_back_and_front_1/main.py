from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.products import router

app = FastAPI()

app.mount(
    path='/static',
    # указываем относительный путь до папки /static для корректной работы
    app=StaticFiles(directory='./static'),
    name='static'
)

app.include_router(router=router)