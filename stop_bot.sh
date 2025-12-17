#!/bin/bash

# Скрипт для корректной остановки бота

BOT_DIR="/Users/annaleodit/Documents/Code/Culture Card Bot"
PID_FILE="$BOT_DIR/bot.pid"
LOG_FILE="$BOT_DIR/bot.log"

cd "$BOT_DIR" || exit 1

echo "🛑 Остановка бота..."

# Функция для проверки, запущен ли процесс
is_running() {
    local pid=$1
    if ps -p "$pid" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Шаг 1: Остановка по PID файлу (graceful shutdown)
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if is_running "$PID"; then
        echo "📋 Найден процесс с PID: $PID"
        echo "Отправляю сигнал SIGTERM для graceful shutdown..."
        
        # Отправляем SIGTERM для корректной остановки
        kill -TERM "$PID" 2>/dev/null
        
        # Ждем до 10 секунд для graceful shutdown
        COUNTER=0
        while is_running "$PID" && [ $COUNTER -lt 10 ]; do
            sleep 1
            COUNTER=$((COUNTER + 1))
            echo -n "."
        done
        echo ""
        
        # Проверяем результат
        if is_running "$PID"; then
            echo "⚠️  Процесс не завершился gracefully, отправляю SIGKILL..."
            kill -KILL "$PID" 2>/dev/null
            sleep 1
        else
            echo "✅ Процесс корректно завершен"
        fi
    else
        echo "⚠️  Процесс с PID $PID не найден"
    fi
    
    # Удаляем PID файл
    rm -f "$PID_FILE"
    echo "🗑️  PID файл удален"
else
    echo "⚠️  PID файл не найден"
fi

# Шаг 2: Поиск и остановка всех процессов бота (на случай если PID файл был удален)
echo "🔍 Поиск всех процессов бота..."
BOT_PROCESSES=$(ps aux | grep -i "python.*bot.py" | grep -v grep | awk '{print $2}')

if [ -n "$BOT_PROCESSES" ]; then
    echo "Найдены процессы: $BOT_PROCESSES"
    for pid in $BOT_PROCESSES; do
        echo "Останавливаю процесс $pid..."
        kill -TERM "$pid" 2>/dev/null
        sleep 2
        
        # Если процесс все еще работает, убиваем принудительно
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "Принудительно завершаю процесс $pid..."
            kill -KILL "$pid" 2>/dev/null
            sleep 1
        fi
    done
else
    echo "✅ Других процессов бота не найдено"
fi

# Финальная проверка
REMAINING=$(ps aux | grep -i "python.*bot.py" | grep -v grep | wc -l | tr -d ' ')
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ Все процессы бота успешно остановлены"
    exit 0
else
    echo "⚠️  Внимание: осталось $REMAINING процесс(ов) бота"
    echo "Оставшиеся процессы:"
    ps aux | grep -i "python.*bot.py" | grep -v grep
    exit 1
fi
