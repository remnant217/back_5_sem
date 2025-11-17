from fastapi import FastAPI
from auth_app_test.routers import auth, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)