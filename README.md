Personal Assistant Bot 🤖
Интеллектуальный ассистент, работающий через Telegram, с интеграцией OpenAI.

🔹 Описание
Этот проект представляет собой чат-бота, который выполняет роль персонального ассистента. Он умеет:
✅ Отвечать на вопросы с помощью GPT-4
✅ Обрабатывать команды и взаимодействовать с пользователем
✅ Анализировать текстовые данные
✅ Работать с файлами, включая resume.txt

🛠 Технологии
Python 3.12
OpenAI API
aiogram (Telegram Bot API)
Loguru (логирование)
Git (контроль версий)
⚡ Как запустить
1️⃣ Установить зависимости
Убедитесь, что у вас установлен Python 3.10+, затем выполните команду:

bash
Копировать
Редактировать
pip install -r requirements.txt
2️⃣ Создать .env файл
Создайте .env в корневой папке проекта и добавьте API-ключи:

ini
Копировать
Редактировать
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
RESUME_FILE_PATH=resume.txt
3️⃣ Запустить бота
bash
Копировать
Редактировать
python main.py
📁 Структура проекта
bash
Копировать
Редактировать
Personal_assistant/
│── .gitignore
│── config.py         # Конфигурация бота
│── handlers.py       # Основная логика обработки команд
│── main.py           # Точка входа
│── prompt.py         # Промпты и обработка диалогов
│── requirements.txt  # Зависимости
│── resume.txt        # Резюме пользователя (файл)
│── utils.py          # Вспомогательные функции
│── .env              # Файл с ключами (не загружается в Git)
🚀 Деплой
Бот может быть развернут на Amvera, Render, Heroku или Yandex Cloud.

Для деплоя на Amvera:

bash
Копировать
Редактировать
git push amvera main
📝 Контакты
Автор: Elena Loskutova
Telegram: @Elena_PromptLab
GitHub: newLisa2024
Email: loskutovaelena50@gmail.com
🔥 Если вам понравился проект, поставьте ⭐ на GitHub! 🚀
