from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Movie
from src.schemas.movie import MovieCreate, MovieUpdate

# создаем словарь с разрешенными сортировками
ALLOWED_ORDERS = {
    'title': Movie.title.asc(),
    '-title': Movie.title.desc(),
    'year': Movie.year.asc(),
    '-year': Movie.year.desc(),
    'rating': Movie.rating.asc(),
    '-rating': Movie.rating.desc(),
    'id': Movie.id.asc(),
    '-id': Movie.id.desc()
}

# функция для создания фильма
async def create_movie(session: AsyncSession, data: MovieCreate) -> Movie:
    new_movie = Movie(**data.model_dump())
    session.add(new_movie)
    await session.commit()
    return new_movie

# функция для получения одного фильма по ID
async def get_movie(session: AsyncSession, movie_id: int) -> Movie | None:
    return await session.get(Movie, movie_id)

# функция для получения списка фильмов
async def get_list_movies(
    session: AsyncSession,
    year_min: int | None = None,        
    year_max: int | None = None,        
    min_rating: float | None = None,    
    order_by: str | None = '-rating',   
    limit: int = 50, 
    offset: int = 0,
) -> list[Movie]:
    
    query = select(Movie)
    
    if year_min is not None:
        query = query.where(Movie.year >= year_min)
    if year_max is not None:
        query = query.where(Movie.year <= year_max)
    if min_rating is not None:
        query = query.where(Movie.rating >= min_rating)
    
    key = order_by or '-rating'
    primary_order = ALLOWED_ORDERS.get(key, Movie.rating.desc())
    query = query.order_by(primary_order, Movie.id.asc())

    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())

# полное обновление фильма
async def put_movie(session: AsyncSession, movie_id: int, movie_data: MovieCreate) -> Movie | None:
    movie = await session.get(Movie, movie_id)
    if not movie:
        return None
    for field, value in movie_data.model_dump().items():
        setattr(movie, field, value)
    await session.commit()
    return movie

# частичное обновление фильма
async def patch_movie(session: AsyncSession, movie_id: int, movie_data: MovieUpdate) -> Movie | None:
    movie = await session.get(Movie, movie_id)
    if not movie:
        return None
    for field, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)
    await session.commit()
    return movie

# функция для удаления фильма по ID
async def delete_movie(session: AsyncSession, movie_id: int) -> bool:
    movie_to_delete = await session.get(Movie, movie_id)
    if not movie_to_delete:
        return False
    await session.delete(movie_to_delete)
    await session.commit()
    return True