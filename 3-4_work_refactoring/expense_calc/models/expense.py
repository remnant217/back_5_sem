# класс для описания структуры траты
class Expense:
    # инициализатор класса с описание суммы и категории траты
    def __init__(self, amount: float, category: str):
        self.amount = amount
        self.category = category
    
    # строковое представление траты для удобного вывода в терминал  
    def __str__(self):
        return f'{self.amount} руб - {self.category}'

    # преобразование объекта траты в строку для записи в файл
    def to_line (self) -> str:
        return f'{self.amount}||{self.category}'
    
    # преобразование строки из файла в объект класса Expense
    @staticmethod
    def from_line(line: str) -> 'Expense':
        amount_str, category = line.strip().split('||')
        return Expense(float(amount_str), category)