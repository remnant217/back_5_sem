from fastapi import Depends, HTTPException
from auth_app.security import oauth2_scheme, decode_token
from auth_app.models import User

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Неверные данные аутентификации',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=403, 
            detail='Пользователь не активен'
        )
    return current_user