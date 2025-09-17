# Повторение Python

# Повторение синтаксиса Python

'''
- Переменные, типы и структуры данных
- Условия: if, elif, else
- Циклы: for, while
- Функции: def, return, *args, **kwargs, декораторы
- Списковые включения (list comprehensions)
'''

# Переменные, типы и структуры данных, условия, циклы

# Типы данных
name = 'Дима'
age = 27
height = 1.78
is_working = True

# Cтруктуры данных
salaries = [180000, 200000, 220000]
months = ('Январь', 'Февраль', 'Март')
skills = {'Python', 'SQL', 'Docker'}
employee = {
    'name': name,
    'age': age,
    'height': height,
    'is_working': is_working,
    'skills': skills,
    'salaries': salaries
}

# Условия
if age >= 18:
    print('Взрослый')
elif age >= 14:
    print('Подросток')
else:
    print('Ребенок')

# Перебор элементов списка через цикл for
for salary in salaries:
    print(salary)

# Тоже перебор элементов, но через цикл while
i = 0
while i < len(salaries):
    print(salaries[i])
    i += 1


# Функции, аргументы и декораторы

# Функция с параметром
def greet(name):
    return f'Hello, {name}!'

print(greet('Дима'))

# Функция с аргументом по умолчанию
def greet(name='Пользователь'):
    return f'Hello, {name}!'

print(greet())

# Функция, принимающая любое количество позиционных аргументов
def calc_average(*args):
    return sum(args) / len(args)

nums = [10, 20, 30, 100]
print(calc_average(*nums))

# Функция, принимающая любое количество именованных аргументов
def show_users_info(**kwargs):
    for key, value in kwargs.items():
        print(f'{key}: {value}')

users = [
    {'name': 'Дима', 'age': 27},
    {'name': 'Максим', 'age': 29}
]

for user in users:
    show_users_info(**user)

# Использование декораторов
# lru_cache() - запоминает результат вызова функции, чтобы повторно не выполнять ее при тех же аргументах
from functools import lru_cache

@lru_cache(maxsize=1000)
def fibonacci(n):
    print(f'Вычисление F({n})')
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(7))     # Увидим все вычисления
print(fibonacci(7))     # Увидим только результат
print(fibonacci(8))     # Увидим только новые вычисления


# Списковые включения (list comprehensions)
nums = [1, 2, 3, 4, 5, 6, 7]
squares = [n**2 for n in nums]
print(squares)

evens = [n for n in squares if n % 2 == 0]
print(evens)

# -------------------------------------------------------------------------------------

# Работа с модулями

'''
Модуль - это любой .py-файл, который можно импортировать.
В больших проектах код почти никогда не хранится в одном файле.
'''

# Импорт всего модуля
import utils

print(utils.fibonacci(8))

# Импорт только нужной функции
from utils import fibonacci

print(fibonacci(8))

# Использование if __name__ == "__main__" (на примере utils.py)

'''
В каждом модуле Python есть служебная переменная __name__.
Если модуль запускается напрямую, то в переменной __name__ будет значение '__main__'.
Если модуль импортируется, то __name__ будет содержать имя импортируемого файла.
Код внутри if __name__ == "__main__" не исполняется при импорте.
Это позволяет добавлять локальные тесты и запускать модуль отдельно, 
не мешая другим частям проекта.
'''

# -------------------------------------------------------------------------------------

# ООП в Python

# Создание класса с инициализатором
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

new_user = User(username='Dima', email='dima123@mail.ru')
print(new_user.username)
print(new_user.email)

# Атрибуты и методы
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
    
    def hello(self):
        return f'Привет, {self.username}!'

new_user = User(username='Dima', email='dima123@mail.ru')
print(new_user.hello())

# Инкапсуляция и приватные атрибуты
class User:
    def __init__(self, username, email, salary):
        self.username = username
        self.email = email
        self.__salary = salary
    
    def hello(self):
        return f'Привет, {self.username}!'  
    
    def get_salary(self):
        return self.__salary

new_user = User(username='Dima', email='dima123@mail.ru', salary=200000)
print(new_user.__salary)    # Ошибка AttributeError
print(new_user.get_salary())

# Наследование и функция super()
class Admin(User):
    def __init__(self, username, email, salary, role):
        super().__init__(username, email, salary)
        self.role = role
    
    def hello(self):
        return f'[ADMIN] {super().hello()}'

admin = Admin(
    username='Maks', 
    email='maks777@mail.ru', 
    salary=200000, 
    role='superuser')

print(admin.hello())