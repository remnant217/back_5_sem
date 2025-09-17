# ForeignKey - класс для определения зависимости между двумя столбцами
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
# relationship() - функция для создания связи на уровне классов
from sqlalchemy.orm import relationship
from .database import Base

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
    # новое поле со статусом заказа (по умолчанию - Новый)
    status = Column(String, default='Новый', nullable=False)
    # новое поле с адресом доставки
    delivery_address = Column(String, nullable=False)