# Используем slim версию
FROM python:3.11-slim

# Отключаем предупреждение pip
ENV PIP_ROOT_USER_ACTION=ignore

# Рабочая директория
WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- ИСПРАВЛЕНИЕ: Копируем любой TTF файл ---
COPY *.ttf . 
# --------------------------------------------

# Копируем код бота
COPY . .

CMD ["python", "bot.py"]
