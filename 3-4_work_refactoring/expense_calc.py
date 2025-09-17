# список для хранения трат в виде словарей
expenses = []

# главный цикл, внутри которого собран весь код приложения
while True:
    # отображение возможных команд для пользователя
    print("1. Добавить трату")
    print("2. Показать все траты")
    print("3. Показать сумму")
    print("4. Сохранить в файл")
    print("5. Загрузить из файла")
    print("6. Выйти")

    # ввод команды со стороны пользователя
    choice = input("Выбор: ")

    # ввод и сохранение информации об одной трате
    if choice == "1":
        amount = float(input("Введите сумму: "))
        category = input("Введите категорию: ")
        expenses.append({"amount": amount, "category": category})

    # вывод на экран информации о всех тратах
    elif choice == "2":
        for e in expenses:
            print(f"{e['amount']} руб — {e['category']}")
    
    # подсчет и вывод на экран общей суммы всех трат
    elif choice == "3":
        total = sum(e["amount"] for e in expenses)
        print(f"Всего потрачено: {total} руб.")
    
    # сохранение данных о тратах в файл
    elif choice == "4":
        with open("expenses.txt", "w", encoding="utf-8") as f:
            for e in expenses:
                f.write(f"{e['amount']}|{e['category']}\n")
        print("Сохранено.")
    
    # выгрузка всех данных о тратах из файла
    elif choice == "5":
        expenses = []
        with open("expenses.txt", encoding="utf-8") as f:
            for line in f:
                amount, category = line.strip().split("|")
                expenses.append({"amount": float(amount), "category": category})
        print("Загружено.")
    
    # завершение работы 
    elif choice == "6":
        break

    # обработка некорректной команды
    else:
        print("Некорректная команда. Попробуйте снова.")