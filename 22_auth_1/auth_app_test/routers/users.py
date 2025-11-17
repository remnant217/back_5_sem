from fastapi import APIRouter, Depends

from auth_app_test.deps import get_current_active_user
from auth_app_test.security import oauth2_scheme
from auth_app_test.models import User

router = APIRouter(tags=['users'])

@router.get('/users/profile')
async def get_users_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get('/items')
async def get_items(token: str = Depends(oauth2_scheme)):
    return {'token': token}