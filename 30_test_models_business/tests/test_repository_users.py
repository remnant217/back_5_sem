import pytest

# подключаем необходимые для тестирования функции и модели
from app.repositories.users import (
    create_user,
    update_user,
    authenticate,
)
from app.models.users import UserCreate, UserUpdate

# тестируем, что пользователь корректно создается в БД
@pytest.mark.asyncio
async def test_create_user(session):
    # подготовливаем данные
    user_data = UserCreate(username='Dima', password='Dima1234')
    # вызываем бизнес-логику
    user = await create_user(session=session, user_create=user_data)
    # проверяем результаты
    assert user.id is not None
    assert user.username == 'Dima'
    # пароль в базе не должен совпадать с открытым паролем
    assert user.hashed_password != 'Dima1234'
    assert user.is_active == True
    assert user.is_superuser == False

# тестируем успешную аутентификацию
@pytest.mark.asyncio
async def test_authenticate_user_success(session):
    # создаем пользователя
    user_data = UserCreate(username='Maks', password='Maks6789')
    await create_user(session=session, user_create=user_data)
    # проверяем аутентификацию
    user = await authenticate(session=session, username='Maks', password='Maks6789')
    assert user is not None
    assert user.username == 'Maks'

# тестируем возвращение None при неверном вводе пароле
@pytest.mark.asyncio
async def test_authenticate_wrong_password(session):
    user_data = UserCreate(username='Misha', password='Misha2007')
    await create_user(session=session, user_create=user_data)
    # проверяем аутентификацию
    user = await authenticate(session=session, username='Misha', password='Misha7002')
    assert user is None  

# тестируем обновление данных - меняем full_name, остальные поля не должны меняться
@pytest.mark.asyncio
async def test_update_user_full_name(session):
    user_data = UserCreate(username='Mike', password='Mike2016', full_name='Mike Wheeler')
    user = await create_user(session=session, user_create=user_data)
    update = UserUpdate(full_name='Michael Wheeler')
    updated_user = await update_user(session=session, user_db=user, user_update=update)
    assert updated_user.full_name == 'Michael Wheeler'
    assert updated_user.username == 'Mike'
    assert updated_user.is_active == True
    assert updated_user.is_superuser == False