import logging
import asyncio
import os
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from google import genai 
from google.genai import types as genai_types

# Импорт конфигурации и текстов
import config
import text_content as tc

# --- SETUP ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Инициализация клиента GenAI (Новая библиотека)
client = genai.Client(api_key=config.GOOGLE_API_KEY)

# --- DATABASE ---
async def init_db():
    async with aiosqlite.connect(config.DB_NAME) asdb:
        await asdb.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await asdb.commit()

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
    # Разбивка на колонки
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
            await asyncio.sleep(0.05) # Rate limit safety
        except Exception:
            pass # User blocked bot
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
    country = data['country']
    
    # 1. Показать TIPS
    tip_text = tc.get_tips(country, code)
    await message.answer(tip_text, parse_mode="Markdown")
    
    # 2. Предложить Topics (с фильтрацией)
    await state.update_data(audience=code)
    
    avail_topics_keys = tc.get_available_topics(code)
    # Формируем словарь для клавиатуры на основе ключей
    topic_buttons = {k: tc.TOPICS[k]["btn"] for k in avail_topics_keys}
    
    await state.set_state(CardGen.choosing_topic)
    await message.answer(
        "Select a theme for your card based on the advice above:",
        reply_markup=make_kb(topic_buttons, cols=2)
    )

@dp.message(CardGen.choosing_topic)
async def topic_chosen(message: types.Message, state: FSMContext):
    # Найти ключ топика по тексту кнопки
    topic_code = None
    for k, v in tc.TOPICS.items():
        if v["btn"] == message.text:
            topic_code = k
            break
            
    if not topic_code:
        await message.answer("Please choose a valid topic.")
        return

    await state.update_data(topic=topic_code)
    
    # Показать описание топика
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
        
        # Сборка промпта
        final_prompt = tc.build_final_prompt(data['country'], data['audience'], data['topic'])
        
        try:
            # --- GOOGLE GENAI CALL ---
            # Используем новую библиотеку google-genai
            # Она автоматически возвращает объект с байтами изображения
            response = client.models.generate_image(
                model='imagen-3.0-generate-001',
                prompt=final_prompt,
                config=genai_types.GenerateImageConfig(
                    aspect_ratio="1:1",
                    number_of_images=1,
                    safety_filter_level="block_medium_and_above",
                    person_generation="allow_adult" # Но промпт запрещает женщин
                )
            )
            
            # В новой библиотеке response.generated_images[0].image.image_bytes
            # содержит сырые байты, декодировать base64 вручную не нужно, библиотека делает это сама.
            image_bytes = response.generated_images[0].image.image_bytes
            
            # Отправка в телеграм
            input_file = BufferedInputFile(image_bytes, filename="greeting_card.png")
            
            caption = (
                f"Here is your card for {tc.COUNTRIES[data['country']]}!\n"
                f"Topic: {tc.TOPICS[data['topic']]['btn']}\n\n"
                "Tap /start to create another one."
            )
            
            await bot.send_photo(chat_id=message.chat.id, photo=input_file, caption=caption)
            await waiting_msg.delete()
            await state.clear()
            
        except Exception as e:
            logging.error(f"Error generating image: {e}")
            await waiting_msg.edit_text("⚠️ Something went wrong with the AI service. Please try again later.")
            await state.clear()

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
