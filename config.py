import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (если есть)
# На Render переменные будут браться из системных переменных окружения
load_dotenv()

# Получаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ADMIN_ID_STR = os.getenv("ADMIN_ID", "0")

# Проверка обязательных переменных окружения
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN не установлен! Установите переменную окружения BOT_TOKEN.\n"
        "Для локальной разработки создайте файл .env с BOT_TOKEN=your_token"
    )

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY не установлен! Установите переменную окружения GOOGLE_API_KEY.\n"
        "Для локальной разработки создайте файл .env с GOOGLE_API_KEY=your_key"
    )

# Преобразуем ADMIN_ID в число с обработкой ошибок
try:
    ADMIN_ID = int(ADMIN_ID_STR)
except ValueError:
    raise ValueError(
        f"ADMIN_ID должен быть числом, получено: {ADMIN_ID_STR}\n"
        "Установите переменную окружения ADMIN_ID с вашим Telegram User ID"
    )

DB_NAME = "bot_data.db"
