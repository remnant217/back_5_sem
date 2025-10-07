# Логирование в FastAPI

# Введение в loguru

# Задание № 1 - установить библиотеку loguru
'''
Установка loguru:
pip install loguru
'''


# Задание № 2 - подключить объект logger в программу

# logger - объект для отправки сообщений с логами
from loguru import logger


# Задание № 3 - вывести в терминал приветственное информационное сообщение

# info() - метод для регистрации информационного сообщения 
logger.info('Привет от loguru!')


# Задание № 4 - создать сообщение каждого уровня и посмотреть на результат в терминале:

logger.trace('Сообщение трассировки')
logger.debug('Проводим дебаг модуля')
logger.info('Запускаем сервер')
logger.success('Сервер успешно запущен')
logger.warning('Сервер медленно обрабатывает запросы')
logger.error('Не удалось обновить ресурс')
logger.critical('Потеряно соединение с сервером')


# Задание № 5 - сбросить стандартную настройку объекта logger и указать новую с помощью метода add()

# импортируем модуль sys для указания, чтобы логи выводились в терминал
import sys

# сбрасываем стандартные настройки объекта logger
logger.remove()

# add() - метод для собственной настройки объекта logger
logger.add(
    sink=sys.stderr,    # sys.stderr - файловый объект, соответствующий стандартному потоку ошибок
    level='TRACE',      # минимальный уровень отображения сообщений
    format='<green>{time}</green> | {level} | {message}',      # шаблон, используемый для форматирования логов перед отправкой
    colorize=True       # цветной вывод (если указаны цвета)
)


# Задание № 6 - создать простую функцию для валидации имени пользователя и настроить метод add()

# обновим метод add()
logger.add(
    sink=sys.stderr,
    level='DEBUG',
    format='<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | {name}:<cyan>{function}</cyan> | <level>{message}</level>',
    colorize=True
)

# функция валидации имени пользователя
def is_valid_name(user_id, name):
    logger.info(f'Обрабатываем пользователя {user_id}')

    if len(name) < 2:
        logger.warning(f'Слишком короткое имя: {name}')
        return False
    
    logger.debug(f'Имя корректно: {name}')
    return True

# протестируем работу логов
print(is_valid_name(123, 'Иван'))
print(is_valid_name(124, 'А'))


# Задание № 7 - настроить новые параметры в методе add() и реализовать сохранение
# логов в лог-файл, находящийся внутри папки logs/

# импортируем модуль os для создания папки logs/ в коде
import os

# создаем папку для хранения логов (если папка уже существует - новая не создается)
os.makedirs('logs', exist_ok=True)

# не забываем сбросить стандартные настройки logger-а
logger.remove()

# указываем новые настройки 
logger.add(
    sink='logs/app.log',    # файл, куда сохранять логи
    level='INFO',
    # убираем теги в параметр format, иначе логи запишутся с лишними символами
    format='{time:HH:mm:ss} | {level:8} | {name}:{function} | {message}',
    rotation='100 KB',    # новый файл каждые 100 килобайт
    retention='1 day',    # обновлять файлы с логами каждый день
    compression='zip'     # сжимать старые файлы в формат ZIP
)

# генерируем много логов для тестирования
for i in range(1000):
    logger.info(f'Тестовое сообщение № {i}')

    if i % 100 == 0:
        logger.warning(f'Каждое сотое сообщение - предупреждение, № {i}')


# ----------------------------------------------------------------------------------------------------------

# Интеграция loguru и FastAPI

# Задание № 8 - реализовать файл logging_app.py

from loguru import logger
import os
import sys

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
        # line - показывает номер строчки в файле, откуда было вызвано сохранение лога
        format='{time:HH:mm:ss} | {level:8} | {name}:{function}:{line} | {message}',
        rotation='10 MB',    
        retention='7 days',    
        compression='zip',
    )

    # логирование в logs/errors.log (ошибки)
    logger.add(
        sink='logs/errors.log',
        level='ERROR',
        # exception - показывает возникшее исключение
        format='{time:HH:mm:ss} | {level:8} | {name}:{function}:{line} | {message}\n{exception}',
        rotation='10 MB',    
        retention='7 days',    
        compression='zip'
    )


# Задание № 9 - реализовать файл main.py

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