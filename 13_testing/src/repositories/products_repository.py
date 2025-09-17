# подключаем класс AsyncSession для работы с асинхронной сессией
from sqlalchemy.ext.asyncio import AsyncSession
# select() - функция для конструирования SQL-запроса на чтение данных, работает в асинхронных сессиях, замена query()
from sqlalchemy import select
from src.models import Product
from src.schemas import ProductCreate, ProductUpdate

# создать новый товар
async def create_product(session: AsyncSession, product_data: ProductCreate) -> Product:
    new_product = Product(**product_data.model_dump())
    session.add(new_product)
    await session.commit()
    return new_product

# получение списка товаров с фильтрацией
async def get_products_list(
    session: AsyncSession,
    q: str = None,
    in_stock: bool = None,
    min_price: float = None,
    max_price: float = None
) -> list[Product]:

    # меняем query() на select(), result на query для дальнейшего удобства и логики
    query = select(Product)

    # проверка фильтров наличия, макс. и мин. цены
    if in_stock is not None:
        # здесь и далее - меняем filter() на where()
        query = query.where(Product.in_stock == in_stock)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    
    # отправляем запрос в БД и получаем объект класса Result
    result = await session.execute(query)
    # превращаем объект Result в список объектов Product
    products = result.scalars().all()
    
    if q:
        low_q = q.lower()
        products = [p for p in products if low_q in p.name.lower()]
    
    return products

# получение товара по ID
async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

# полное обновление товара
async def put_product(session: AsyncSession, product: Product, product_data: ProductCreate) -> Product:
    for field, value in product_data.model_dump().items():
        setattr(product, field, value)
    await session.commit()
    return product

# частичное обновление товара
async def patch_product(session: AsyncSession, product: Product, product_data: ProductUpdate) -> Product:
    updates = product_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)
    await session.commit()
    return product

# удаление товара
async def delete_product(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.commit()