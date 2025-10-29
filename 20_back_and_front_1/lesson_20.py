# Интеграция с фронтендом 1

# Подготовка структуры проекта

# Задание № 1 - оформить каркас проекта
'''
├─ main.py                  # точка входа в приложение
├─ routers/
│  └─ products.py           # эндпоинты
└─ static/                  # статические файлы
    ├─ index.html           # главная страница
    ├─ products.html        # список товаров
    ├─ add_product.html     # форма для добавления товара
    └─ styles.css           # CSS-стили

'''

# Задание № 2 - рассмотреть содержимое статических файлов

# Задание № 3 - оформить файл routers/products.py

from fastapi import APIRouter
# RedirectResponse - класс, перенаправляющий клиента на другой URL
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get('/')
async def root():
    # переадресация на страницу index.html
    return RedirectResponse(url='/static/index.html')


# Задание № 4 - оформить файл main.py

from fastapi import FastAPI
# StaticFiles - класс для работы со статическими файлами
from fastapi.staticfiles import StaticFiles
# подключаем роутер из файла routers/products.py
from routers.products import router

app = FastAPI()

# mount() - метод, позволяющий "вмонтировать под-приложение" в основное FastAPI-приложение
# добавляем папку со статическими файлами под именем static
app.mount(
    path='/static',
    app=StaticFiles(directory='./static'),
    name='static'
)

# подключаем роутер
app.include_router(router=router)

# ---------------------------------------------------------------------------------------------------

# Знакомство с шаблонизатором Jinja2

# Задание № 5 - установить Jinja2
'''
pip install jinja2

Документация Jinja2: https://jinja.palletsprojects.com/en/stable/templates/
'''

# Задание № 6 - создать папку /templates

# Задание № 7 - подключить Jinja2 в routers/products.py

# подключаем класс Request для корректной работы с запросами
from fastapi import APIRouter, Request
# HTMLResponse - класс, позволяющий возвращать HTML-содержимое из эндпоинта
from fastapi.responses import RedirectResponse, HTMLResponse
# Jinja2Templates - класс, позволяющий встраивать динамические данные в HTML-шаблоны
from fastapi.templating import Jinja2Templates

router = APIRouter()
# создаем менеджер шаблонов и указываем путь, где лежат HTML-шаблоны
templates = Jinja2Templates(directory='./templates')

# псевдо-БД с данными
products_db: list[dict] = [
    {'id': 1, 'title': 'Ноутбук', 'price': 79990, 'stock': 5},
    {'id': 2, 'title': 'Клавиатура', 'price': 2990, 'stock': 12},
    {'id': 3, 'title': 'Наушники', 'price': 1990, 'stock': 10}
]

# через response_class явно указываем, что ответ от сервера будет в виде HTML
@router.get('/', response_class=HTMLResponse)
async def root():
    return RedirectResponse(url='/static/index.html')

# обработка запроса на получение списка товаров
@router.get('/products', response_class=HTMLResponse)
# request нужен для корректной работы с шаблонами Jinja2
async def get_products_list(request: Request):
    # TemplateResponse - метод для отображения данных шаблонами Jinja2
    return templates.TemplateResponse(
        # name - имя файла в папке с шаблонами
        name='products.html',
        # context - словарь с переменными, которые будут доступны в HTML-файле
        context={'request': request, 'products': products_db}
    )

# ---------------------------------------------------------------------------------------------------

# Преобразование products.html

# Задание № 8 - переместить products.html в папку /templates

# Задание № 9 - внедрить Jinja2 в код файла products.html
'''
    <tbody>
      {% for p in products %}
      <tr>
        <td>{{ p.id }}</td>
        <td>{{ p.title }}</td>
        <td>{{ p.price }}</td>
        <td>{{ p.stock }}</td>
      </tr>
      {% endfor %}
    </tbody>



  {% if products|length == 0 %}
    <p>Товаров пока нет</p>
  {% else %}
    <table>
    ...
    </table>
  {% endif %}


          <td>{{ p.price | int }}</td>
          <td>{{ p.stock | int }}</td>

'''

# ---------------------------------------------------------------------------------------------------

# Преобразование add_product.html

# Задание № 10 - добавить новые эндпоинты в routers/products.py

# Form - класс для работы с данными из формы
from fastapi import Form
...
# обработка GET-запроса на получение формы создания товара
@router.get('/products/new', response_class=HTMLResponse)
async def get_new_product_form(request: Request):
    return templates.TemplateResponse(
        name='add_product.html',
        context={'request': request}
    )

# обработка POST-запроса на создание товара
@router.post('/products/create')
async def create_product(
    # указываем, что параметры придут из формы и выставляем ограничения
    title: str = Form(min_length=2),
    price: float = Form(ge=0),
    stock: int = Form(ge=0)
):
    # генерируем ID для нового товара
    next_id = max((p['id'] for p in products_db), default=0) + 1
    # добавляем новый товар в псевдо-БД
    products_db.append({
        'id': next_id,
        'title': title,
        'price': price,
        'stock': stock
    })
    # перенаправляем на страницу со списком товаров
    # ОБЯЗАТЕЛЬНО указываем status_code=303, чтобы произошел редирект,
    # но с методом GET на новый URL (по умолчанию возвращается 307, с ним будет ошибка)
    return RedirectResponse(url='/products', status_code=303)

# Задание № 11 - переместить add_product.html в папку /templates

# Задание № 12 - внести изменения в add_product.html
'''

1) В строке <a href="/static/products.html">Список</a> поменяем путь на "/products",

2) Для открывающего тега <form> внутри добавим action="/products/create" и method="post",
получится <form action="/products/create" method="post">. 

3) Для тегов <input> добавим параметр name, где укажем такие же имена, которые мы передавали
ранее в Form() внутри create_product(). Получится так:
...<input name="title" ...
...<input name="price" ...
...<input name="stock" ...

4) Для кнопки в теге <button> для параметра type укажем "submit", чтобы при нажатии на кнопку
данные из формы действительно отправлялись на сервер. Получится так:
<button type="submit">...
'''

# ---------------------------------------------------------------------------------------------------

# Преобразование index.html

# Задание № 13 - модифицировать эндпоинт root()

@router.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        context={'request': request}
    )

# Задание № 14 - переместить add_product.html в папку /templates

# Задание № 15 - модифицировать ссылки во всех HTML-файлах
'''
index.html:
  <p><a class="button" href="/products">Список товаров</a></p>
  <p><a class="button" href="/products/new">Добавить товар</a></p>

add_product.html:
      <a href="/">Главная</a>
    
products.html:
      <a href="/">Главная</a>
      <a href="/products/new">Добавить</a>
'''