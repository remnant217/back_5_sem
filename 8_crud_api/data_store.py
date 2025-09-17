from schemas import Product

# класс для реализации хранилища товаров
class DataStore:
    def __init__(self):
        # инициализация словаря с товарами и счетчика ID
        self.products: dict[int, Product] = {}
        self.current_id: int = 1
    
    # метод для увеличения значения счетчика ID на 1
    def next_id(self) -> int:
        value = self.current_id
        self.current_id += 1
        return value

# создаем экземпляр DataStore
store = DataStore()