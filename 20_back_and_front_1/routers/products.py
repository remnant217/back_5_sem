from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory='./templates')

# псевдо-БД с данными
products_db: list[dict] = [
    {'id': 1, 'title': 'Ноутбук', 'price': 79990, 'stock': 5},
    {'id': 2, 'title': 'Клавиатура', 'price': 2990, 'stock': 12},
    {'id': 3, 'title': 'Наушники', 'price': 1990, 'stock': 10}
]

@router.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        context={'request': request}
    )

# обработка запроса на получение списка товаров
@router.get('/products', response_class=HTMLResponse)
async def get_products_list(request: Request):
    return templates.TemplateResponse(
        name='products.html',
        # context - словарь с переменными, которые будут доступны в HTML-файле
        context={'request': request, 'products': products_db}
    )

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
    return RedirectResponse(url='/products', status_code=303)