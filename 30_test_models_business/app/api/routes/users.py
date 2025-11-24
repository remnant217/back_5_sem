from fastapi import APIRouter, HTTPException, Depends

# импортируем новую зависимость, новую модель и новые функции для работы с пользователями в БД
from app.models.users import UserRegister, UserCreate, UserUpdate, UserOut
from app.api.deps import (
    SessionDep, 
    CurrentUserDep, 
    get_current_superuser
)
from app.repositories.users import (
    create_user as create_user_repo,
    update_user as update_user_repo,
    delete_user as delete_user_repo,
    get_user_by_username,
    get_user_by_id,
    get_users
)

router = APIRouter(prefix='/users', tags=['users'])

# получить текущего пользователя
@router.get('/me', response_model=UserOut)
async def get_user_me(current_user: CurrentUserDep):
    return current_user

# получить пользователя по username - модифицируем:
# - Если простой пользователь запрашивает информацию о себе - все окей
# - Если простой пользователь запрашивает информацию о другом пользователе - только для админа
@router.get('/{username}', response_model=UserOut)
async def get_user(session: SessionDep, username: str, current_user: CurrentUserDep):
    user = await get_user_by_username(session=session, username=username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )
    # если смотрим другого пользователя и текущий пользователь не админ
    if user.username != current_user.username and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='У пользователя недостаточно прав для данного действия'
        )
    return user

# новый эндпоинт - получить список всех пользователей (только для админа)
# указываем зависимость в параметре dependencies для проверки, что пользователь является админом
@router.get('/', response_model=list[UserOut], dependencies=[Depends(get_current_superuser)])
async def get_users_list(session: SessionDep, skip: int = 0, limit: int = 100):
    users = await get_users(session=session, skip=skip, limit=limit)
    return users

# новый эндпоинт - создать нового пользователя без предварительного входа в систему 
# (классическая регистрация)
@router.post('/signup', response_model=UserOut)
async def register_user(session: SessionDep, user_data: UserRegister):
    user = await get_user_by_username(session=session, username=user_data.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail='Пользователь с таким username уже существует в системе'
        )
    user_create = UserCreate(
        username=user_data.username,
        full_name=user_data.full_name,
        password=user_data.password
        # is_active и is_superuser возьмут значения по умолчанию
    )
    new_user = await create_user_repo(session=session, user_create=user_create)
    return new_user

# создать нового пользователя - модифицируем, чтобы работало только для админа
@router.post('/', response_model=UserOut, dependencies=[Depends(get_current_superuser)])
async def create_user(session: SessionDep, user_data: UserCreate):
    user = await get_user_by_username(session=session, username=user_data.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail='Пользователь с таким username уже существует в системе'
        )
    new_user = await create_user_repo(session=session, user_create=user_data)
    return new_user

# обновить данные пользователя по id - модифицируем:
# - Простой пользователь может обновить только свои данные
# - Админ может обновить данные любого пользователя
# - Для удобства использования поменяем put на patch
@router.patch('/{user_id}', response_model=UserOut)
async def update_user(session: SessionDep, user_id: int, user_data: UserUpdate, current_user: CurrentUserDep) -> UserOut:
    user_db = await get_user_by_id(session=session, user_id=user_id)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )
    # если обновляем другого пользователя и текущий пользователь не админ
    if user_db.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='У пользователя недостаточно прав для данного действия'
        )

    updated_user = await update_user_repo(
        session=session,
        user_db=user_db,
        user_update=user_data,
    )
    return updated_user

# новый эндпоинт - удалить пользователя по ID (только для админа)
@router.delete('/{user_id}', dependencies=[Depends(get_current_superuser)])
async def delete_user(session: SessionDep, current_user: CurrentUserDep, user_id: int):
    user_db = await get_user_by_id(session=session, user_id=user_id)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
    )
    # админ не может удалить сам себя
    if user_db.id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Администраторам нельзя удалять себя'
        )
    
    await delete_user_repo(session=session, user_db=user_db)
    return {'message': 'Пользователь успешно удален'}