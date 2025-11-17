from fastapi import Depends
from auth_app.security import oauth2_scheme, decode_token

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    return user