from pydantic import BaseModel

# модель токена доступа
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

# модель содержимого JWT-токена 
class TokenData(BaseModel):
    sub: str | None = None