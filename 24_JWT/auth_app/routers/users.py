from fastapi import APIRouter, Depends
from auth_app.security import oauth2_scheme
from auth_app.deps import get_current_active_user
from auth_app.models import User

router = APIRouter(tags=['users'])

@router.get('/users/profile', response_model=User)
async def get_users_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get('/items')
async def get_items(current_user: User = Depends(get_current_active_user)):
    return [{'item_id': '4815162342', 'owner': current_user.username}]