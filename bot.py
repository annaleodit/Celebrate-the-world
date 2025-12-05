import logging
import asyncio
import os
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
import ai_service  # Твой файл генерации

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
    choosing_audience = State()
    choosing_topic = State()
    confirming_topic = State()

# --- KEYBOARD BUILDER (INLINE) ---
def make_inline_kb(items: dict, prefix: str, cols=2):
    """
    Создает инлайн клавиатуру.
    callback_data будет иметь вид "prefix:key" (например, "country:uae")
    """
    builder = []
    keys = list(items.keys())
    
    for i in range(0, len(keys), cols):
        row = []
        for key in keys[i:i + cols]:
            btn_text = items[key] # Например "🇦🇪 UAE"
            if isinstance(items[key], dict): # Если это словарь (для топиков)
                 btn_text = items[key]["btn"]
            
            row.append(InlineKeyboardButton(text=btn_text, callback_data=f"{prefix}:{key}"))
        builder.append(row)
        
    return InlineKeyboardMarkup(inline_keyboard=builder)

# --- HANDLERS: START ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await add_user(message.from_user.id, message.from_user.username)
    
    welcome_text = (
        "Hello! I'll help you congratulate your international colleagues "
        "in GCC with respect to their culture and traditions.\n\n"
        "Tap the button below to start!"
    )
    
    # Инлайн кнопка старта
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Start Creating", callback_data="start_flow")]
    ])
    
    await message.answer(welcome_text, reply_markup=kb)

# --- HANDLERS: FLOW (CALLBACKS) ---

# 1. Выбор страны
@dp.callback_query(F.data == "start_flow")
async def start_flow(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CardGen.choosing_country)
    
    # Редактируем старое сообщение, чтобы не спамить
    await callback.message.edit_text(
        "First, select the GCC country where you plan to send this greeting:",
        reply_markup=make_inline_kb(tc.COUNTRIES, prefix="country")
    )
    await callback.answer()

# 2. Обработка страны -> Выбор аудитории
@dp.callback_query(F.data.startswith("country:"))
async def country_chosen(callback: CallbackQuery, state: FSMContext):
    # Парсим данные из кнопки (например "country:uae" -> "uae")
    country_code = callback.data.split(":")[1]
    
    await state.update_data(country=country_code)
    await state.set_state(CardGen.choosing_audience)
    
    await callback.message.edit_text(
        f"Selected: {tc.COUNTRIES[country_code]}\n\n"
        "Now, who is this greeting for?",
        reply_markup=make_inline_kb(tc.AUDIENCES, prefix="audience", cols=1)
    )
    await callback.answer()

# 3. Обработка аудитории -> Показ советов и Выбор темы
@dp.callback_query(F.data.startswith("audience:"))
async def audience_chosen(callback: CallbackQuery, state: FSMContext):
    audience_code = callback.data.split(":")[1]
    data = await state.get_data()
    
    # Логика фильтрации топиков из text_content
    avail_topics_keys = tc.get_available_topics(audience_code)
    # Собираем словарь только из доступных топиков
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    
    # Советы эксперта
    tip_text = tc.get_tips(data['country'], audience_code)
    
    await state.update_data(audience=audience_code)
    await state.set_state(CardGen.choosing_topic)
    
    # Тут мы не можем просто сделать edit_text, если предыдущий текст был коротким, 
    # а TIPS длинные. Но попробуем. Если хочется сохранить историю советов, 
    # лучше отправить новое сообщение.
    # Но раз мы хотим инлайн стиль - редактируем.
    
    text_to_show = (
        f"🎯 Target: {tc.AUDIENCES[audience_code]}\n\n"
        f"{tip_text}\n\n"
        "👇 **Select a theme based on this advice:**"
    )
    
    await callback.message.edit_text(
        text_to_show,
        reply_markup=make_inline_kb(filtered_topics, prefix="topic", cols=2),
        parse_mode="Markdown"
    )
    await callback.answer()

# 4. Обработка темы -> Подтверждение
@dp.callback_query(F.data.startswith("topic:"))
async def topic_chosen(callback: CallbackQuery, state: FSMContext):
    topic_code = callback.data.split(":")[1]
    await state.update_data(topic=topic_code)
    
    desc = tc.TOPICS[topic_code]["desc"]
    topic_name = tc.TOPICS[topic_code]["btn"]
    
    # Кнопки "Назад" и "Генерировать"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Generate Card!", callback_data="do_generate")],
        [InlineKeyboardButton(text="⬅️ Back to Topics", callback_data="back_to_topics")]
    ])
    
    await state.set_state(CardGen.confirming_topic)
    
    await callback.message.edit_text(
        f"**Theme Selected:** {topic_name}\n\n"
        f"{desc}\n\n"
        "Ready to create art?",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    await callback.answer()

# 5. Кнопка "Назад к темам"
@dp.callback_query(F.data == "back_to_topics")
async def back_to_topics(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    avail_topics_keys = tc.get_available_topics(data['audience'])
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    
    await state.set_state(CardGen.choosing_topic)
    await callback.message.edit_text(
        "👇 **Select a theme:**",
        reply_markup=make_inline_kb(filtered_topics, prefix="topic", cols=2),
        parse_mode="Markdown"
    )
    await callback.answer()

# 6. ГЕНЕРАЦИЯ
@dp.callback_query(F.data == "do_generate")
async def generate_action(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Тут мы удаляем кнопки, чтобы пользователь не нажал дважды, и пишем статус
    await callback.message.edit_text("🎨 Mixing culture and AI art... Please wait...")
    
    final_prompt = tc.build_final_prompt(data['country'], data['audience'], data['topic'])
    
    # Вызов твоего ai_service
    image_io = await ai_service.generate_image_bytes(final_prompt)
    
    if image_io:
        file_bytes = image_io.getvalue()
        input_file = BufferedInputFile(file_bytes, filename="greeting_card.jpg")
        
        caption = (
            f"Here is your card for {tc.COUNTRIES[data['country']]}!\n"
            f"Topic: {tc.TOPICS[data['topic']]['btn']}\n\n"
            "Tap /start to create another one."
        )
        
        # Удаляем сообщение "Please wait..."
        await callback.message.delete()
        
        # Отправляем фото
        await bot.send_photo(chat_id=callback.message.chat.id, photo=input_file, caption=caption)
        await state.clear()
    else:
        await callback.message.edit_text("⚠️ Google AI API Error. Please try again later.")
        await state.clear()

# --- ADMIN HANDLERS ---
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        users = await get_all_users()
        await message.answer(f"📊 Total Users: {len(users)}")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            users = await get_all_users()
            msg = await message.answer("Starting broadcast...")
            count = 0
            for uid in users:
                try:
                    await bot.send_message(uid, parts[1])
                    count += 1
                    await asyncio.sleep(0.05)
                except: pass
            await msg.edit_text(f"✅ Broadcast done. Sent to {count} users.")

async def main():
    await init_db()
    # Удаляем вебхуки и старые апдейты
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
