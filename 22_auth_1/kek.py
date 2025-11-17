from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

@app.get('/items')
async def get_items(token: str = Depends(oauth2_scheme)):
    return {'token': token}