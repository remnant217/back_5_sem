from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# подключение к in-memory SQLite для асинхронного движка
TEST_DATABASE_ASYNC = 'sqlite+aiosqlite:///:memory:'

# отдельный движок для тестов
test_engine = create_async_engine(url=TEST_DATABASE_ASYNC, echo=False, poolclass=StaticPool)

# фабрика асинхронных сессий для тестовой БД
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)
