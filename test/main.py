import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

# Отдаём статику (твой фронтенд)
app.mount("/static", StaticFiles(directory="./static"), name="static")

def reply(user_text: str) -> str:
    t = (user_text or "").lower()
    if "привет" in t or "здравствуй" in t:
        return "Привет! Как твои дела?"
    if "погода" in t:
        return "Я пока не умею смотреть погоду, но скоро научусь!"
    if "имя" in t:
        return "Меня зовут Ботти."
    if "пока" in t or "до свидания" in t:
        return "До встречи! Хорошего дня!"
    return "Я не совсем понял. Можешь переформулировать?"

async def process_and_reply(ws: WebSocket, text: str):
    await asyncio.sleep(1.5)  # минимальная «задержка печати»
    await ws.send_text(reply(text))

# Чтобы главная открывалась по корню "/"
@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            text = await ws.receive_text()
            asyncio.create_task(process_and_reply(ws, text))
    except WebSocketDisconnect:
        # соединение закрыто клиентом/сетевой ошибкой — просто выходим
        pass