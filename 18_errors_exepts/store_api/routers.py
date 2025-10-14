from fastapi import APIRouter, HTTPException

# необходимые импорты из других файлов проекта
from .storage import store
from .models import ItemUpdate
from .exceptions import OutOfStockError

# объявление роутера с префиксом /items
router = APIRouter(prefix='/items')

# получение информации о товаре по ID
@router.get('/{item_id}')
async def get_item(item_id: int):
    if item_id not in store:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return store[item_id]

# обновление информации о товаре по ID
@router.put('/{item_id}')
async def put_item(item_id: int, data: ItemUpdate):
    if item_id not in store:
        raise HTTPException(status_code=404, detail='Товар не найден')
    
    store[item_id] = {'name': data.name, 'count': data.count}
    return store[item_id]

# обработка запроса на покупку определенного количества товара
@router.post('/{item_id}/{count}')
async def buy_items(item_id: int, count: int):
    if item_id not in store:
        raise HTTPException(status_code=404, detail='Товар не найден')
    
    item = store[item_id]
    # если на складе нет запрашиваемого количества товара
    if count > item['count']:
        raise OutOfStockError(
            item_id=item_id, 
            item_name=item['name'], 
            requested=count, 
            available=item['count']
    )
    
    # уменьшаем количество товара на складе и возвращаем ответ клиенту
    item['count'] -= count
    return {
        'message': 'Покупка оформлена',
        'item_name': item['name'],
        'bought': count,
        'left': item['count']
    }