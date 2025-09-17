# Миграции Alembic

# Доработка кода с предыдущего занятия
'''
СОВЕТ ПРЕПОДАВАТЕЛЮ: если на предыдущем занятии вы не успели до конца модифицировать 
проект product_catalog - крайне рекомендуется выделить время и дописать программный код.
В любом случае рекомендуется напомнить студентам текущую структуру приложения с учетом наличия БД.
Особое внимание обратите на модули database.py и models.py.
'''

# -------------------------------------------------------------------------------------------------------------

# Установка и настройка Alembic

# Задание № 1 - установить библиотеку alembic
'''
Alembic - сторонняя библиотека, установим ее через pip внутри виртуального окружения нашего проекта product_catalog:
pip install alembic
'''

# Задание № 2 - провести инициализацию Alembic и изучить появившиеся файлы
'''
Для инициализации Alembic выполним в терминале следующую команду:
alembic init migrations

После выполнения в папке проекта появятся следующие файлы:
migrations/
    env.py              # настройка подключения к БД и импорт моделей
    README              # README-файл от Alembic
    script.py.mako      # Шаблон, по которому Alembic будет создавать новые миграции в папке versions/
    versions/           # папка, где будут храниться все миграции
alembic.ini             # главный файл конфигурации 
'''

# Задание № 3 - настроить файл alembic.ini
'''
Откроем alembic.ini и найдем строку:
sqlalchemy.url = driver://user:pass@localhost/dbname

Заменим ее на путь к нашей SQLite-базе:
sqlalchemy.url = sqlite:///./products.db
'''

# Задание № 4 - настроить файл env.py
'''
По умолчанию Alembic ничего не знает про наши модели SQLAlchemy.
Нужно показать ему объекты Base и engine из нашего проекта.

В файле migrations/env.py заменим/добавим следующий код:
'''
# подключаем объекты Base и engine
from database import Base, engine
# импортируем модели проекта
import models
...
# указываем, какие таблицы и модели нужно отслеживать для миграций
target_metadata = Base.metadata

# Задание № 5 - проверить настройки Alembic
'''
Для проверки, что все настроено корректно, выполним в терминале следующую команду:
alembic revision --autogenerate -m "init db"

revision - создать новый файл миграции
--autogenerate - включить автогенерацию на основе различий между моделями (Base.metadata) и схемой БД.
Без --autogenerate Alembic создаст пустой шаблон миграции, тогда код в upgrade()/downgrade() нужно писать вручную
-m "init db" - сообщение, которое попадет в название миграции, чтобы было понятно, для чего она
'''

# -------------------------------------------------------------------------------------------------------------

# Создание и применение миграций

# Задание № 6 - создать модель для новой таблицы orders
'''
В нашей БД есть таблица products. Создадим новую таблицу - orders, где будет храниться информация о заказах.
Поля таблицы orders:
- id - ID заказа (первичный ключ)
- customer_name - имя покупателя
- total_price - сумма заказа
- product_id - внешний ключ, ссылается на id в таблице products

Откроем models.py и добавим новый класс Order:
'''
# ForeignKey - класс для определения зависимости между двумя столбцами
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
# relationship() - функция для создания связи на уровне классов
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)             
    price = Column(Float, nullable=False)            
    in_stock = Column(Boolean, default=True)

# модель таблицы заказов
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    # создаем связь "один ко многим": заказ -> товары
    product_id = Column(Integer, ForeignKey('products.id'))
    # создаем связь с классом Product, объект Order сможет обращаться к полям Product напрямую
    product = relationship('Product')

# Задание № 7 - выполнить миграцию для появления таблицы orders в БД
'''
Т.к. в БД уже есть таблица products с данными, мы скажем Alembic, что БД в актуальном состоянии. Для этого есть команда:
alembic stamb head

Выполним миграцию:
alembic revision --autogenerate -m "create orders table"

Теперь применим миграцию:
alembic upgrade head

Если возникает необходимость откатить изменения, до для этого также есть команда:
alembic downgrade -1

При желании можно откатиться и дальше, указать конкретный идентификатор миграции:
alembic downgrade <revision_id>

Вернемся обратно к последней версии, с таблицей orders:
alembic upgrade head
'''

# -------------------------------------------------------------------------------------------------------------

# Изменение модели и миграции

# Задание № 8 - добавить новое поле status в таблицу orders
'''
Ранее мы создали модель Order и с помощью миграции внесли ее в БД.
Представим, что нам нужно дополнить таблицу новым полем под названием status,
который будет хранить статус заказа (Новый, В обработке, Выполнен)
'''
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product')
    # новое поле со статусом заказа (по умолчанию - Новый)
    status = Column(String, default='Новый', nullable=False)
'''
Создадим файл миграции следующей командой:
alembic revision --autogenerate -m "add_status_column_to_orders"

В появившемся файле миграций функции upgrade() и downgrade() будут выглядеть примерно так:
'''
def upgrade() -> None:
    op.add_column('orders', sa.Column('status', sa.String(), nullable=False))

def downgrade() -> None:
    op.drop_column('orders', 'status')

'''
Запустим миграцию:
alembic upgrade head
'''

# Задание № 9 - добавить новое поле delivery_address в таблицу orders
'''
Задание на самостоятельное выполнение:
1. Добавить в таблицу orders новое поле delivery_address - адрес доставка заказа (строка, обязательное)
2. Сгенерируйте миграцию с комментарием "add delivery_address column to orders"
3. Выполните миграцию
4. Проверьте, что поле появилось в таблице

Решение задания:
'''
# Шаг 1 - добавим в модель Order поле delivery_address
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product')
    status = Column(String, default='Новый', nullable=False)
    # новое поле с адресом доставки
    delivery_address = Column(String, nullable=False)

# Шаг 2 - сгенерируем миграцию с помощью команды:
# alembic revision --autogenerate -m "add delivery_address column to orders"

# Шаг 3 - выполним миграцию с помощью команды:
# alembic upgrade head

# Шаг 4 - зайдем в products.db, откроем таблицу orders и увидим новое поле delivery_address