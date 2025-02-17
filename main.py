from loguru import logger
import telebot
import openai

from config import TELEGRAM_API_KEY, OPENAI_API_KEY
from handlers import register_handlers

# Инициализируем клиента OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Инициализируем бота
bot = telebot.TeleBot(TELEGRAM_API_KEY)

# Передаем клиента в обработчики
user_context = register_handlers(bot, client)  # <-- Добавляем client

if __name__ == '__main__':
    logger.info("Бот запущен...")
    bot.polling(none_stop=True)

