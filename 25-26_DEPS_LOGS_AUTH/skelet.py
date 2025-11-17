# pip install fastapi uvicorn sqlalchemy alembic loguru pyjwt "pwdlib[argon2]"

'''
Важная деталь для SQLite: включить внешние ключи

Чтобы ON DELETE CASCADE действительно работал, в SQLite надо включать FK:
- в sync-движке: PRAGMA foreign_keys = ON;
- в async-движке: сделай это на старте приложения (в событии/стартап-хуке) или через event-слушатель к engine.sync_engine.
Пример для async-engine (один из способов — в старте приложения):

# при старте приложения
from sqlalchemy import text
from app.database import engine

async def on_startup():
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))

(Либо через @event.listens_for(engine.sync_engine, "connect").)
'''