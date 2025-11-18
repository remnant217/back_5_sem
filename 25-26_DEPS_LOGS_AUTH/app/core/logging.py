import os
import sys
from loguru import logger

# настройка источников логирования для проекта
def setup_logging():
    logger.remove()

    # логирование в консоль
    logger.add(
        sink=sys.stderr,
        level='DEBUG',
        format='<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | {name}:<cyan>{function}</cyan> | <level>{message}</level>',
        colorize=True
    )

    # подготавливаем папку для хранения лог-файлов
    os.makedirs('logs', exist_ok=True)

    # логирование в logs/app.log (все логи)
    logger.add(
        sink='logs/app.log',
        level='INFO',
        format='{time:HH:mm:ss} | {level:8} | {name}:{function}:{line} | {message}',
        rotation='10 MB',    
        retention='7 days',    
        compression='zip',
    )