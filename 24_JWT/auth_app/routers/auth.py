# обновим импорты
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException

from auth_app.security import ACCESS_TOKEN_EXPIRE_MINUTES
from auth_app.security import authenticate_user, create_access_token
from auth_app.database import users_db
from auth_app.models import Token

router = APIRouter(tags=['auth'])

@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(
        db=users_db,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Неверный логин или пароль',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type='bearer')