# подключаем необходимые инстурменты из Pydantic
from pydantic import BaseModel, EmailStr, Field, field_validator

# создаем модель пользователя
class User(BaseModel):
    name: str = Field(..., description='Имя пользователя')
    age: int = Field(..., gt=0, description='Возраст')
    email: EmailStr = Field(..., description='Электронная почта')

    # проверка, что имя состоит только из букв
    @field_validator('name')
    def name_only_letters(cls, value: str):
        if not value.isalpha():
            raise ValueError('Имя должно содержать только буквы')
        return value

# функция для подсчетка количества корректных строк
def count_valid_users(file_path: str) -> int:
    # счетчик корректных строк
    valid_count = 0

    # открываем поток работы с файлом
    with open(file_path, encoding='utf-8') as f:
        # перебираем строки в файле
        for line in f:
            # разбиваем строку на отдельные части (имя, возраст, email)
            parts = line.strip().split()
            name, age, email = parts

            # пробуем создать экземляр класса User
            try:
                # если объект создался - строка валидная
                User(name=name, age=age, email=email)
                valid_count += 1
            # если возникла ошибка - строка невалидная
            except:
                pass

    # возвращаем количество корректных строк
    return valid_count

# вызываем функцию и выводим ответ на экран
print(count_valid_users(file_path='users.txt'))