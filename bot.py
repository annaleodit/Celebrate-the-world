import logging
import asyncio
import asyncpg
import json
import os
import sys
import random
import csv
import io
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery, 
    BufferedInputFile
)

# Импорты проекта
import config
import text_content as tc
import ai_service

# #region agent log
# Debug logging (опционально, только для локальной разработки)
DEBUG_LOG_ENABLED = os.getenv("DEBUG_LOG_ENABLED", "false").lower() == "true"
DEBUG_LOG_PATH = os.path.join(os.getcwd(), ".cursor", "debug.log") if DEBUG_LOG_ENABLED else None

def debug_log(location, message, data, hypothesis_id=None):
    """Логирование отладочной информации (только если включено)"""
    if not DEBUG_LOG_ENABLED or not DEBUG_LOG_PATH:
        return
    try:
        # Создаем директорию, если её нет
        log_dir = os.path.dirname(DEBUG_LOG_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass  # Игнорируем ошибки логирования
# #endregion

# --- SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# --- DATABASE ---
# Connection pool для PostgreSQL
db_pool: asyncpg.Pool = None

async def init_db():
    """Инициализация базы данных и создание connection pool"""
    global db_pool
    try:
        # Создаем connection pool
        db_pool = await asyncpg.create_pool(
            config.DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        
        # Создаем таблицу, если она не существует
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        logging.info("✅ База данных PostgreSQL инициализирована")
    except Exception as e:
        logging.error(f"❌ Ошибка инициализации базы данных: {e}")
        raise

async def close_db():
    """Закрытие connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logging.info("База данных закрыта")

async def add_user(user_id: int, username: str):
    """Добавление пользователя в базу данных"""
    if not db_pool:
        logging.error("Connection pool не инициализирован")
        return
    
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (user_id, username) VALUES ($1, $2) ON CONFLICT (user_id) DO NOTHING",
                user_id, username or None
            )
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя: {e}")

async def get_all_users():
    """Получение списка всех пользователей"""
    if not db_pool:
        logging.error("Connection pool не инициализирован")
        return []
    
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM users")
            return [row['user_id'] for row in rows]
    except Exception as e:
        logging.error(f"Ошибка при получении списка пользователей: {e}")
        return []

async def get_user_info(user_id: int):
    """Получение информации о конкретном пользователе"""
    if not db_pool:
        logging.error("Connection pool не инициализирован")
        return None
    
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT user_id, username, joined_at FROM users WHERE user_id = $1",
                user_id
            )
            return dict(row) if row else None
    except Exception as e:
        logging.error(f"Ошибка при получении информации о пользователе: {e}")
        return None

async def get_users_list(limit: int = 50, offset: int = 0):
    """Получение списка пользователей с пагинацией"""
    if not db_pool:
        logging.error("Connection pool не инициализирован")
        return []
    
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT user_id, username, joined_at FROM users ORDER BY joined_at DESC LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [dict(row) for row in rows]
    except Exception as e:
        logging.error(f"Ошибка при получении списка пользователей: {e}")
        return []

async def get_users_count():
    """Получение общего количества пользователей"""
    if not db_pool:
        logging.error("Connection pool не инициализирован")
        return 0
    
    try:
        async with db_pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM users")
            return count or 0
    except Exception as e:
        logging.error(f"Ошибка при получении количества пользователей: {e}")
        return 0

async def get_recent_users(days: int = 7):
    """Получение количества новых пользователей за последние N дней"""
    if not db_pool:
        logging.error("Connection pool не инициализирован")
        return 0
    
    try:
        async with db_pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE joined_at >= NOW() - make_interval(days => $1)",
                days
            )
            return count or 0
    except Exception as e:
        logging.error(f"Ошибка при получении новых пользователей: {e}")
        return 0

async def delete_user(user_id: int):
    """Удаление пользователя из базы данных"""
    if not db_pool:
        logging.error("Connection pool не инициализирован")
        return False
    
    try:
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE user_id = $1",
                user_id
            )
            return result == "DELETE 1"
    except Exception as e:
        logging.error(f"Ошибка при удалении пользователя: {e}")
        return False

# --- FSM STATES ---
class CardGen(StatesGroup):
    choosing_country = State()
    choosing_topic = State()
    confirming_topic = State()
    waiting_for_text = State()

# --- KEYBOARD BUILDER (INLINE) ---
def make_inline_kb(items: dict, prefix: str, cols=2, add_cancel=False):
    builder = []
    keys = list(items.keys())
    for i in range(0, len(keys), cols):
        row = []
        for key in keys[i:i + cols]:
            btn_text = items[key] if isinstance(items[key], str) else items[key]["btn"]
            row.append(InlineKeyboardButton(text=btn_text, callback_data=f"{prefix}:{key}"))
        builder.append(row)
    if add_cancel:
        builder.append([InlineKeyboardButton(text="🏠 В начало", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=builder)

def make_topics_kb(filtered_topics: dict, country_code: str):
    """Создает клавиатуру с темами и кнопкой 'Мне повезет' по 2 в ряд"""
    builder = []
    keys = list(filtered_topics.keys())
    cols = 2
    
    # Создаем строки с темами
    for i in range(0, len(keys), cols):
        row = []
        for key in keys[i:i + cols]:
            btn_text = filtered_topics[key]["btn"]
            row.append(InlineKeyboardButton(text=btn_text, callback_data=f"topic:{key}"))
        builder.append(row)
    
    # Добавляем "Мне повезет" в последнюю строку, если там есть место, иначе в новую строку
    if builder and len(builder[-1]) < cols:
        # Есть место в последней строке - добавляем туда
        builder[-1].append(InlineKeyboardButton(text="🍀 Мне повезет!", callback_data=f"lucky_topic:{country_code}"))
    else:
        # Нет места или builder пуст - создаем новую строку
        builder.append([InlineKeyboardButton(text="🍀 Мне повезет!", callback_data=f"lucky_topic:{country_code}")])
    
    # Добавляем кнопку "В начало"
    builder.append([InlineKeyboardButton(text="🏠 В начало", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=builder)

# --- HANDLERS: START & FLOW ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    # #region agent log
    debug_log("bot.py:93", "cmd_start ENTRY", {"user_id": message.from_user.id}, None)
    # #endregion
    await state.clear()
    await add_user(message.from_user.id, message.from_user.username)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Начать создание", callback_data="start_flow")]])
    await message.answer("Приветствуем! Нажмите кнопку ниже, чтобы начать создание поздравительной открытки, учитывающей культурные особенности разных стран!", reply_markup=kb)

@dp.callback_query(F.data == "start_flow")
async def start_flow(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CardGen.choosing_country)
    await callback.message.edit_text("Из какой страны получатель вашей открытки?", reply_markup=make_inline_kb(tc.COUNTRIES, prefix="country", add_cancel=True))
    await callback.answer()

@dp.callback_query(F.data.startswith("country:"))
async def country_chosen(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split(":")[1]
    # #region agent log
    debug_log("bot.py:88", "country_chosen ENTRY", {"country_code": country_code}, "D")
    # #endregion
    
    # Очищаем topic при смене страны (гипотеза D)
    await state.update_data(country=country_code, topic=None)
    
    avail_topics_keys = tc.get_available_topics(country_code)
    # #region agent log
    debug_log("bot.py:93", "get_available_topics RESULT", {"country": country_code, "available_topics": avail_topics_keys}, "A")
    # #endregion
    
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    
    # #region agent log
    state_data = await state.get_data()
    debug_log("bot.py:97", "country_chosen STATE AFTER UPDATE", {"state_data": state_data}, "D")
    # #endregion
    
    tip_text = tc.get_tips(country_code)
    
    await state.set_state(CardGen.choosing_topic)
    
    # Создаем клавиатуру с темами и кнопкой "Мне повезет" по 2 в ряд
    kb = make_topics_kb(filtered_topics, country_code)
    
    await callback.message.edit_text(f"**Выбор страны: {tc.COUNTRIES[country_code]}**\n\n{tip_text}\n\n👇 Выберите тему:", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("lucky_topic:"))
async def lucky_topic_chosen(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Мне повезет!' - случайный выбор темы"""
    try:
        country_code = callback.data.split(":")[1]
        
        # Проверяем валидность страны
        if country_code not in tc.COUNTRIES:
            await callback.answer("❌ Неверные параметры", show_alert=True)
            return
        
        # Получаем доступные темы для страны
        avail_topics = tc.get_available_topics(country_code)
        
        if not avail_topics:
            await callback.answer("❌ Нет доступных тем для этой страны", show_alert=True)
            return
        
        # Случайно выбираем тему
        random_topic = random.choice(avail_topics)
        
        # Сохраняем в state: topic="lucky" для отображения, lucky_topic для генерации
        await state.update_data(country=country_code, topic="lucky", lucky_topic=random_topic)
        await state.set_state(CardGen.waiting_for_text)
        
        # Показываем предпросмотр параметров
        topic_display = "Бот выберет тему случайным образом, вам точно повезет!"
        preview_text = (
            f"📋 Ваш выбор:\n\n"
            f"🌍 Страна — {tc.COUNTRIES[country_code]}\n"
            f"🎨 Тема — {topic_display}\n\n"
            f"---\n\n"
            f"✍️ Добавьте ваше персональное сообщение!\n\n"
            f"Отправьте боту текст на английском и он появится на открытке. Например: Happy and Prosperous New Year 2026!\n\n"
            f"Или выберите \"Использовать шаблон\" и бот сам подберет текст для вас!"
        )
        
        skip_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Использовать шаблон текста", callback_data="skip_text")],
            [InlineKeyboardButton(text="🏠 В начало", callback_data="cancel")]
        ])
        
        await callback.message.edit_text(preview_text, reply_markup=skip_kb, parse_mode="Markdown")
        await callback.answer("🍀 Тема выбрана случайным образом!")
    except Exception as e:
        logging.error(f"Ошибка в lucky_topic_chosen: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

@dp.callback_query(F.data.startswith("topic:"))
async def topic_chosen(callback: CallbackQuery, state: FSMContext):
    topic_code = callback.data.split(":")[1]
    # #region agent log
    debug_log("bot.py:133", "topic_chosen ENTRY", {"topic_code": topic_code}, "A")
    # #endregion
    
    state_data = await state.get_data()
    country_code = state_data.get('country')
    
    # #region agent log
    debug_log("bot.py:140", "topic_chosen STATE BEFORE VALIDATION", {"country": country_code, "topic": topic_code, "full_state": state_data}, "A")
    # #endregion
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Если country отсутствует, это ошибка состояния
    if not country_code:
        # #region agent log
        debug_log("bot.py:145", "topic_chosen COUNTRY MISSING", {"state_data": state_data}, "A")
        # #endregion
        await callback.answer("❌ Ошибка: страна не выбрана. Начните заново с /start", show_alert=True)
        await state.clear()
        return
    
    # ВАЛИДАЦИЯ: Проверяем, что тема доступна для выбранной страны (гипотеза A)
    avail_topics = tc.get_available_topics(country_code)
    # #region agent log
    debug_log("bot.py:152", "topic_chosen VALIDATION CHECK", {"country": country_code, "selected_topic": topic_code, "available_topics": avail_topics, "is_valid": topic_code in avail_topics}, "A")
    # #endregion
    
    if topic_code not in avail_topics:
        # #region agent log
        debug_log("bot.py:156", "topic_chosen VALIDATION FAILED", {"country": country_code, "invalid_topic": topic_code, "available_topics": avail_topics}, "A")
        # #endregion
        await callback.answer("❌ Эта тема недоступна для выбранной страны", show_alert=True)
        return
    
    # Сохраняем ОБА параметра одновременно для надежности
    await state.update_data(country=country_code, topic=topic_code)
    # #region agent log
    state_data_after = await state.get_data()
    debug_log("bot.py:165", "topic_chosen STATE AFTER UPDATE", {"state_data": state_data_after}, "A")
    # #endregion
    
    desc = tc.TOPICS[topic_code]["desc"]
    topic_name = tc.TOPICS[topic_code]["btn"]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить", callback_data="ask_for_text")],
        [InlineKeyboardButton(text="⬅️ Назад к темам", callback_data="back_to_topics")],
        [InlineKeyboardButton(text="🏠 В начало", callback_data="cancel")]
    ])
    await state.set_state(CardGen.confirming_topic)
    await callback.message.edit_text(f"**Выбрана тема:** {topic_name}\n\n{desc}\n\nПерейти к добавлению вашего персонального сообщения?", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_to_topics")
async def back_to_topics(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    country_code = data.get('country')
    
    # #region agent log
    debug_log("bot.py:180", "back_to_topics ENTRY", {"state_data": data}, "D")
    # #endregion
    
    # Дополнительная проверка безопасности
    if not country_code or country_code not in tc.COUNTRIES:
        await callback.answer("❌ Ошибка: страна не выбрана", show_alert=True)
        await state.clear()
        return
    
    # Очищаем topic при возврате к выбору тем (дополнительная защита)
    await state.update_data(topic=None)
    
    avail_topics_keys = tc.get_available_topics(country_code)
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    tip_text = tc.get_tips(country_code)
    await state.set_state(CardGen.choosing_topic)
    
    # Создаем клавиатуру с темами и кнопкой "Мне повезет" по 2 в ряд
    kb = make_topics_kb(filtered_topics, country_code)
    
    await callback.message.edit_text(f"**Выбор страны: {tc.COUNTRIES[country_code]}**\n\n{tip_text}\n\n👇 Выберите тему:", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

# --- НОВЫЙ ЭТАП: ЗАПРОС ТЕКСТА ---

@dp.callback_query(F.data == "ask_for_text")
async def ask_for_text_action(callback: CallbackQuery, state: FSMContext):
    """Переводит бота в режим ожидания текста от пользователя."""
    data = await state.get_data()
    country_code = data.get('country')
    topic_code = data.get('topic')
    
    # #region agent log
    debug_log("bot.py:192", "ask_for_text ENTRY", {"state_data": data}, "B")
    # #endregion
    
    # Дополнительная валидация перед переходом к тексту (защита от редких багов)
    if not country_code or country_code not in tc.COUNTRIES:
        await callback.answer("❌ Ошибка: страна не выбрана", show_alert=True)
        await state.clear()
        return
    
    # Если тема выбрана случайно, пропускаем валидацию темы
    if topic_code == "lucky":
        # Валидация не нужна для lucky темы
        pass
    elif not topic_code or topic_code not in tc.TOPICS:
        await callback.answer("❌ Ошибка: тема не выбрана", show_alert=True)
        await state.clear()
        return
    else:
        # Финальная проверка соответствия темы и страны
        avail_topics = tc.get_available_topics(country_code)
        if topic_code not in avail_topics:
            # #region agent log
            debug_log("bot.py:297", "ask_for_text VALIDATION FAILED", {"country": country_code, "invalid_topic": topic_code, "available_topics": avail_topics}, "B")
            # #endregion
            await callback.answer("❌ Тема не соответствует выбранной стране", show_alert=True)
            await state.clear()
            return
    
    # Показываем предпросмотр выбранных параметров
    # Проверяем, выбрана ли тема случайным образом (помечаем специальным значением)
    is_lucky = topic_code == "lucky"
    topic_display = "Бот выберет тему случайным образом, вам точно повезет!" if is_lucky else tc.TOPICS[topic_code]['btn']
    
    preview_text = (
        f"📋 Ваш выбор:\n\n"
        f"🌍 Страна — {tc.COUNTRIES[country_code]}\n"
        f"🎨 Тема — {topic_display}\n\n"
        f"---\n\n"
        f"✍️ Добавьте ваше персональное сообщение!\n\n"
        f"Отправьте боту текст на английском и он появится на открытке. Например: Happy and Prosperous New Year 2026!\n\n"
        f"Или нажмите Пропустить и бот сам подберет текст для вас!"
    )
    
    await state.set_state(CardGen.waiting_for_text)
    
    # Кнопки: Пропустить и В начало
    skip_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Использовать шаблон текста", callback_data="skip_text")],
        [InlineKeyboardButton(text="🏠 В начало", callback_data="cancel")]
    ])
    
    await callback.message.edit_text(preview_text, reply_markup=skip_kb, parse_mode="Markdown")
    await callback.answer()

# --- ФИНАЛЬНАЯ ГЕНЕРАЦИЯ (С ТЕКСТОМ ИЛИ БЕЗ) ---

async def perform_generation(message: types.Message, state: FSMContext, user_text: str = None, retry_count: int = 0):
    """Общая функция для генерации и отправки, вызывается из двух хэндлеров ниже."""
    data = await state.get_data()
    # #region agent log
    debug_log("bot.py:263", "perform_generation ENTRY", {"state_data": data, "user_text_length": len(user_text) if user_text else 0}, "B")
    # #endregion
    
    country_code = data.get('country')
    topic_code = data.get('topic')
    
    # Если тема выбрана случайно, используем реальную тему для генерации
    if topic_code == "lucky":
        topic_code = data.get('lucky_topic')
        if not topic_code:
            await message.answer("❌ Ошибка: случайная тема не была выбрана. Начните заново с /start")
            await state.clear()
            return
    
    # #region agent log
    debug_log("bot.py:370", "perform_generation BEFORE VALIDATION", {"country": country_code, "topic": topic_code}, "B")
    # #endregion
    
    # КРИТИЧЕСКАЯ ПРОВЕРКА: Оба параметра обязательны
    if not country_code or not topic_code:
        # #region agent log
        debug_log("bot.py:275", "perform_generation MISSING PARAMS", {"country": country_code, "topic": topic_code}, "B")
        # #endregion
        await message.answer(
            f"⚠️ **Ошибка: отсутствуют параметры**\n\n"
            f"Страна: {'выбрана' if country_code else 'НЕ выбрана'}\n"
            f"Тема: {'выбрана' if topic_code else 'НЕ выбрана'}\n\n"
            f"Пожалуйста, начните заново командой /start"
        )
        await state.clear()
        return
    
    # ВАЛИДАЦИЯ: Проверяем соответствие topic и country перед генерацией (гипотеза B)
    avail_topics = tc.get_available_topics(country_code)
    # #region agent log
    debug_log("bot.py:287", "perform_generation VALIDATION CHECK", {"country": country_code, "topic": topic_code, "available_topics": avail_topics, "is_valid": topic_code in avail_topics}, "B")
    # #endregion
    
    if topic_code not in avail_topics:
        # #region agent log
        debug_log("bot.py:291", "perform_generation VALIDATION FAILED", {"country": country_code, "invalid_topic": topic_code, "available_topics": avail_topics}, "B")
        # #endregion
        await message.answer(
            f"⚠️ **Ошибка валидации**\n\n"
            f"Тема '{tc.TOPICS.get(topic_code, {}).get('btn', topic_code)}' недоступна для страны {tc.COUNTRIES.get(country_code, country_code)}.\n"
            f"Пожалуйста, начните заново командой /start"
        )
        await state.clear()
        return
    
    max_retries = 2
    
    # Информируем пользователя о начале процесса
    status_msg = await message.answer("🎨 Создаю вашу открытку с помощью AI и с учетом культурных особенностей страны... Пожалуйста, подождите 15-20 секунд.")
    
    # 1. Генерация AI картинки с retry
    # #region agent log
    debug_log("bot.py:190", "build_final_prompt CALL", {"country": country_code, "topic": topic_code}, "C")
    # #endregion
    final_prompt = tc.build_final_prompt(country_code, topic_code)
    ai_image_io = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                await status_msg.edit_text(f"🔄 Повторная попытка генерации изображения... (попытка {attempt + 1}/{max_retries + 1})")
                await asyncio.sleep(2)
            
            ai_image_io = await ai_service.generate_image_bytes(final_prompt)
            if ai_image_io:
                break
            elif attempt < max_retries:
                logging.warning(f"Генерация вернула None, попытка {attempt + 1}/{max_retries + 1}")
                continue
        except asyncio.TimeoutError:
            logging.error(f"Timeout при генерации изображения (попытка {attempt + 1})")
            if attempt == max_retries:
                await status_msg.edit_text(
                    "⚠️ **Превышено время ожидания**\n\n"
                    "Генерация изображения заняла слишком много времени.\n"
                    "Возможные причины:\n"
                    "• Перегрузка API Google Gemini\n"
                    "• Слишком сложный запрос\n"
                    "• Проблемы с интернет-соединением\n\n"
                    "Попробуйте позже или начните заново командой /start"
                )
                await state.clear()
                return
        except Exception as e:
            logging.error(f"Ошибка генерации изображения (попытка {attempt + 1}): {e}")
            if attempt == max_retries:
                await status_msg.edit_text(
                    "⚠️ **Ошибка генерации изображения**\n\n"
                    "К сожалению, не удалось создать изображение. Возможные причины:\n"
                    "• Проблемы с API Google Gemini\n"
                    "• Превышен лимит запросов\n"
                    "• Нестабильное интернет-соединение\n\n"
                    "Попробуйте позже или начните заново командой /start"
                )
                await state.clear()
                return
    
    if not ai_image_io:
        await status_msg.edit_text(
            "⚠️ **Ошибка генерации изображения**\n\n"
            "Не удалось создать изображение после нескольких попыток.\n"
            "Попробуйте позже или начните заново командой /start"
        )
        await state.clear()
        return

    # 2. Сборка финальной открытки (Холст + AI + Текст + Рамка)
    # Убрали сообщение про компоновку - оно мелькает слишком быстро
    
    try:
        final_card_io = await ai_service.compose_final_card(ai_image_io, user_text)
    except Exception as e:
        logging.error(f"Ошибка композиции открытки: {e}")
        await status_msg.edit_text(
            "⚠️ **Ошибка при создании открытки**\n\n"
            "Не удалось собрать финальную композицию.\n"
            "Попробуйте позже или начните заново командой /start"
        )
        await state.clear()
        return
    
    if final_card_io:
        file_bytes = final_card_io.getvalue()
        # Важно: отправляем как фото, чтобы телеграм показал превью
        input_file = BufferedInputFile(file_bytes, filename="greeting_card.jpg")
        
        caption = (
            f"Ваша открытка готова!\n"
            f"Страна получателя: {tc.COUNTRIES[data['country']]}!\n"
            f"Нажмите /start, чтобы начать процесс заново.\n\n"
            f"---\n\n"
            f"🪄 Эта открытка была создана с помощью @celebrate_the_world_bot"
        )
        
        # Сохраняем страну для быстрого создания еще одной открытки
        country_code = data.get('country')
        
        # Кнопка "Создать еще одну" - возврат к выбору темы для той же страны
        restart_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Создать еще одну", callback_data=f"create_another:{country_code}")]
        ])
        
        await status_msg.delete()
        await bot.send_photo(chat_id=message.chat.id, photo=input_file, caption=caption, reply_markup=restart_kb)
        
        # НЕ очищаем state сразу - он нужен для кнопки "Создать еще одну"
        # State будет очищен при следующем /start или в create_another
    else:
        await status_msg.edit_text(
            "⚠️ **Ошибка при создании открытки**\n\n"
            "Не удалось собрать финальную композицию.\n"
            "Попробуйте позже или начните заново командой /start"
        )
        await state.clear()

# Хэндлер 1: Пользователь прислал текст
@dp.message(CardGen.waiting_for_text, F.text)
async def text_received(message: types.Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer(
            f"⚠️ Ваш текст слишком длинный ({len(message.text)} символов).\n"
            "Пожалуйста, ограничьтесь 200 символами для лучшего дизайна.\n\n"
            "Попробуйте отправить более короткую версию:"
        )
        return
    # Вызываем общую функцию с полученным текстом
    await perform_generation(message, state, user_text=message.text)

# Хэндлер 2: Пользователь нажал "Skip Text"
@dp.callback_query(CardGen.waiting_for_text, F.data == "skip_text")
async def skip_text_action(callback: CallbackQuery, state: FSMContext):
    # --- ОБНОВЛЕННЫЙ ТЕКСТ ПО УМОЛЧАНИЮ ---
    default_text = "Season's Greetings and best wishes for a prosperous and successful New Year!"
    
    # Вызываем генерацию с этим текстом
    await perform_generation(callback.message, state, user_text=default_text)
    await callback.answer()

# --- БЫСТРОЕ СОЗДАНИЕ ЕЩЕ ОДНОЙ ОТКРЫТКИ ---
@dp.callback_query(F.data.startswith("create_another:"))
async def create_another_action(callback: CallbackQuery, state: FSMContext):
    """Быстрое создание еще одной открытки - возврат к выбору темы для той же страны"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 2:
            await callback.answer("❌ Ошибка параметров", show_alert=True)
            return
        
        country_code = parts[1]
        
        # #region agent log
        debug_log("bot.py:427", "create_another ENTRY", {"country_code": country_code}, "E")
        # #endregion
        
        # Проверяем валидность страны
        if country_code not in tc.COUNTRIES:
            await callback.answer("❌ Неверные параметры", show_alert=True)
            return
        
        # Восстанавливаем состояние с выбранной страной, ОЧИЩАЕМ topic (гипотеза E)
        await state.update_data(country=country_code, topic=None)
        # #region agent log
        state_data = await state.get_data()
        debug_log("bot.py:447", "create_another STATE AFTER UPDATE", {"state_data": state_data}, "E")
        # #endregion
        await state.set_state(CardGen.choosing_topic)
        
        # Показываем выбор тем для этой страны
        avail_topics_keys = tc.get_available_topics(country_code)
        filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
        tip_text = tc.get_tips(country_code)
        
        # Создаем клавиатуру с темами и кнопкой "Мне повезет" по 2 в ряд
        kb = make_topics_kb(filtered_topics, country_code)
        
        # ИСПРАВЛЕНИЕ: Нельзя редактировать фото через edit_text()
        # Просто отправляем новое текстовое сообщение с выбором тем
        await callback.message.answer(
            f"**Выбор страны: {tc.COUNTRIES[country_code]}**\n\n{tip_text}\n\n👇 Выберите тему:",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка в create_another: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

# --- ОБРАБОТКА ОТМЕНЫ ---
@dp.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Создание открытки остановлено.\n\n"
        "Нажмите /start, чтобы начать заново."
    )
    await callback.answer()

# --- ADMIN & MAIN ---

def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id == config.ADMIN_ID

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Главное меню администратора"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    admin_menu = (
        "🔐 **Панель администратора**\n\n"
        "Доступные команды:\n\n"
        "📊 `/stats` - Статистика пользователей\n"
        "👥 `/users` - Выгрузка CSV файла со всеми пользователями\n"
        "🔍 `/user_info <user_id>` - Информация о пользователе\n"
        "🗑️ `/delete_user <user_id>` - Удалить пользователя\n"
        "📢 `/broadcast <сообщение>` - Рассылка сообщений\n"
        "💾 `/db_stats` - Статистика базы данных\n"
        "❓ `/help_admin` - Показать это меню"
    )
    await message.answer(admin_menu, parse_mode="Markdown")

@dp.message(Command("help_admin"))
async def cmd_help_admin(message: types.Message):
    """Справка по админским командам"""
    await cmd_admin(message)

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Расширенная статистика пользователей"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    try:
        total_users = await get_users_count()
        new_users_today = await get_recent_users(1)
        new_users_week = await get_recent_users(7)
        new_users_month = await get_recent_users(30)
        
        stats_text = (
            f"📊 **Статистика пользователей**\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"🆕 Новых сегодня: {new_users_today}\n"
            f"📅 Новых за неделю: {new_users_week}\n"
            f"📆 Новых за месяц: {new_users_month}"
        )
        await message.answer(stats_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка в cmd_stats: {e}")
        await message.answer("❌ Ошибка при получении статистики.")

@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    """Выгрузка CSV файла со всеми пользователями"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    try:
        # Получаем всех пользователей (без лимита)
        if not db_pool:
            await message.answer("❌ База данных не инициализирована.")
            return
        
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT user_id, username, joined_at FROM users ORDER BY joined_at DESC"
            )
            users = [dict(row) for row in rows]
        
        total_users = len(users)
        
        if not users:
            await message.answer("📋 Пользователи не найдены.")
            return
        
        # Создаем CSV файл в памяти
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        
        # Записываем заголовки
        csv_writer.writerow(['user_id', 'username', 'joined_at'])
        
        # Записываем данные
        for user in users:
            user_id = user['user_id']
            username = user['username'] or ''
            joined_at = user['joined_at'].strftime("%Y-%m-%d %H:%M:%S") if user['joined_at'] else ''
            csv_writer.writerow([user_id, username, joined_at])
        
        # Конвертируем в bytes для отправки
        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')  # utf-8-sig для правильного отображения в Excel
        csv_buffer.close()
        
        # Создаем файл для отправки
        input_file = BufferedInputFile(
            csv_bytes,
            filename=f"users_export_{total_users}.csv"
        )
        
        await message.answer(
            f"📊 **Выгрузка пользователей**\n\n"
            f"✅ Всего пользователей: {total_users}\n"
            f"📁 Файл готов к скачиванию",
            parse_mode="Markdown"
        )
        await bot.send_document(
            chat_id=message.chat.id,
            document=input_file,
            caption=f"📋 Список всех пользователей ({total_users} записей)"
        )
    except Exception as e:
        logging.error(f"Ошибка в cmd_users: {e}", exc_info=True)
        await message.answer("❌ Ошибка при выгрузке списка пользователей.")

@dp.message(Command("user_info"))
async def cmd_user_info(message: types.Message):
    """Информация о конкретном пользователе"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: `/user_info <user_id>`", parse_mode="Markdown")
            return
        
        user_id = int(parts[1])
        user_info = await get_user_info(user_id)
        
        if not user_info:
            await message.answer(f"❌ Пользователь с ID `{user_id}` не найден.", parse_mode="Markdown")
            return
        
        username = user_info['username'] or "не указан"
        joined_at = user_info['joined_at'].strftime("%d.%m.%Y %H:%M:%S") if user_info['joined_at'] else "неизвестно"
        
        info_text = (
            f"👤 **Информация о пользователе**\n\n"
            f"🆔 ID: `{user_info['user_id']}`\n"
            f"👤 Username: @{username}\n"
            f"📅 Дата регистрации: {joined_at}"
        )
        await message.answer(info_text, parse_mode="Markdown")
    except ValueError:
        await message.answer("❌ Неверный формат user_id. Используйте число.")
    except Exception as e:
        logging.error(f"Ошибка в cmd_user_info: {e}")
        await message.answer("❌ Ошибка при получении информации о пользователе.")

@dp.message(Command("delete_user"))
async def cmd_delete_user(message: types.Message):
    """Удаление пользователя из базы данных"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: `/delete_user <user_id>`", parse_mode="Markdown")
            return
        
        user_id = int(parts[1])
        
        # Проверяем, существует ли пользователь
        user_info = await get_user_info(user_id)
        if not user_info:
            await message.answer(f"❌ Пользователь с ID `{user_id}` не найден.", parse_mode="Markdown")
            return
        
        # Удаляем пользователя
        success = await delete_user(user_id)
        
        if success:
            username = user_info['username'] or "без username"
            await message.answer(
                f"✅ Пользователь удален:\n"
                f"🆔 ID: `{user_id}`\n"
                f"👤 @{username}",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Ошибка при удалении пользователя.")
    except ValueError:
        await message.answer("❌ Неверный формат user_id. Используйте число.")
    except Exception as e:
        logging.error(f"Ошибка в cmd_delete_user: {e}")
        await message.answer("❌ Ошибка при удалении пользователя.")

@dp.message(Command("db_stats"))
async def cmd_db_stats(message: types.Message):
    """Статистика базы данных"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    try:
        total_users = await get_users_count()
        new_users_today = await get_recent_users(1)
        new_users_week = await get_recent_users(7)
        new_users_month = await get_recent_users(30)
        
        # Получаем информацию о самой старой и новой регистрации
        if db_pool:
            async with db_pool.acquire() as conn:
                oldest_user = await conn.fetchrow(
                    "SELECT user_id, username, joined_at FROM users ORDER BY joined_at ASC LIMIT 1"
                )
                newest_user = await conn.fetchrow(
                    "SELECT user_id, username, joined_at FROM users ORDER BY joined_at DESC LIMIT 1"
                )
        else:
            oldest_user = None
            newest_user = None
        
        stats_text = (
            f"💾 **Статистика базы данных**\n\n"
            f"👥 Всего пользователей: {total_users}\n\n"
            f"📈 **Новые регистрации:**\n"
            f"   Сегодня: {new_users_today}\n"
            f"   За неделю: {new_users_week}\n"
            f"   За месяц: {new_users_month}\n\n"
        )
        
        if oldest_user and newest_user:
            oldest_date = oldest_user['joined_at'].strftime("%d.%m.%Y") if oldest_user['joined_at'] else "неизвестно"
            newest_date = newest_user['joined_at'].strftime("%d.%m.%Y") if newest_user['joined_at'] else "неизвестно"
            stats_text += (
                f"📅 **Период:**\n"
                f"   Первая регистрация: {oldest_date}\n"
                f"   Последняя регистрация: {newest_date}"
            )
        
        await message.answer(stats_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка в cmd_db_stats: {e}")
        await message.answer("❌ Ошибка при получении статистики базы данных.")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    """Рассылка сообщений всем пользователям"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ Использование: `/broadcast <сообщение>`\n\n"
            "Пример: `/broadcast Привет всем! Это тестовая рассылка.`",
            parse_mode="Markdown"
        )
        return
    
    users = await get_all_users()
    if not users:
        await message.answer("❌ Нет пользователей для рассылки.")
        return
    
    msg = await message.answer(f"📢 Начинаю рассылку для {len(users)} пользователей...")
    count = 0
    failed = 0
    
    for uid in users:
        try:
            await bot.send_message(uid, parts[1])
            count += 1
            await asyncio.sleep(0.05)  # Задержка, чтобы не превысить лимиты Telegram
        except Exception as e:
            failed += 1
            logging.warning(f"Не удалось отправить сообщение пользователю {uid}: {e}")
    
    await msg.edit_text(
        f"✅ **Рассылка завершена**\n\n"
        f"✅ Успешно: {count}\n"
        f"❌ Ошибок: {failed}\n"
        f"📊 Всего: {len(users)}",
        parse_mode="Markdown"
    )

async def main():
    """Основная функция запуска бота"""
    try:
        await init_db()
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("🚀 Бот запущен и готов к работе")
        await dp.start_polling(bot, handle_as_tasks=True)
    except asyncio.CancelledError:
        logging.info("Получен сигнал остановки...")
    except Exception as e:
        logging.error(f"Ошибка в main(): {e}", exc_info=True)
        raise
    finally:
        logging.info("Завершаю работу бота...")
        try:
            await close_db()
        except Exception as e:
            logging.error(f"Ошибка при закрытии базы данных: {e}")
        try:
            await bot.session.close()
        except Exception as e:
            logging.error(f"Ошибка при закрытии сессии: {e}")

if __name__ == "__main__":
    try:
        # asyncio.run() правильно обрабатывает SIGINT и SIGTERM
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Получен KeyboardInterrupt - завершаю работу")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logging.info("Бот завершил работу")
