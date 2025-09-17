# подключаем все инструменты из созданных слоев проекта
from models.expense import Expense
from logic.statistics import get_total
from storage.file_storage import save_expenses, load_expenses
from controller.cli import print_expenses, input_expense

# функция для запуска работы приложения в терминале
def run():
    # список для хранения трат
    expenses = []

    # цикл работы с пользователем
    while True:
        # отображение возможных команд для пользователя
        print('1. Добавить трату')
        print('2. Показать все')
        print('3. Показать сумму')
        print('4. Сохранить')
        print('5. Загрузить')
        print('6. Выйти')

        # ввод команды со стороны пользователя
        choice = input('Выбор: ')

        # ввод и сохранение информации о тратах
        if choice == '1':
            amount, category = input_expense()
            expenses.append(Expense(amount, category))
            print('Данные о трате сохранены!')

        # вывод на экран информации о всех тратах
        elif choice == '2':
            print_expenses(expenses)

        # подсчет и вывод на экран общей суммы всех трат
        elif choice == '3':
            total = get_total(expenses)
            print(f'Итого: {total} руб.')

        # сохранение данных о тратах в файл
        elif choice == '4':
            save_expenses(expenses)
            print('Данные сохранены в файл!')

         # выгрузка всех данных о тратах из файла
        elif choice == '5':
            expenses = load_expenses()
            print('Данные выгружены из файла!')

        # завершение работы
        elif choice == '6':
            break

        # обработка некорректной команды
        else:
            print('Некорректная команда. Попробуйте снова.')
