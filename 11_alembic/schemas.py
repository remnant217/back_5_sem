from pydantic import BaseModel, Field

# схема для создания нового товара
class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(gt=0)
    in_stock: bool = True

# схема для возврата ответа клиенту
class ProductOut(ProductCreate):
    id: int
    # Сonfig - специальный вложенный класс для настроек Pydantic-модели
    class Config:
        # позволяет возвращать ORM-объекты как JSON
        orm_mode = True 

# схема для частичного обновления
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    in_stock: bool | None = None