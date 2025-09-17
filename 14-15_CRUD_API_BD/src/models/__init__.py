from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from .movie import Movie

__all__ = ['Base', 'Movie']