from pydantic import BaseModel, Field

# Pydantic-модель для обновления данных о товаре
class ItemUpdate(BaseModel):
    name: str = Field(min_length=2)
    count: int = Field(ge=1)