# подключаем класс APIRouter
from fastapi import APIRouter

router = APIRouter(
    # prefix - общий путь для всех маршрутов роутера 
    prefix='/products', # все маршруты в роутере будут начинаться с /products
    # tags - метка, по которой маршруты будут сгруппированы в Swagger UI
    tags=['Products']
)

# обработка GET-запроса по пути /products/
@router.get('/')
def get_product():
    return {'id': 123, 'name': 'Название продукта'}

# обработка POST-запроса по пути /products/
@router.post('/')
def create_product():
    return {'message': 'Продукт создан'}