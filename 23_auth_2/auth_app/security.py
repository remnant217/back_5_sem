from fastapi.security import OAuth2PasswordBearer
from auth_app.database import users_db, get_user
from auth_app.models import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def hash_password(password: str) -> str:
    return 'hashed' + password

def decode_token(token) -> UserInDB | None:
    user = get_user(users_db, token)
    return user