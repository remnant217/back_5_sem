from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import Base

engine = create_async_engine('sqlite+aiosqlite:///./movies.db', echo=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# корутина для локального запуска движка, без Alembic
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)