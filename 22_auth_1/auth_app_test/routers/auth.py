from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from auth_app_test.security import hash_password
from auth_app_test.database import users_db
from auth_app_test.models import UserInDB

router = APIRouter(tags=['auth'])

@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400,
            detail='Неверный логин или пароль'
        )
    user = UserInDB(**user_dict)
    hashed_password = hash_password(form_data.password)
    if hashed_password != user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail='Неверный логин или пароль'
        )
    
    return {'access_token': user.username, 'token_type': 'bearer'}