# подключаем класс Expense и функции save_expenses(), load_expenses()
from models.expense import Expense
from storage.file_storage import save_expenses, load_expenses

# функция для тестирования сохранения в файл и загрузки из файла
def test_save_and_load():
    # создаем тестовые данные и проверяем функции save_expenses(), load_expenses()
    expenses = [
        Expense(100, 'Развлечения'),
        Expense(50, 'Другое')
    ]

    save_expenses(expenses)
    loaded = load_expenses()

    # если количество сохраненных и загруженных элементов не совпало - тест не пройден
    if len(loaded) != len(expenses):
        print('test_save_and_load: FAILED')
        print(f'Элементов сохранено: {len(expenses)}, загружено: {len(loaded)}')
    # иначе - тест пройден
    else:
        print('test_save_and_load: PASSED')

# запускаем тест
if __name__ == '__main__':
    test_save_and_load()