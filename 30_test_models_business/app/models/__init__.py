from sqlalchemy.orm import DeclarativeBase

# базовый класс для создания ORM-моделей таблиц 
class Base(DeclarativeBase):
    pass

# импорты моделей для корректной работы Alembic
from app.models.products import Product
from app.models.users import User