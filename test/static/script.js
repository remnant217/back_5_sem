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

// Функция для обработки отправки сообщения
function handleSendMessage() {
    const userText = userInput.value.trim();
    if (userText === '' || isTyping) return;

    // 1) Показываем сообщение пользователя
    addMessage(userText, true);
    userInput.value = '';

    // 2) Включаем индикатор "бот печатает"
    isTyping = true;
    typingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // 3) Отправляем текст на сервер по WebSocket
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(userText);
    } else {
        // Фоллбек: если соединение не готово/закрыто
        isTyping = false;
        typingIndicator.style.display = 'none';
        addMessage('(Сервер недоступен. Попробуйте позже.)', false);
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

// Работа с веб-сокетом
const wsProtocol = location.protocol === 'https:' ? 'wss' : 'ws';
const ws = new WebSocket(`${wsProtocol}://${location.host}/ws`);

ws.addEventListener('message', (e) => {
    // Когда пришёл ответ от сервера - прячем индикатор и показываем сообщение бота
    if (isTyping) {
        isTyping = false;
        typingIndicator.style.display = 'none';
    }
    addMessage(e.data, false);
});