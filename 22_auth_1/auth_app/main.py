from fastapi import FastAPI
from auth_app.routers import users

app = FastAPI()

app.include_router(users.router)