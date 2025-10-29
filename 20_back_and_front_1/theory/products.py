from fastapi import APIRouter
# RedirectResponse - класс, перенаправляющий клиента на другой URL
from fastapi.responses import RedirectResponse

router = APIRouter()

# обработка GET-запроса для доступа к странице index.html
@router.get('/')
async def root():
    # переадресация на страницу index.html
    return RedirectResponse(url='/static/index.html')


