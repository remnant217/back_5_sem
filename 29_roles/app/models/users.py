from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field
from app.models import Base

# модель таблицы "Пользователи"
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    full_name = Column(String(128), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # добавляем поле-флаг для суперпользователя
    is_superuser = Column(Boolean, default=False, nullable=False)

# обновленная базовая модель пользователя
class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    is_active: bool = True
    # добавляем поле-флаг для суперпользователя
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=128)

# новая модель пользователя при регистрации:
# 1) наследуемся от BaseModel, чтобы не перетаскивать is_superuser из UserBase, иначе простой пользователь 
# сам сможет сделать себя суперпользователем
# 2) модель UserCreate тоже будет, но только для использования суперпользователем
class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    full_name: str | None = Field(default=None, max_length=128)
    password: str = Field(min_length=8, max_length=64)

# модель для создания нового пользователя (только для админа)
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)

# модель пользователя при обновлении
class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=64)
    password: str | None = Field(default=None, min_length=8, max_length=64)
    full_name: str | None = Field(default=None, max_length=128)

# модель пользователя при его возвращении по API
class UserOut(UserBase):
    id: int
    model_config = {'from_attributes': True}