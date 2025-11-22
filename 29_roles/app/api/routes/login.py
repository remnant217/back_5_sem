from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token
from app.api.deps import SessionDep
from app.models.tokens import Token
from app.repositories.users import authenticate

router = APIRouter(tags=['login'])

# вход в систему и получение токена
@router.post("/login/access-token")
async def login_access_token(
    session: SessionDep, 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user = await authenticate(
        session=session,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        logger.warning(f'Неудачная попытка входа: username={form_data.username}')
        raise HTTPException(
            status_code=401,
            detail='Неверный логин или пароль',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    elif not user.is_active:
        logger.warning(f'Неактивный пользователь попытался войти в систему: username={user.username}')
        raise HTTPException(status_code=400, detail='Неактивный пользователь')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    logger.info(f'Пользователь успешно вошел в систему: username={user.username}')
    return Token(access_token=access_token, token_type='bearer')