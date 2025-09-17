from schemas import Product, ProductCreate, ProductUpdate

class DataStore:
    # инициализация словаря с товарами и счетчика ID
    def __init__(self):
        self.products: dict[int, Product] = {}
        self.current_id: int = 1
    
    # метод для увеличения значения счетчика ID на 1
    def next_id(self) -> int:
        value = self.current_id
        self.current_id += 1
        return value

    # создание нового продукта
    def create_product(self, product_data: ProductCreate) -> Product:
        product = Product(id=self.next_id(), **product_data.model_dump())
        self.products[product.id] = product
        return product
    
    # получение списка товаров с фильтрацией
    def get_products_list(
        self,
        q: str = None,
        in_stock: bool = None,
        min_price: float = None,
        max_price: float = None
    ) -> list[Product]:
        
        result = list(self.products.values())

        if q is not None:
            q_low = q.lower()
            result = [p for p in result if q_low in p.name.lower()]
        
        if in_stock is not None:
            result = [p for p in result if p.in_stock == in_stock]
        
        if min_price is not None:
            result = [p for p in result if p.price >= min_price]
        
        if max_price is not None:
            result = [p for p in result if p.price <= max_price]

        return result
    
    # получение товара по ID
    def get_product(self, product_id: int) -> Product | None:
        return self.products.get(product_id)
    
    # полное обновление товара
    def put_product(self, product_id: int, product_data: ProductCreate) -> Product:
        updated = Product(id=product_id, **product_data.model_dump())
        self.products[product_id] = updated
        return updated
    
    # частичное обновление товара
    def patch_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        current = self.products[product_id]
        updates = product_data.model_dump(exclude_unset=True)
        product_data_updated = current.model_copy(update=updates)
        self.products[product_id] = product_data_updated
        return product_data_updated
    
    # удаление товара
    def delete_product(self, product_id: int) -> None:
        del self.products[product_id]

store = DataStore()