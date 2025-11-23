# Реализация ролевой модели и разграничение доступа

# Разделение ролей в веб-приложении
'''
В созданных нами ранее FastAPI-проектах если и присутствует пользователь, то ему доступны все возможности и функции.
Оно и логично - мы создаем API, который могут использоваться другие.
Однако, в реальных проектах всегда есть минимальное разграничение доступа - есть обычные пользователи
приложения с базовыми возможностями, а есть "суперпользователи" или "администраторы", 
которым доступны дополнительные "фичи". 

Для примера рассмотрим обычный сервис объявлений, по типу "Авито".

Что может делать обычный пользователь:
- Зарегистрироваться и войти на сайт
- Посмотреть список объявлений
- Создать свое объявление
- Редактировать только свои объявления
- Удалять только свои объявления
- Редактировать свой профиль: имя, аватар, пароль и т.д.

Чего не может делать обычный пользователь:
- Управлять чужими объявлениями
- Управлять другими пользователями
- Видеть служебные настройки сайта

Суперпользователь/администратор может быть человеком из команды сервиса (например, модератор).
Что может делать суперпользователь:
- Все, что может делать обычный пользователь
- Просматривать любые данные любых пользователей
- Быстро получать список всех пользователей или всех объявлений
- Блокировать/удалять пользователей (например, за мошенничество)
- Исправлять/удалять любые объявления (например, с запрещенным контентом)
- Создавать других пользователей (суперпользователей в том числе)

Почему это важно:
- Если обычный пользователь может удалить чужое объявление или заблокировать другого пользователь, то
сервис быстро превратится в хаос.
- Если не будет администраторов, то никто не сможет реагировать на жалобы пользователей, спам
и нарушения правил сайта.

В реальных приложениях ролей может быть больше, чем 2, в зависимости от вида сервиса.
'''

# ----------------------------------------------------------------------------------------------------------

# Внедрение ролей в FastAPI-приложении
'''
Сегодня мы вновь обратимся к проекту с нашего последнего воркшопа и внедрим 3 роли:
- гость (незарегистрированный пользователь)
- обычный пользователь (авторизованный пользователь)
- суперпользователь (администратор)

К концу занятия у нас будут следующие возможности для описанных ролей:

| Описание                                   | Гость  | Обычный пользователь      | Суперпользователь                      |
|--------------------------------------------|--------|---------------------------|----------------------------------------|
| Получить данные текущего пользователя      | ❌     | ✅ Только свои данные    | ✅                                     |
| Получить пользователя по username          | ❌     | ✅ Только свои данные    | ✅ Данные любого пользователя          |
| Получить список всех пользователей         | ❌     | ❌                       | ✅                                     |
| Регистрация                                | ✅     | ✅                       | ✅                                     |
| Создать нового пользователя                | ❌     | ❌                       | ✅ В том числе и суперпользователя     |
| Обновить данные пользователя по ID         | ❌     | ✅ Только свои данные    | ✅ Данные любого пользователя          |
| Удалить пользователя по ID                 | ❌     | ❌                       | ✅ Можно удалять других пользователей ❌ Нельзя удалить самого себя |

СОВЕТ ПРЕПОДАВАТЕЛЮ: убедитесь, что у студентов есть последняя версия кода с воркшопа "Архитектура и авторизация API"
'''

# ----------------------------------------------------------------------------------------------------------

# Модификация моделей пользователей
'''
Итак, начнем внедрение ролей в наш проект с модификации пользовательских моделей в файле app/models/users.py.

1) Обновить модель таблицы Users
Один из наиболее простых вариантов для реализации ролевой модели пользователей - это добавление поля, 
которое показывает: "Является ли пользователь суперпользователем?". Добавим такое поле в класс User,
назовем его is_superuser, оно будет логическим, обязательным и иметь значение False по умолчанию:
'''

# app/models/users.py

# импорты не меняем, добавлены для удобства
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field
from app.models import Base

# модель таблицы "Пользователи"
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    full_name = Column(String(128), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # добавляем поле-флаг для суперпользователя
    is_superuser = Column(Boolean, default=False, nullable=False)

'''
2) Обновить модель UserBase
Далее необходимо добавить поле is_superuser в Pydantic-модель UserBase.
Значение по умолчанию также укажем False, т.к. чаще всего взаимодействие будет происходить
с обычными пользователями:
'''

# обновленная базовая модель пользователя
class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    is_active: bool = True
    # добавляем поле-флаг для суперпользователя
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=128)

'''
3) Создать новую модель UserRegister
С учетом того, что у нас появилось поле is_superuser, необходимо создать новую модель UserRegister
для регистрации нового пользователя, которая как раз будет использоваться Гостем. 
При создании модели будем следовать следующим правилам:
- Наследуемся от BaseModel, чтобы не перетаскивать is_superuser из UserBase, иначе простой пользователь 
сам сможет сделать себя суперпользователем
- Модель UserCreate тоже будет, но только для использования суперпользователем
'''

# новая модель пользователя при регистрации
class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    full_name: str | None = Field(default=None, max_length=128)
    password: str = Field(min_length=8, max_length=64)

'''
4) Обновить использование модели UserCreate
Сам код модели UserCreate останется прежним, но мы для себя зафиксируем, что использоваться
модель будет только при создании нового пользователя именно суперпользователем.
'''

# модель для создания нового пользователя (код не меняется, только для админа)
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)

'''
Остальные модели трогать не будем, на этом модификация файла app/models/users.py закончена,
можем двигаться дальше.
'''

# ----------------------------------------------------------------------------------------------------------

# Обновление структуры БД
'''
После обновления моделей нам необходимо создать и применить миграцию с помощью Alembic, чтобы обновить структуру нашей БД.
Для этого выполним следующую команду, добавив пояснение:

В терминале:
alembic revision --autogenerate -m "add_is_superuser_column_to_users"

Затем применим созданную миграцию:

В терминале:
alembic upgrade head

Но при выполнении миграции появится ошибка:
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) Cannot add a NOT NULL column with default value NULL

Разберемся, в чем же проблема. Дело в том, что для уже существующих строк в таблице users значение новой колонки будет NULL, 
а это конфликтует с nullable=False. Есть разные способы исправления данной ситуации и один из вариантов - вручную поправить миграцию.

Откроем файл последней миграции - alembic/versions/<hash>_add_is_superuser_column_to_users.py
Внутри функции upgrade(), где указывается sa.Column(), укажем дополнительный параметр:
'''

# alembic/versions/<hash>_add_is_superuser_column_to_users.py

server_default=sa.text('false')

'''
Теперь при добавлении колонки все уже существующие строки получат 0 (False).

Попробуем заново применить миграцию:

В терминале:
alembic upgrade head

Ошибка пропадет и если мы откроем файл products.db, то увидим новую колонку is_superuser.
Структура нашей БД обновлена, можем двигаться дальше.
'''

# ----------------------------------------------------------------------------------------------------------

# Обновление функций для работы с БД
'''
Перед обновлением эндпоинтов обновим файл app/repositories/users.py, где лежат функции для взаимодействия с БД.
Добавим 2 новых функции:
- получение списка всех пользователей (только для админа)
- удаление пользователя (только для админа)
'''

# app/repositories/users.py

# импорты не меняем, добавлены для удобства
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models.users import User, UserCreate, UserUpdate
...
# новая функция - получение списка пользователей (для админа)
async def get_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    result = await session.execute(statement)
    return list(result.scalars().all())

# новая функция - удаление пользователя (для админа)
# принимаем User, чтобы логику поиска вынести в эндпоинт
async def delete_user(session: AsyncSession, user_db: User):
    await session.delete(user_db)
    await session.commit()
...

'''
Новые функции готовы, можем двигаться дальше.
'''

# ----------------------------------------------------------------------------------------------------------

# Создание новой зависимости для суперпользователя
'''
Прежде, чем двигаться к обновлению эндпоинтов, создадим новую функцию-зависимость в app/api/deps.py для проверки,
что текущий пользователь является суперпользователем. Будем использовать эту зависимость в эндпоинтах,
которые предназначены только для суперпользователей:
'''

# app/api/deps.py
...
# получаем текущего супер-пользователя (администратора)
def get_current_superuser(current_user: CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='У пользователя недостаточно прав для данного действия'
        )
    return current_user

'''
Новая функция-зависимость готова, теперь можем двигаться к пользовательским эндпоинтам.
'''

# ----------------------------------------------------------------------------------------------------------

# Обновление пользовательских эндпоинтов
'''
Наиболее глобальные изменения будут именно в файле app/api/routes/users.py - без модификаций останется только
get_user_me(), остальные эндпоинты будут модифицированы, а также добавятся новые.

1) Обновить импорты
Начнем с актуализации импортов, подключая новую зависимость, новую модель и новые функции для работы с пользователями в БД:
'''

# app/api/routes/users.py

from fastapi import APIRouter, HTTPException, Depends

# импортируем новую зависимость, новую модель и новые функции для работы с пользователями в БД
from app.models.users import UserRegister, UserCreate, UserUpdate, UserOut
from app.api.deps import (
    SessionDep, 
    CurrentUserDep, 
    get_current_superuser
)
from app.repositories.users import (
    create_user as create_user_repo,
    update_user as update_user_repo,
    delete_user as delete_user_repo,
    get_user_by_username,
    get_user_by_id,
    get_users
)

# роутер не меняется, добавлен для удобства
router = APIRouter(prefix='/users', tags=['users'])

'''
2) Обновить get_user()
Затем обновим get_user(), где мы получали пользователя по username, по следующим правилам:
- Если простой пользователь запрашивает информацию о себе - все окей
- Если простой пользователь запрашивает информацию о другом пользователе - только для админа
'''

# получить пользователя по username - модифицируем:
# - Если простой пользователь запрашивает информацию о себе - все окей
# - Если простой пользователь запрашивает информацию о другом пользователе - только для админа
@router.get('/{username}', response_model=UserOut)
async def get_user(session: SessionDep, username: str, current_user: CurrentUserDep):
    user = await get_user_by_username(session=session, username=username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )
    # если смотрим другого пользователя и текущий пользователь не админ
    if user.username != current_user.username and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='У пользователя недостаточно прав для данного действия'
        )
    return user

'''
3) Создать get_users_list()
Далее создадим новый админский эндпоинт get_users_list() для получения списка всех пользователей:
'''

# новый эндпоинт - получить список всех пользователей (только для админа)
# указываем зависимость в параметре dependencies для проверки, что пользователь является админом
@router.get('/', response_model=list[UserOut], dependencies=[Depends(get_current_superuser)])
async def get_users_list(session: SessionDep, skip: int = 0, limit: int = 100):
    users = await get_users(session=session, skip=skip, limit=limit)
    return users

'''
4) Создать register_user()
Создадим еще один новый эндпонт - register_user() - для создания нового пользователя без предварительного
входа в систему, что по сути является классической регистрацией:
'''

# новый эндпоинт - создать нового пользователя без предварительного входа в систему 
# (классическая регистрация)
@router.post('/signup', response_model=UserOut)
async def register_user(session: SessionDep, user_data: UserRegister):
    user = await get_user_by_username(session=session, username=user_data.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail='Пользователь с таким username уже существует в системе'
        )
    user_create = UserCreate(
        username=user_data.username,
        full_name=user_data.full_name,
        password=user_data.password
        # is_active и is_superuser возьмут значения по умолчанию
    )
    new_user = await create_user_repo(session=session, user_create=user_create)
    return new_user

'''
5) Обновить create_user()
Также следуем обновить create_user(), чтобы он работал только для суперпользователя:
'''

# создать нового пользователя - модифицируем, чтобы работало только для админа
@router.post('/', response_model=UserOut, dependencies=[Depends(get_current_superuser)])
async def create_user(session: SessionDep, user_data: UserCreate):
    user = await get_user_by_username(session=session, username=user_data.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail='Пользователь с таким username уже существует в системе'
        )
    new_user = await create_user_repo(session=session, user_create=user_data)
    return new_user

'''
6) Обновить update_user()
Предпоследнее изменение - обновим update_user() по следующим правилам:
- Простой пользователь может обновить только свои данные
- Админ может обновить данные любого пользователя
- Для удобства использования поменяем put на patch
'''

# обновить данные пользователя по id - модифицируем:
# - Простой пользователь может обновить только свои данные
# - Админ может обновить данные любого пользователя
# - Для удобства использования поменяем put на patch
@router.patch('/{user_id}', response_model=UserOut)
async def update_user(session: SessionDep, user_id: int, user_data: UserUpdate, current_user: CurrentUserDep) -> UserOut:
    user_db = await get_user_by_id(session=session, user_id=user_id)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
        )
    # если обновляем другого пользователя и текущий пользователь не админ
    if user_db.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='У пользователя недостаточно прав для данного действия'
        )

    updated_user = await update_user_repo(
        session=session,
        user_db=user_db,
        user_update=user_data,
    )
    return updated_user

'''
7) Создать delete_user()
Финальное изменение - создадим админский эндпоинт delete_user() для удаления пользователя по ID:
'''

# новый эндпоинт - удалить пользователя по ID (только для админа)
@router.delete('/{user_id}', dependencies=[Depends(get_current_superuser)])
async def delete_user(session: SessionDep, current_user: CurrentUserDep, user_id: int):
    user_db = await get_user_by_id(session=session, user_id=user_id)
    if not user_db:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден',
    )
    # админ не может удалить сам себя
    if user_db.id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Администраторам нельзя удалять себя'
        )
    
    await delete_user_repo(session=session, user_db=user_db)
    return {'message': 'Пользователь успешно удален'}

'''
Прекрасно! Все эндпоинты обновлены, и, казалось бы, мы готовы их тестировать. Но есть одна маленькая проблемка,
о которой сейчас поговорим.
'''

# ----------------------------------------------------------------------------------------------------------

# Добавление первого суперпользователя
'''
Казалось бы - весь код готов для реализации ролевой модели, но если мы попробуем запустить приложение
и протестировать админские эндпоинты в Swagger, то у нас ничего не получится. Все правильно, нам нужно
авторизоваться как суперпользователь. И вот тут проблема - какие логин и пароль нам вводить? 
В нашей БД нет ни одного суперпользователя, а зарегистрироваться можно только как обычный пользователь.
Не переживайте, эту ситуацию, конечно, тоже можно решить. Нужно сделать так, чтобы в нашей БД появился
суперпользователь, и тогда мы сможем авторизоваться под его данными. Суперпользователя в БД можно добавить
разными способами, мы сделаем так:

- Напишем скрипт для создания и добавления суперпользователя в БД
- Запустим скрипт 1 раз, до запуска FastAPI-приложения
- Убедимся, что в БД появился суперпользователь
- Запустим FastAPI-приложение и залогинимся как суперпользователь

Итак, создадим файл скрипт в корне папки app/, назовем его create_superuser.py:

app/
├─ api/
├─ core/
├─ models/
├─ repositories/
├─ create_superuser.py
└─ main.py

В файле пропишем следующий код:

СОВЕТ ПРЕПОДАВАТЕЛЮ: если не хватает времени, то отправьте студентам код файла create_superuser.py
и быстро прокомментируйте его содержимое.
'''

# app/create_superuser.py

# подключаем asyncio для асинхронного запуска кода
import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.users import User

# функция для создания суперпользователя (если их еще нет в БД)
async def create_superuser():
    async with AsyncSessionLocal() as session:
        # придумываем username и password для первого суперпользователя
        username = 'admin'
        password = 'admin123'
        # проверяем, есть такой суперпользователь в БД или нет
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        check_user = result.scalar_one_or_none()
        if check_user:
            print(f'Такой {username} уже существует')
            return
        # создаем суперпользователя и добавляем его в БД
        super_user = User(
            username=username,
            full_name = 'Администратор',
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True
        )
        session.add(super_user)
        await session.commit()
        print(f'Суперпользователь создан: {username}/{password}')

# создаем суперпользователя только при прямом запуске файла
if __name__ == '__main__':
    asyncio.run(create_superuser())

'''
Скрипт готов, для  его запуска выполним в терминале следующую команду:
python -m app.create_superuser

Так в нашей БД появится первый суперпользователь с правами администратора.
Можем открыть products.db и убедиться в этом.

Теперь мы можем запустить наше FastAPI-приложение и войти под данными суперпользователя:

username: admin
password: admin123

Мы увидим сообщение "Authorized", теперь можно тестировать админские эндпоинты.
'''