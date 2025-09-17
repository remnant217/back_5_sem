# подключаем класс Expense
from models.expense import Expense

# функция для тестирования преобразования объекта Expense в строку и обратно
def test_to_line_and_back():
    # создаем тестовые данные и проверяем методы to_line(), from_line()
    exp_origin = Expense(220, 'Еда')
    line = exp_origin.to_line()
    exp_result = Expense.from_line(line)

    # если значения amount и category исходного объекта равны значениям результата - тест пройден
    if exp_origin.amount == exp_result.amount and exp_origin.category == exp_result.category:
        print('test_to_line_and_back: PASSED')
    # иначе - тест не пройден, выводим пояснение
    else:
        print('test_to_line_and_back: FAILED')
        print(f'Ожидалось: amount={exp_origin.amount}, category={exp_origin.category}')
        print(f'Получено: amount={exp_result.amount}, category={exp_result.category}')

# запускаем тест
if __name__ == '__main__':
    test_to_line_and_back()