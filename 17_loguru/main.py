from fastapi import FastAPI
# импортируем logger, чтобы сохранять логи внутри эндпонитов
from loguru import logger
from logging_app import setup_logging

# запускаем логирование в проекте
setup_logging()

app = FastAPI()

# обращение к корневому каталогу
@app.get('/')
async def root():
    logger.info('Вызван корневой эндпоинт')
    return {'message': 'Приложение с loguru работает корректно'}

# вычисление математического выражения
@app.get('/calc')
# получаем на вход строку с выражением (например, 2 + 2)
async def get_calc(expression: str):
    logger.info('Пользователь обратился к эндпоинту /calc')
    # пробуем вычислить выражение
    try:
        logger.info(f'Попытка вычислить выражение {expression}')
        # проводим вычисления
        result = eval(expression)
        logger.info(f'Результат вычисления: {result}')
        return {'result': f'Результат вычисления: {result}'}
    # если при вычислении возникла ошибка
    except Exception as e:
        logger.exception('При вычислении произошла ошибка')
        return {'error': f'При вычислении произошла ошибка: {e}'}