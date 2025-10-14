from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# необходимые импорты из других файлов проекта
from .exceptions import OutOfStockError
from .routers import router

app = FastAPI()

# обработчик исключения OutOfStockError
@app.exception_handler(OutOfStockError)
async def out_of_stock_handler(request: Request, exc: OutOfStockError):
    return JSONResponse(
        status_code=409, 
        content={
            'error': 'out_of_stock',
            'item_id': exc.item_id,
            'item_name': exc.item_name,
            'requested': exc.requested,
            'available': exc.available,
            'message': f'Невозможно купить {exc.requested}, доступно только {exc.available}'
        }
    )

# подключаем роутер с эндпоинтами
app.include_router(router)