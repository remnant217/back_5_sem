from fastapi import FastAPI 

app = FastAPI()
 
@app.get("/add")
async def add(a: int, b: int):
     return {"result": a + b}   # "result": a + b
 
@app.get("/subtract")
async def subtract(a: int, b: int): # a: int = int, b: int = int
     return {"result": a - b}
 
@app.get("/multiply")
async def multiply(a: int, b: int): # async def multiply(a: int, b: int):
     return {"result": a * b}  # return {"result": a * b}
 
@app.get("/divide")
async def divide(a: int, b: int):
    if b == 0:
         return {"error": "Ошибка деления на ноль!"}
    return {"result": a / b}    # a \ b
