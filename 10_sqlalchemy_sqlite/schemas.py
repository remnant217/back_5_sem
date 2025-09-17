from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

    class Config:
        orm_mode = True 