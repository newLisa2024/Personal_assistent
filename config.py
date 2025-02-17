import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RESUME_FILE_PATH = os.getenv("RESUME_FILE_PATH", "resume.txt")
