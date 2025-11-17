from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.users import UserCreate, UserUpdate, UserOut
from app.repositories.users import (
    create_user as create_user_repo,
    update_user as update_user_repo,
    get_user_by_username,
    get_user_by_id
)

router = APIRouter(prefix='/users', tags=['users'])

# получить пользователя по username
@router.get('/{username}', response_model=UserOut)
async def get_user(session: SessionDep, username: str):
    user = await get_user_by_username(session=session, username=username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )
    return user

# создать нового пользователя
@router.post('/', response_model=UserOut)
async def create_user(session: SessionDep, user_data: UserCreate):
    new_user = await create_user_repo(session=session, user_create=user_data)
    return new_user

# обновить данные пользователя по id
@router.put('/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user_data: UserUpdate, session: SessionDep) -> UserOut:
    user_db = await get_user_by_id(session=session, user_id=user_id)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )

    updated_user = await update_user_repo(
        session=session,
        user_db=user_db,
        user_update=user_data,
    )
    return updated_user