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

# PostgreSQL database URL
# Формат: postgresql://username:password@host:port/database
# На Render будет автоматически предоставлена переменная DATABASE_URL
# Render использует postgres://, но asyncpg требует postgresql://
raw_database_url = os.getenv("DATABASE_URL")
if not raw_database_url:
    raise ValueError(
        "DATABASE_URL не установлен! Установите переменную окружения DATABASE_URL.\n"
        "Для локальной разработки создайте файл .env с DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
    )

# Конвертируем postgres:// в postgresql:// для asyncpg (Render использует postgres://)
DATABASE_URL = raw_database_url.replace("postgres://", "postgresql://", 1) if raw_database_url.startswith("postgres://") else raw_database_url
