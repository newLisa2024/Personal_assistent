# handlers.py
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import partial
import time  # <-- для пауз при повторных попытках
import telebot
import openai
from loguru import logger
from telebot import types
from typing import Dict, Any

from config import RESUME_FILE_PATH
from prompt import get_system_prompt
from utils import load_resume, is_user_subscribed, check_session_expired

# Пытаемся получить исключения из openai.error, если они существуют.
try:
    OpenAITimeout = openai.error.Timeout
    OpenAIApiError = openai.error.APIError
    OpenAIAuthError = openai.error.AuthenticationError
except AttributeError:
    # Если версия openai не содержит атрибутов error,
    # используем базовый класс Exception как запасной вариант.
    OpenAITimeout = Exception
    OpenAIApiError = Exception
    OpenAIAuthError = Exception


def register_handlers(bot: telebot.TeleBot, client: openai.OpenAI) -> Dict[int, Dict[str, Any]]:
    user_context: Dict[int, Dict[str, Any]] = {}

    def check_and_cache_subscription(chat_id: int) -> bool:
        """Проверяет и кеширует статус подписки пользователя"""
        try:
            if user_context[chat_id].get("subscribed") is None:
                is_subscribed = is_user_subscribed(bot, chat_id, "@PromptGuideElena")
                user_context[chat_id]["subscribed"] = is_subscribed

                if not is_subscribed:
                    bot.send_message(
                        chat_id,
                        "📌 Для продолжения подпишитесь на наш канал:\n"
                        "https://t.me/PromptGuideElena\n\n"
                        "После подписки отправьте любое сообщение для продолжения."
                    )
                    logger.info(f"Пользователь {chat_id} не подписан")
                else:
                    logger.info(f"Пользователь {chat_id} подписан")
            return user_context[chat_id]["subscribed"]
        except Exception as e:
            logger.error(f"Ошибка проверки подписки: {e}")
            return False

    def get_openai_response(chat_id: int, prompt: str) -> str:
        """
        Обработчик запросов к OpenAI с учётом контекста, с несколькими
        повторными попытками при таймаутах или API ошибках.
        """
        messages = user_context[chat_id]["messages"]
        messages.append({"role": "user", "content": prompt})

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1500,
                    timeout=20  # таймаут запроса к OpenAI (важно!)
                )
                response_text = response.choices[0].message.content
                messages.append({"role": "assistant", "content": response_text})
                return response_text

            except (OpenAITimeout, OpenAIApiError) as e:
                # Ошибка таймаута или внутренняя ошибка API
                logger.error(f"OpenAI Error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    return "Сервис временно недоступен. Попробуйте позже."

            except OpenAIAuthError as e:
                # Ошибка аутентификации (неверный ключ, запрет доступа и т.п.)
                logger.error(f"OpenAI Auth Error: {e}")
                return "Ошибка аутентификации. Пожалуйста, сообщите администратору."

            except Exception as e:
                # Любая другая непредвиденная ошибка
                logger.error(f"Unexpected error: {e}")
                return "Произошла непредвиденная ошибка. Попробуйте еще раз."

        return "Сервис временно недоступен. Попробуйте позже."

    def safe_message_processing(chat_id: int, message_text: str) -> str:
        """Безопасная обработка сообщений с таймаутом (ThreadPoolExecutor)"""
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    partial(get_openai_response, chat_id, message_text)
                )
                # Если get_openai_response не завершится за 20 секунд – будет TimeoutError
                return future.result(timeout=20)
        except TimeoutError:
            logger.error("Превышено время ожидания ответа OpenAI (ThreadPoolExecutor)")
            return "Время ответа превышено. Попробуйте задать вопрос короче."
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return "Ошибка обработки запроса."

    @bot.message_handler(commands=['start'])
    def start_conversation(message: types.Message):
        """Инициализация новой сессии"""
        chat_id = message.chat.id
        try:
            resume_content = load_resume()
            user_context[chat_id] = {
                "messages": [{"role": "system", "content": get_system_prompt(resume_content)}],
                "joke_count": 0,
                "question_count": 0,
                "subscribed": None,
                "last_message_time": datetime.now().isoformat()
            }

            welcome_text = (
                "Здравствуйте! 👋\n\n"
                "Я — персональный ассистент Елены Лоскутовой, эксперта по:\n"
                "• Нейросетям и AI-инструментам\n"
                "• Автоматизации бизнес-процессов\n"
                "• Разработке чат-ботов\n\n"
                "📌 Могу помочь:\n"
                "→ Подобрать решения для ваших задач\n"
                "→ Объяснить сложные технологии простым языком\n"
                "→ Создать прототип системы автоматизации\n\n"
                "⚠️ Обратите внимание:\n"
                "• Сессия длится 30 минут\n"
                "• Доступно 20 вопросов за сессию\n"
                "• Для продолжения требуется подписка на канал\n\n"
                "Чем могу помочь? 😊"
            )

            bot.send_message(
                chat_id,
                welcome_text,
                parse_mode='Markdown',
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.success(f"Новая сессия: {chat_id}")
        except Exception as e:
            logger.error(f"Ошибка старта сессии: {e}")
            bot.send_message(chat_id, "Ошибка инициализации. Попробуйте позже.")

    @bot.message_handler(func=lambda m: m.text.lower().strip() == "старт")
    def start_button_handler(message: types.Message):
        start_conversation(message)

    @bot.message_handler(func=lambda m: True)
    def handle_message(message: types.Message):
        """Основной обработчик сообщений"""
        chat_id = message.chat.id
        try:
            if chat_id not in user_context:
                start_conversation(message)
                return

            data = user_context[chat_id]

            if data["question_count"] >= 20:
                bot.send_message(
                    chat_id,
                    "⏳ Лимит вопросов исчерпан. Для продолжения:\n"
                    "• Напишите напрямую: @ElenaAIExpert\n"
                    "• Или начните новую сессию командой /start"
                )
                return

            if data["subscribed"] is None and not check_and_cache_subscription(chat_id):
                return

            if check_session_expired(user_context, chat_id):
                bot.send_message(chat_id, "⏳ Сессия истекла. Для продолжения нажмите /start")
                return

            data["question_count"] += 1
            user_context[chat_id]["last_message_time"] = datetime.now().isoformat()

            if data["question_count"] == 18:
                bot.send_message(chat_id, "ℹ️ Осталось 2 вопроса в этой сессии")

            if "анекдот" in message.text.lower():
                data["joke_count"] += 1
                response = safe_message_processing(
                    chat_id,
                    f"Расскажи профессиональный анекдот №{data['joke_count']} про IT"
                )
                bot.send_message(chat_id, response)
                return

            response_text = safe_message_processing(chat_id, message.text)
            bot.send_message(chat_id, response_text)
            logger.info(f"Ответ для {chat_id}: {response_text[:100]}...")

        except Exception as e:
            logger.critical(f"Критическая ошибка: {e}")
            bot.send_message(chat_id, "⚠️ Произошла техническая ошибка. Попробуйте позже.")

    return user_context

