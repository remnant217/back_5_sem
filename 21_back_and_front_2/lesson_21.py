# Интеграция с фронтендом 2

# Реализация чат-бота через WebSocket

# Задание № 1 - выстроить архитектуру проекта

'''
new_bot/
├─ main.py
└─ static/
   ├─ index.html
   ├─ style.css
   └─ script.js
'''

# Задание № 2 - реализовать файл main.py

# подключаем asyncio для реализации задержки бота (1.5 секунды) и запуска фоновой задачи
import asyncio
# WebSocket - класс для работы с протоколом WebSocket в FastAPI
# WebSocketDisconnect - класс для обработки разрыва WebSocket-соединений
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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

# эндпоинт для работы с WebSocket-соединение
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
    # ловим WebSocketDisconnect (клиент покинул чат) - освобождаем ресурсы и закрываем соединение
    except WebSocketDisconnect:
        pass

# Задание № 3 - модифицировать файл index.html

'''
Теперь подправим файл index.html, в данном коде:
<link rel="stylesheet" href="style.css">
<script src="script.js"></script>

укажем папку /static для корректной работе ссылок:
<link rel="stylesheet" href="/static/style.css">
<script src="/static/script.js"></script>
'''

# Задание № 4 - модифицировать файл script.js

'''
Итак, перейдем к модификации файла script.js:
1) Удалим строчку let typingTimer = null; - раньше задержка ответа была на стороне фронтенда,
теперь же она на стороне сервера.

2) Полностью удаляем функцию function getBotResponse(userText) - раньше логика ответа бота была на стороне фронтенда,
теперь же она на стороне сервера.

3) Добавляем минимальный JS-код для работы с WebSocket:
// Работа с веб-сокетом
// Если текущий сайт открыт по протоколу https - выбирается wss, иначе простой ws
const wsProtocol = location.protocol === 'https:' ? 'wss' : 'ws';
// Создаем новое WebSocket-соединение через шаблон <ws|wss>://<хост и порт текущей страницы>/ws
// В location.host лежит localhost:8000
const ws = new WebSocket(`${wsProtocol}://${location.host}/ws`);
// Ожидаем событие message - оно появляется, когда сервер прислал фрейм с данными
// e - событие с полезными данными
ws.addEventListener('message', (e) => {
    // Когда пришел ответ от сервера - прячем индикатор "Бот печатает..."
    if (isTyping) {
        isTyping = false;
        typingIndicator.style.display = 'none';
    }
    // Показываем сообщение бота, e.data содержит текст ответа бота
    // Ставим false, показывая, что сообщение от бота, а не от пользователя
    addMessage(e.data, false);
});

4) В функции function handleSendMessage() удаляем конструкцию
    if (typingTimer) {
        clearTimeout(typingTimer);
    }
Логика работы с таймером задержки теперь на бэкенде.

5) Также внутри функции function handleSendMessage() убираем функцию typingTimer = setTimeout(() => 
в текущем виде - вместо нее пишем проверку - если WebSocket-соединение открыто, то отправляем текст
пользователя на сервер. Если же соединение не готово или закрыто - прячем индикатор "Бот печатает..."
и Отправляем сообщение о недоступности сервера:
// 3) Отправляем текст на сервер по WebSocket
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(userText);
    // Если соединение не готово или закрыто
    } else {
        // Прячем индикатор "Бот печатает..."
        isTyping = false;
        typingIndicator.style.display = 'none';
        // Отправляем сообщение о недоступности сервера
        addMessage('Сервер недоступен. Попробуйте позже.', false);
    }

6) Финальная правка - в функции function clearChatHistory() убираем все, что связано с typingTimer
и оставляем только скрытие индикатор "Бот печатает...":
// Функция для очистки истории чата
function clearChatHistory() {
    // Скрываем индикатор, если был
    if (isTyping) {
        isTyping = false;
        typingIndicator.style.display = 'none';
    }

'''