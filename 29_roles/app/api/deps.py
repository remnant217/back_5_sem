from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core.database import AsyncSessionLocal
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.tokens import TokenData
from app.models.users import User
from app.repositories.users import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login/access-token')

# функция-зависимость для генерации новой сессии
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# получаем текущего пользователя
async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code = 401,
        detail = 'Не удалось подтвердить учетные данные',
        headers = {'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        token_data = TokenData(**payload)
        if token_data.sub is None:
            raise credentials_exception
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    
    user = await get_user_by_username(session=session, username=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Неактивный пользователь')
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]