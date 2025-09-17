from schemas import Product

class DataStore:
    def __init__(self):
        self.products: dict[int, Product] = {}
        self.current_id: int = 1
    
    def next_id(self) -> int:
        value = self.current_id
        self.current_id += 1
        return value

store = DataStore()