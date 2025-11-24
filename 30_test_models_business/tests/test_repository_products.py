import pytest

# подключаем необходимые для тестирования функции и модели
from app.repositories.products import(
    create_product,
    update_product,
    get_product_by_id
)
from app.models.products import ProductCreate, ProductUpdate

# тестируем создание продукта
@pytest.mark.asyncio
async def test_create_product(session):
    product_data = ProductCreate(name='Ноутбук', price=55000)
    product = await create_product(session=session, product_create=product_data)
    assert product.id is not None
    assert product.name == 'Ноутбук'
    assert product.price == 55000
    assert product.in_stock is True

# тестируем обновление продукта
@pytest.mark.asyncio
async def test_update_product_price(session):
    product_data = ProductCreate(name='Телефон', price=45000)
    product = await create_product(session=session, product_create=product_data)
    update = ProductUpdate(price=50000)
    updated_product = await update_product(session=session, product_db=product, product_update=update)
    assert updated_product.price == 50000
    assert updated_product.name == 'Телефон'

# тестируем получение None при попытке получить несуществующий продукт
@pytest.mark.asyncio
async def test_get_product_by_id_not_found(session):
    product = await get_product_by_id(session, product_id=999)
    assert product is None