import codecs
from datetime import datetime, timedelta
from loguru import logger
from config import RESUME_FILE_PATH


def load_resume(file_path: str = RESUME_FILE_PATH) -> str:
    try:
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Ошибка загрузки резюме: {e}")
        return "Резюме недоступно."


def is_user_subscribed(bot, user_id: int, channel_username: str = "@PromptGuideElena") -> bool:  # Исправлен канал
    try:
        member = bot.get_chat_member(channel_username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False


def check_session_expired(user_context: dict, chat_id: int, expiration_minutes: int = 30) -> bool:
    if chat_id not in user_context:
        return True

    last_time_str = user_context[chat_id].get("last_message_time")
    if not last_time_str:
        return True

    try:
        last_time = datetime.fromisoformat(last_time_str)
        return (datetime.now() - last_time) > timedelta(minutes=expiration_minutes)
    except Exception as e:
        logger.error(f"Ошибка времени сессии: {e}")
        return True
