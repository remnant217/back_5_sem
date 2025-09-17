from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)             
    price = Column(Float, nullable=False)            
    in_stock = Column(Boolean, default=True)