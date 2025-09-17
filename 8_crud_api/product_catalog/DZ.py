# ВАЖНО: данный код ДОБАВЛЯЕТСЯ к уже существующему, который вы написали на занятии в файле main.py

# добавляем импорт функции Query() к остальным импортам 
from fastapi import Query

# эндпоинт для обработки GET-запроса на получение списка товаров по заданным фильтрам
@app.get('/products', response_model=List[Product])
def get_products_list(
    # параметры фильтрации
    q: str | None = Query(default=None, description='Поиск по подстроке'),
    in_stock: bool | None = Query(default=None, description='Фильтр по наличию'),
    min_price: float | None = Query(default=None, ge=0, description='Минимальная цена'),
    max_price: float | None = Query(default=None, ge=0, description='Максимальная цена')
):
    # список со всеми товарами
    result = list(store.products.values())

    # если передана подстрока для поиска
    if q is not None:
        # приводим подстроку к нижниму регистру
        q_low = q.lower()
        # формируем список товаров с подстроками в названии
        result = [p for p in result if q_low in p.name.lower()]
    
    # если передан фильтр поиска по наличию
    if in_stock is not None:
        # формируем список товаров в соответствии с фильтром (в наличии / не в наличии)
        result = [p for p in result if p.in_stock is in_stock]
    
    # если передана минимальная цена
    if min_price is not None:
        # формируем список товаров, цена которых >= минимальной
        result = [p for p in result if p.price >= min_price]
    
    # если передана максимальная цена
    if max_price is not None:
        # формируем список товаров, цена которых <= максимальной
        result = [p for p in result if p.price <= max_price]
    
    # возвращаем итоговый список с товарами 
    return result