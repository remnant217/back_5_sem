# подключаем класс Session для указания типа объекта сессии 
from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate, ProductUpdate

# создать новый товар
def create_product(db: Session, product_data: ProductCreate) -> Product:
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    return new_product

# получение списка товаров с фильтрацией
def get_products_list(
    db: Session,
    q: str = None,
    in_stock: bool = None,
    min_price: float = None,
    max_price: float = None
) -> list[Product]:
    # получаем объект Query, который будем дополнять с каждым выполнением .filter(),
    # формируя под капотом оптимизированный SQL-запрос
    result = db.query(Product)

    # проверка фильтров наличия, макс. и мин. цены
    if in_stock is not None:
        result = result.filter(Product.in_stock == in_stock)
    if min_price is not None:
        result = result.filter(Product.price >= min_price)
    if max_price is not None:
        result = result.filter(Product.price <= max_price)
    
    result = result.all()
    '''
    Проверка фильтра q реализуется уже со списком 
    в силу ограничений SQLite на работу с регистром символов кириллицы.
    Ниже приведено не самое оптимальное решение, но в рамках обучения подойдет.
    '''
    # если передана непустая подстрока для поиска
    if q:
        # все приводим к нижнему регистру и формируем список с совпадениями
        low_q = q.lower()
        result = [p for p in result if low_q in p.name.lower()]
    
    return result

# получение товара по ID
def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()

# полное обновление товара
def put_product(db: Session, product: Product, product_data: ProductCreate) -> Product:
    # превращаем модель в словарь и перебираем все пары ключ-значение 
    for field, value in product_data.model_dump().items():
        # обновляем все атрибуты объекта product
        setattr(product, field, value)
    db.commit()
    return product

# частичное обновление товара
def patch_product(db: Session, product: Product, product_data: ProductUpdate) -> Product:
    updates = product_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)
    db.commit()
    return product

# удаление товара
def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()