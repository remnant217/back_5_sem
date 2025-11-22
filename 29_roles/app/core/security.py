from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

SECRET_KEY = 'a1e1abda8dd3079c07cd9a0f7b7e348476ee1b2c16dbe44d1653bd342f17f287'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

# вычислить хэш для пароля
def get_password_hash(password):
    return password_hash.hash(password)

# сравнить пароль с предполагаемым хэшем
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

# создать JWT-токен
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