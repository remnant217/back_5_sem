from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from auth_app.database import get_user
from datetime import datetime, timedelta, timezone
import jwt

SECRET_KEY = 'efb4d3b0a105afe7b78056264735b37596c40d0840f42c5bb3a4789d3e4662cf'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,      
        key=SECRET_KEY,         
        algorithm=ALGORITHM    
    )
    return encoded_jwt