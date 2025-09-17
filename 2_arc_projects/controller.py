from note_logic import add_note, show_notes

def run():
    while True:
        print("1. Добавить 2. Показать 3. Выйти")
        cmd = input("Выберите команду: ")
        if cmd == "1":
            title = input("Заголовок: ")
            text = input("Текст: ")
            add_note(title, text)
        elif cmd == "2":
            show_notes()
        elif cmd == "3":
            break