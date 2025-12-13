import logging
import asyncio
import aiosqlite
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

# --- SETUP ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# --- DATABASE ---
async def init_db():
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(config.DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            return [row[0] for row in await cursor.fetchall()]

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
        builder.append([InlineKeyboardButton(text="В начало", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=builder)

# --- HANDLERS: START & FLOW ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await add_user(message.from_user.id, message.from_user.username)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Начать создание", callback_data="start_flow")]])
    await message.answer("Привет! Нажмите кнопку ниже, чтобы начать создание профессиональной поздравительной открытки.", reply_markup=kb)

@dp.callback_query(F.data == "start_flow")
async def start_flow(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CardGen.choosing_country)
    await callback.message.edit_text("Из какой страны получатель вашей открытки?", reply_markup=make_inline_kb(tc.COUNTRIES, prefix="country", add_cancel=True))
    await callback.answer()

@dp.callback_query(F.data.startswith("country:"))
async def country_chosen(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split(":")[1]
    await state.update_data(country=country_code)
    
    avail_topics_keys = tc.get_available_topics(country_code)
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    tip_text = tc.get_tips(country_code)
    
    await state.set_state(CardGen.choosing_topic)
    await callback.message.edit_text(f"Выбрано: {tc.COUNTRIES[country_code]}\n\n{tip_text}\n\n👇 **Выберите тему:**", reply_markup=make_inline_kb(filtered_topics, prefix="topic", cols=2, add_cancel=True), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("topic:"))
async def topic_chosen(callback: CallbackQuery, state: FSMContext):
    topic_code = callback.data.split(":")[1]
    await state.update_data(topic=topic_code)
    desc = tc.TOPICS[topic_code]["desc"]
    topic_name = tc.TOPICS[topic_code]["btn"]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить к тексту", callback_data="ask_for_text")],
        [InlineKeyboardButton(text="⬅️ Назад к темам", callback_data="back_to_topics")],
        [InlineKeyboardButton(text="В начало", callback_data="cancel")]
    ])
    await state.set_state(CardGen.confirming_topic)
    await callback.message.edit_text(f"**Выбрана тема:** {topic_name}\n\n{desc}\n\nПерейти к добавлению вашего персонального сообщения?", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_to_topics")
async def back_to_topics(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    avail_topics_keys = tc.get_available_topics(data['country'])
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    tip_text = tc.get_tips(data['country'])
    await state.set_state(CardGen.choosing_topic)
    await callback.message.edit_text(f"Выбрано: {tc.COUNTRIES[data['country']]}\n\n{tip_text}\n\n👇 **Выберите тему:**", reply_markup=make_inline_kb(filtered_topics, prefix="topic", cols=2, add_cancel=True), parse_mode="Markdown")
    await callback.answer()

# --- НОВЫЙ ЭТАП: ЗАПРОС ТЕКСТА ---

@dp.callback_query(F.data == "ask_for_text")
async def ask_for_text_action(callback: CallbackQuery, state: FSMContext):
    """Переводит бота в режим ожидания текста от пользователя."""
    data = await state.get_data()
    
    # Показываем предпросмотр выбранных параметров
    preview_text = (
        f"📋 **Предпросмотр параметров:**\n\n"
        f"🌍 Страна: {tc.COUNTRIES[data['country']]}\n"
        f"🎨 Тема: {tc.TOPICS[data['topic']]['btn']}\n\n"
        f"---\n\n"
        f"✍️ **Добавьте ваше персональное сообщение.**\n\n"
        f"Отправьте текст, который должен появиться на открытке (например, 'С Новым годом от [Название компании]').\n"
        f"Для лучшего вида сохраняйте текст кратким!\n\n"
        f"*Или нажмите Пропустить ниже.*"
    )
    
    await state.set_state(CardGen.waiting_for_text)
    
    # Кнопки: Пропустить и В начало
    skip_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Пропустить текст и создать", callback_data="skip_text")],
        [InlineKeyboardButton(text="В начало", callback_data="cancel")]
    ])
    
    await callback.message.edit_text(preview_text, reply_markup=skip_kb, parse_mode="Markdown")
    await callback.answer()

# --- ФИНАЛЬНАЯ ГЕНЕРАЦИЯ (С ТЕКСТОМ ИЛИ БЕЗ) ---

async def perform_generation(message: types.Message, state: FSMContext, user_text: str = None, retry_count: int = 0):
    """Общая функция для генерации и отправки, вызывается из двух хэндлеров ниже."""
    data = await state.get_data()
    max_retries = 2
    
    # Информируем пользователя о начале процесса
    status_msg = await message.answer("🎨 Создаю вашу профессиональную открытку... Это включает генерацию AI и графическую композицию. Пожалуйста, подождите (примерно 15-20 сек)...")
    
    # 1. Генерация AI картинки с retry
    final_prompt = tc.build_final_prompt(data['country'], data['topic'])
    ai_image_io = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                await status_msg.edit_text(f"🔄 Повторная попытка генерации изображения... (попытка {attempt + 1}/{max_retries + 1})")
                await asyncio.sleep(2)
            
            ai_image_io = await ai_service.generate_image_bytes(final_prompt)
            if ai_image_io:
                break
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
    await status_msg.edit_text("🖌️ Компоную финальный дизайн и применяю золотую рамку...")
    
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
            f"Вот ваша профессиональная открытка для {tc.COUNTRIES[data['country']]}!\n\n"
            f"Эта открытка была создана с помощью @culture_card_bot\n\n"
            f"Нажмите /start, чтобы создать еще одну."
        )
        
        # Кнопка "Начать заново"
        restart_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Создать еще одну", callback_data="start_flow")]
        ])
        
        await status_msg.delete()
        await bot.send_photo(chat_id=message.chat.id, photo=input_file, caption=caption, reply_markup=restart_kb)
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
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        users = await get_all_users()
        await message.answer(f"📊 Всего пользователей: {len(users)}")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            users = await get_all_users()
            msg = await message.answer("Начинаю рассылку...")
            count = 0
            for uid in users:
                try:
                    await bot.send_message(uid, parts[1])
                    count += 1
                    await asyncio.sleep(0.05)
                except: pass
            await msg.edit_text(f"✅ Рассылка завершена. Отправлено {count} пользователям.")

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
