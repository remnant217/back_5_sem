from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.movie import MovieCreate, MovieUpdate, MovieOut
from src.repositories import movies as repo

router = APIRouter(
    prefix='/movies',
    tags=['Movies']
)

# получаем список фильмов
@router.get('/', response_model=list[MovieOut])
async def get_movies_list(
    session: AsyncSession = Depends(get_session),
    limit: int = 50, 
    offset: int = 0
):
    return await repo.get_list_movies(session, limit, offset)

# получаем фильм по ID
@router.get('/{movie_id}', response_model=MovieOut)
async def get_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    movie = await repo.get_movie(session, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail='Фильм не найден')
    return movie

# создаем запись с новым фильмов в БД
@router.post('/', response_model=MovieOut)
async def create_movie(movie_data: MovieCreate, session: AsyncSession = Depends(get_session)):
    return await repo.create_movie(session, movie_data)

# удаляем фильм из БД
@router.delete('/{movie_id}')
async def delete_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    is_deleted = await repo.delete_movie(session, movie_id)
    if not is_deleted:
        raise HTTPException(status_code=404, detail='Фильм не найден')
    return {'message': 'Фильм удален'}