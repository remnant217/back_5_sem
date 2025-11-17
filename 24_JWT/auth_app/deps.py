import jwt
from fastapi import HTTPException, Depends
from jwt.exceptions import InvalidTokenError
from auth_app.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from auth_app.database import get_user, users_db
from auth_app.models import User, TokenData

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db=users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=403, 
            detail='Пользователь не активен'
        )
    return current_user