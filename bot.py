import logging
import asyncio
import os
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

# Импорты проекта
import config
import text_content as tc
import ai_service  # <--- Подключаем модуль генерации

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

# --- KEYBOARDS ---
def make_kb(items: dict, cols=2):
    buttons = [KeyboardButton(text=val) for val in items.values()]
    grid = [buttons[i:i + cols] for i in range(0, len(buttons), cols)]
    return ReplyKeyboardMarkup(keyboard=grid, resize_keyboard=True, one_time_keyboard=True)

def get_key_by_value(d, value):
    for k, v in d.items():
        if v == value:
            return k
    return None

# --- HANDLERS: ADMIN ---
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    users = await get_all_users()
    await message.answer(f"📊 Total Users: {len(users)}")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /broadcast <message>")
        return
    text = parts[1]
    users = await get_all_users()
    count = 0
    for uid in users:
        try:
            await bot.send_message(uid, text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"✅ Broadcast sent to {count} users.")

# --- HANDLERS: FLOW ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await add_user(message.from_user.id, message.from_user.username)
    welcome_text = (
        "Hello! I'll help you congratulate your international colleagues, "
        "partners and friends in GCC with respect to their culture and traditions, "
        "while keeping a creative vibe.\n\n"
        "Tap Start below!"
    )
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Start Creating")]], resize_keyboard=True)
    await message.answer(welcome_text, reply_markup=kb)

@dp.message(F.text == "Start Creating")
async def start_flow(message: types.Message, state: FSMContext):
    await state.set_state(CardGen.choosing_country)
    await message.answer(
        "First, select the GCC country where you plan to send this greeting:",
        reply_markup=make_kb(tc.COUNTRIES)
    )

@dp.message(CardGen.choosing_country)
async def country_chosen(message: types.Message, state: FSMContext):
    code = get_key_by_value(tc.COUNTRIES, message.text)
    if not code:
        await message.answer("Please choose from the buttons.")
        return
    await state.update_data(country=code)
    await state.set_state(CardGen.choosing_audience)
    await message.answer(
        "Great! Now, who is this greeting for?",
        reply_markup=make_kb(tc.AUDIENCES, cols=1)
    )

@dp.message(CardGen.choosing_audience)
async def audience_chosen(message: types.Message, state: FSMContext):
    code = get_key_by_value(tc.AUDIENCES, message.text)
    if not code:
        await message.answer("Please choose from the buttons.")
        return
    data = await state.get_data()
    
    # Tips
    tip_text = tc.get_tips(data['country'], code)
    await message.answer(tip_text, parse_mode="Markdown")
    
    await state.update_data(audience=code)
    avail_topics_keys = tc.get_available_topics(code)
    topic_buttons = {k: tc.TOPICS[k]["btn"] for k in avail_topics_keys}
    
    await state.set_state(CardGen.choosing_topic)
    await message.answer(
        "Select a theme for your card based on the advice above:",
        reply_markup=make_kb(topic_buttons, cols=2)
    )

@dp.message(CardGen.choosing_topic)
async def topic_chosen(message: types.Message, state: FSMContext):
    topic_code = None
    for k, v in tc.TOPICS.items():
        if v["btn"] == message.text:
            topic_code = k
            break
    if not topic_code:
        await message.answer("Please choose a valid topic.")
        return

    await state.update_data(topic=topic_code)
    desc = tc.TOPICS[topic_code]["desc"]
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Generate Card!")],
            [KeyboardButton(text="⬅️ Back to Topics")]
        ], resize_keyboard=True
    )
    await state.set_state(CardGen.confirming_topic)
    await message.answer(
        f"**Theme Selected:** {message.text}\n\n{desc}\n\nReady to create art?",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(CardGen.confirming_topic)
async def confirm_generation(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Back to Topics":
        data = await state.get_data()
        avail_topics_keys = tc.get_available_topics(data['audience'])
        topic_buttons = {k: tc.TOPICS[k]["btn"] for k in avail_topics_keys}
        await state.set_state(CardGen.choosing_topic)
        await message.answer("Select a theme:", reply_markup=make_kb(topic_buttons))
        return

    if message.text == "✅ Generate Card!":
        data = await state.get_data()
        waiting_msg = await message.answer("🎨 Mixing culture and AI art... Please wait...")
        
        final_prompt = tc.build_final_prompt(data['country'], data['audience'], data['topic'])
        
        # Вызов функции из нового файла ai_service
        image_io = await ai_service.generate_image_bytes(final_prompt)
        
        if image_io:
            file_bytes = image_io.getvalue()
            input_file = BufferedInputFile(file_bytes, filename="greeting_card.jpg")
            
            caption = (
                f"Here is your card for {tc.COUNTRIES[data['country']]}!\n"
                f"Topic: {tc.TOPICS[data['topic']]['btn']}\n\n"
                "Tap /start to create another one."
            )
            
            await bot.send_photo(chat_id=message.chat.id, photo=input_file, caption=caption)
            await waiting_msg.delete()
            await state.clear()
        else:
            await waiting_msg.edit_text("⚠️ Google AI API Error or Policy Block. Please try again or check logs.")
            await state.clear()

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
