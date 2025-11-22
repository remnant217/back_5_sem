from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# асинхронное подключение для работы с API
DATABASE_ASYNC = 'sqlite+aiosqlite:///./products.db'
# синхронное подключение для работы с alembic
DATABASE_SYNC = 'sqlite:///./products.db'

# асинхронный движок для работы с БД
engine = create_async_engine(url=DATABASE_ASYNC, echo=False)
# фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)