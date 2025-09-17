# подключаем класс Expense для оформления аннотации типов
from models.expense import Expense

# функция для ввода информации о трате через терминал, возвращает кортеж с дробным число и строкой
def input_expense() -> tuple[float, str]:
    # запрашиваем сумму траты, пока не получим корректное значение
    while True:
        # проверяем, что введено неотрицательное число
        try:
            amount = float(input('Введите сумму:'))
            if amount < 0:
                raise ValueError('Сумма траты не должна быть отрицательной')
            break
        # показываем ошибку при некорректном вводе
        except ValueError as err:
            print(f'Ошибка: {err}')

    # запрашиваем категорию траты
    category = input('Введите категорию:')
    # возвращаем кортеж с суммой и категорией траты
    return amount, category

# функция для отображения данных о тратах в терминале
def print_expenses(expenses: list[Expense]):
    # если данные о тратах еще не выгружены в программу
    if not expenses:
        print('Нет данных для отображения')
        return
    
    # построчный вывод трат в терминал с разделением для удобства восприятия
    print('Список трат:')
    print('-' * 30)
    # нумерацию начинаем с 1 для удобства пользователя
    for ind, exp in enumerate(expenses, start=1):
        print(f'{ind}. {exp.amount} руб. - {exp.category}')
    print('-' * 30)