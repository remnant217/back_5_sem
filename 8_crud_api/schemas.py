from pydantic import BaseModel, Field

# схема для создания товара
class ProductCreate(BaseModel):
    # обязательное поле длиной от 1 до 200 символов
    name: str = Field(min_length=1, max_length=200)
    # необязательное поле, может быть строкой или объектом None
    description: str | None = None
    # обязательное поле, цена должна быть > 0
    price: float = Field(gt=0)
    # необязательное поле, по умолчанию True (если клиент не прислал - считаем, что товар "в наличии")
    in_stock: bool = True

# схема ответа (что возвращаем клиенту), наследуемся от ProductCreate
class Product(ProductCreate):
    # ID добавляем только в ответ клиенту (генерируется на стороне БД)
    id: int

# схема для обновления данных о товаре
class ProductUpdate(BaseModel):
    # все поля опциональны - клиент может прислать только то, что хочет изменить
    # если поле не прислано вовсе - оно считается 'unset', важно для будущего эндпоинта
    # default=None - поле может быть передано как null
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    # значение по умолчанию делаем None, а не True, чтобы при PATCH-запросе, если клиент
    # не прислал in_stock, оно не считалось присланным как True, что может привести к путанице
    in_stock: bool | None = None