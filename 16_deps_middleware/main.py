from fastapi import FastAPI, Depends, Request
from typing import Annotated
from time import perf_counter

app = FastAPI()

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    process_time = perf_counter() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response

async def get_parameters(
    q: str | None = None,
    page: int = 1,
    limit: int = 100
) -> dict:
    return {'q': q, 'page': page, 'limit': limit}

ParametersDep = Annotated[dict, Depends(get_parameters)] 

class QueryParameters:
    def __init__(
        self,
        q: str | None = None,
        page: int = 1,
        limit: int = 100
    ):
        self.q = q
        self.page = page
        self.limit = limit

products_db = [
    {'product_name': 'Молоко'},
    {'product_name': 'Хлеб'},
    {'product_name': 'Телефон'},
    {'product_name': 'Куртка'}
]

@app.get('/products')
async def get_products(parameters: Annotated[QueryParameters, Depends()]):
    response = {}      
    if parameters.q:    
        response.update({'q': parameters.q})    
    products = products_db[parameters.page:parameters.page + parameters.limit]
    response.update({'products': products})     
    return response     

@app.get('/users')
async def get_users(parameters: ParametersDep):
    return parameters