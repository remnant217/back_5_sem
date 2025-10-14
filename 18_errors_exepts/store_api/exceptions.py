# класс исключения для обработки ситуации "Недостаточно товара на складе"
class OutOfStockError(Exception):
    def __init__(self, item_id, item_name: str, requested: int, available: int):
        self.item_id = item_id          # ID товара
        self.item_name = item_name      # название товара        
        self.requested = requested      # сколько товара нужно клиенту
        self.available = available      # сколько товара есть на складе