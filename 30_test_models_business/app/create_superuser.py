# подключаем asyncio для асинхронного запуска кода
import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.users import User

# функция для создания суперпользователя (если их еще нет в БД)
async def create_superuser():
    async with AsyncSessionLocal() as session:
        # придумываем username и password для первого суперпользователя
        username = 'admin'
        password = 'admin123'
        # проверяем, есть такой суперпользователь в БД или нет
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        check_user = result.scalar_one_or_none()
        if check_user:
            print(f'Такой {username} уже существует')
            return
        # создаем суперпользователя и добавляем его в БД
        super_user = User(
            username=username,
            full_name = 'Администратор',
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True
        )
        session.add(super_user)
        await session.commit()
        print(f'Суперпользователь создан: {username}/{password}')

# создаем суперпользователя только при прямом запуске файла
if __name__ == '__main__':
    asyncio.run(create_superuser())