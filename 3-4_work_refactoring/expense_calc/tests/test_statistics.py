# подключаем класс Expense и функцию get_total()
from logic.statistics import get_total
from models.expense import Expense

# функция для тестирования подсчета общей суммы по нескольким тратам
def test_get_total():
    # создаем тестовые данные и проверяем функцию get_total()
    expenses = [Expense(100, "Еда"), Expense(50, "Транспорт")]
    expected = 150
    actual = get_total(expenses)

    # если ожидаемая и рассчитанная суммы совпали - тест пройден
    if expected == actual:
        print('test_get_total: PASSED')
    # иначе - тест не пройден, выводим пояснение
    else:
        print('test_get_total: FAILED')
        print(f'Ожидалось значение суммы {expected}, получено {actual}')

# запускаем тест
if __name__ == '__main__':
    test_get_total()