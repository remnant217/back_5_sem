from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///products.db', echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()       # создаем новую сессию
    try:
        yield db              # отдаем ее в эндпоинт
    finally:
        db.close()            # после завершения запроса закрываем соединение