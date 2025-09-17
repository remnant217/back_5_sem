from sqlalchemy import Column, Integer, String, Float, CheckConstraint
from . import Base

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    year = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 10', name='check_show_rating_range'),
        CheckConstraint('year >= 1888', name='check_movie_year_ge_1888')
    )