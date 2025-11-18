from fastapi import FastAPI

from app.api.routes import login, products, users
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware

setup_logging()

app = FastAPI()

app.include_router(login.router)
app.include_router(products.router)
app.include_router(users.router)

setup_middleware(app)