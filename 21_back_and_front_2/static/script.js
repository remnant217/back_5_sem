// Получаем элементы DOM
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const typingIndicator = document.getElementById('typing-indicator');
const clearChatButton = document.getElementById('clear-chat');

// Переменные для управления состоянием
let isTyping = false;

// Функция для добавления сообщения в чат
function addMessage(text, isUser) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(isUser ? 'user-message' : 'bot-message');

    // Аватарки - используем разные иконки для пользователя и бота
    const userAvatar = 'https://cdn-icons-png.flaticon.com/512/847/847969.png';
    const botAvatar = 'https://cdn-icons-png.flaticon.com/512/4712/4712039.png';

    messageElement.innerHTML = `
        <img src="${isUser ? userAvatar : botAvatar}" alt="${isUser ? 'Пользователь' : 'Бот'}" class="message-avatar">
        <div class="message-text">${text}</div>
    `;

    chatMessages.appendChild(messageElement);

    // Прокручиваем чат вниз к новому сообщению
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

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

// Функция для обработки отправки сообщения
function handleSendMessage() {
    const userText = userInput.value.trim();

    if (userText === '' || isTyping) return; // Игнорируем пустые сообщения и если бот "печатает"

    // 1. Добавляем сообщение пользователя
    addMessage(userText, true);
    userInput.value = ''; // Очищаем поле ввода

    // 2. Показываем индикатор "печатает"
    isTyping = true;
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight; // Прокручиваем к индикатору

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
}

// Функция для очистки истории чата
function clearChatHistory() {
    // Скрываем индикатор, если был
    if (isTyping) {
        isTyping = false;
        typingIndicator.style.display = 'none';
    }

    // Сохраняем только первое приветственное сообщение бота (если оно есть)
    const welcomeMessage = chatMessages.querySelector('.bot-message');
    chatMessages.innerHTML = '';
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage);
    }
}

// Обработчики событий
sendButton.addEventListener('click', handleSendMessage);

// Отправка сообщения по нажатию Enter
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});

// Очистка истории чата
clearChatButton.addEventListener('click', clearChatHistory);