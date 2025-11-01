# подключаем asyncio для реализации задержки бота (1.5 секунды) и запуска фоновой задачи
import asyncio
# WebSocket - класс для работы с протоколом WebSocket в FastAPI
from fastapi import FastAPI, WebSocket
# подключаем класс StaticFiles для работы с файлами HTML, CSS и JS
from fastapi.staticfiles import StaticFiles
# подключаем класс RedirectResponse чтобы при обращении к / происходил редирект на /static/index.html
from fastapi.responses import RedirectResponse

app = FastAPI()

# подключаем обработчик статических файлов из папки /static
app.mount('/static', StaticFiles(directory='./static'), name='static')

# функция для ответа пользователю (также, как в script.js)
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

# корутина для имитации "Бот печатает..." и отправки ответа через WebSocket
async def process_and_reply(ws: WebSocket, text: str):
    # задержка печати в 1.5 секунды
    await asyncio.sleep(1.5)
    # send_text() - метод для отправки текстовых сообщений через WebSocket
    await ws.send_text(reply(text))

# обработка GET-запроса для перехода на страницу бота
@app.get('/')
def root():
    return RedirectResponse(url='/static/index.html')

# эндпоинт 
@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    # accept() - метод для начала работы WebSocket-соединения 
    await ws.accept()
    # открываем бесконечный цикл приема сообщений 
    # пока клиент подключен - будем читать и отвечать на сообщения
    try:
        while True:
            # receive_text() - метод, ожидающий получение текстового сообщения от клиента через WebSocket
            text = await ws.receive_text()
            # создаем фоновую задачу, так сервер может принимать новые сообщения
            asyncio.create_task(process_and_reply(ws, text))
    # ловим любые исключения (например, разрыв соединения) - освобождаем ресурсы и закрываем соединение
    except Exception:
        pass