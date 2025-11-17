from sqlalchemy import Column, Integer, String, Float, Boolean
from pydantic import BaseModel, Field
from . import Base

# модель таблицы "Продукты"
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)

# базовая модель продукта
class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    price: float = Field(ge=0)
    in_stock: bool = True

# модель продукта при его создании
class ProductCreate(ProductBase):
    pass

# модель продукта при его обновлении
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=128)
    price: float | None = Field(default=None, ge=0)
    in_stock: bool | None = None

# модель продукта при его возвращении по API
class ProductOut(ProductBase):
    id: int
    model_config = {'from_attributes': True}