# подключаем класс Expense
from models.expense import Expense

# переменная для хранения имени файла
FILENAME = 'expenses.txt'

# функция для сохранения трат в файл, принимает список с объектами класса Expense
def save_expenses(expenses: list[Expense]):
    # открываем поток работы с файлом и записываем в него траты, каждую с новой строки
    with open(FILENAME, 'w', encoding='utf-8') as f:
        for exp in expenses:
            f.write(exp.to_line() + '\n')

# функция для загрузки трат из файла, возвращает список с объектами класса Expense
def load_expenses() -> list[Expense]:
    # список для загрузки данных
    expenses = []
    # пробуем открыть поток работы с файлом и сохранить данные в список
    try:
        with open(FILENAME, encoding='utf-8') as f:
            for line in f:
                expenses.append(Expense.from_line(line))
    # если файл не найден - вернем пустой список
    except FileNotFoundError:
        pass
    # возвращаем список с объектами класса Expense
    return expenses