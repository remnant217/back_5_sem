from fastapi.security import OAuth2PasswordBearer
from auth_app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def decode_token(token: str):
    return User(
        username=token + 'decoded',
        email='dima@mail.ru'
    )