# Используем slim версию для уменьшения размера образа
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Устанавливаем системные зависимости (если нужны для сборки некоторых пакетов)
# Для aiosqlite и стандартных либ обычно достаточно базового образа, 
# но иногда нужен gcc. Для надежности оставим.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Создаем папку для базы данных (опционально, но полезно для понимания структуры)
# На Render нужно будет монтировать Disk к пути /app/data если мы хотим менять путь
# Но так как мы пишем в корень (bot_data.db), Render Disk можно примонтировать в /app

# Команда запуска
CMD ["python", "bot.py"]
