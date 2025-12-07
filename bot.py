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
    choosing_audience = State()
    choosing_topic = State()
    confirming_topic = State()
    waiting_for_text = State() # НОВОЕ СОСТОЯНИЕ

# --- KEYBOARD BUILDER (INLINE) ---
def make_inline_kb(items: dict, prefix: str, cols=2):
    builder = []
    keys = list(items.keys())
    for i in range(0, len(keys), cols):
        row = []
        for key in keys[i:i + cols]:
            btn_text = items[key] if isinstance(items[key], str) else items[key]["btn"]
            row.append(InlineKeyboardButton(text=btn_text, callback_data=f"{prefix}:{key}"))
        builder.append(row)
    return InlineKeyboardMarkup(inline_keyboard=builder)

# --- HANDLERS: START & FLOW ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await add_user(message.from_user.id, message.from_user.username)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Start Creating", callback_data="start_flow")]])
    await message.answer("Hello! Tap the button below to start creating your professional GCC greeting card.", reply_markup=kb)

@dp.callback_query(F.data == "start_flow")
async def start_flow(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CardGen.choosing_country)
    await callback.message.edit_text("First, select the GCC country:", reply_markup=make_inline_kb(tc.COUNTRIES, prefix="country"))
    await callback.answer()

@dp.callback_query(F.data.startswith("country:"))
async def country_chosen(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split(":")[1]
    await state.update_data(country=country_code)
    await state.set_state(CardGen.choosing_audience)
    await callback.message.edit_text(f"Selected: {tc.COUNTRIES[country_code]}\n\nNow, who is this greeting for?", reply_markup=make_inline_kb(tc.AUDIENCES, prefix="audience", cols=1))
    await callback.answer()

@dp.callback_query(F.data.startswith("audience:"))
async def audience_chosen(callback: CallbackQuery, state: FSMContext):
    audience_code = callback.data.split(":")[1]
    data = await state.get_data()
    await state.update_data(audience=audience_code)
    
    avail_topics_keys = tc.get_available_topics(audience_code)
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    tip_text = tc.get_tips(data['country'], audience_code)
    
    await state.set_state(CardGen.choosing_topic)
    await callback.message.edit_text(f"🎯 Target: {tc.AUDIENCES[audience_code]}\n\n{tip_text}\n\n👇 **Select a theme:**", reply_markup=make_inline_kb(filtered_topics, prefix="topic", cols=2), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("topic:"))
async def topic_chosen(callback: CallbackQuery, state: FSMContext):
    topic_code = callback.data.split(":")[1]
    await state.update_data(topic=topic_code)
    desc = tc.TOPICS[topic_code]["desc"]
    topic_name = tc.TOPICS[topic_code]["btn"]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Continue to Text", callback_data="ask_for_text")],
        [InlineKeyboardButton(text="⬅️ Back to Topics", callback_data="back_to_topics")]
    ])
    await state.set_state(CardGen.confirming_topic)
    await callback.message.edit_text(f"**Theme Selected:** {topic_name}\n\n{desc}\n\nProceed to add your personal message?", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_to_topics")
async def back_to_topics(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    avail_topics_keys = tc.get_available_topics(data['audience'])
    filtered_topics = {k: tc.TOPICS[k] for k in avail_topics_keys}
    await state.set_state(CardGen.choosing_topic)
    await callback.message.edit_text("👇 **Select a theme:**", reply_markup=make_inline_kb(filtered_topics, prefix="topic", cols=2), parse_mode="Markdown")
    await callback.answer()

# --- НОВЫЙ ЭТАП: ЗАПРОС ТЕКСТА ---

@dp.callback_query(F.data == "ask_for_text")
async def ask_for_text_action(callback: CallbackQuery, state: FSMContext):
    """Переводит бота в режим ожидания текста от пользователя."""
    await state.set_state(CardGen.waiting_for_text)
    
    # Кнопка для тех, кто не хочет писать текст
    skip_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Skip Text & Generate ⏩", callback_data="skip_text")]
    ])
    
    await callback.message.edit_text(
        "✍️ **Add your personal message.**\n\n"
        "Send me the text you want to appear on the card (e.g., 'Season's Greetings from [Company Name]').\n"
        "Keep it concise for the best look!\n\n"
        "*Or tap Skip below.*",
        reply_markup=skip_kb,
        parse_mode="Markdown"
    )
    await callback.answer()

# --- ФИНАЛЬНАЯ ГЕНЕРАЦИЯ (С ТЕКСТОМ ИЛИ БЕЗ) ---

async def perform_generation(message: types.Message, state: FSMContext, user_text: str = None):
    """Общая функция для генерации и отправки, вызывается из двух хэндлеров ниже."""
    data = await state.get_data()
    
    # Информируем пользователя о начале процесса
    status_msg = await message.answer("🎨 Creating your professional card... This involves AI generation and graphical composition. Please wait (approx 15-20s)...")
    
    # 1. Генерация AI картинки
    final_prompt = tc.build_final_prompt(data['country'], data['audience'], data['topic'])
    ai_image_io = await ai_service.generate_image_bytes(final_prompt)
    
    if not ai_image_io:
        await status_msg.edit_text("⚠️ AI Generation Error. Please try again later.")
        await state.clear()
        return

    # 2. Сборка финальной открытки (Холст + AI + Текст + Рамка)
    await status_msg.edit_text("🖌️ Composing final design and applying golden frame...")
    final_card_io = await ai_service.compose_final_card(ai_image_io, user_text)
    
    if final_card_io:
        file_bytes = final_card_io.getvalue()
        # Важно: отправляем как фото, чтобы телеграм показал превью
        input_file = BufferedInputFile(file_bytes, filename="greeting_card_stories.jpg")
        
        caption = (
            f"Here is your professional card for {tc.COUNTRIES[data['country']]}!\n"
            f"Format: Instagram Stories (9:16)\n\n"
            "Tap /start to create another one."
        )
        
        await status_msg.delete()
        await bot.send_photo(chat_id=message.chat.id, photo=input_file, caption=caption)
    else:
        await status_msg.edit_text("⚠️ Error during final card composition.")
    
    await state.clear()

# Хэндлер 1: Пользователь прислал текст
@dp.message(CardGen.waiting_for_text, F.text)
async def text_received(message: types.Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer(
            f"⚠️ Your text is too long ({len(message.text)} chars). \n"
            "Please keep it under 200 characters for the best design.\n\n"
            "Try sending a shorter version:"
        )
        return
    # Вызываем общую функцию с полученным текстом
    await perform_generation(message, state, user_text=message.text)

# Хэндлер 2: Пользователь нажал "Skip Text"
@dp.callback_query(CardGen.waiting_for_text, F.data == "skip_text")
async def skip_text_action(callback: CallbackQuery, state: FSMContext):
    # --- ОБНОВЛЕННЫЙ ТЕКСТ ПО УМОЛЧАНИЮ ---
    default_text = "Season's Greetings and best wishes for a prosperous and successful New Year."
    
    # Вызываем генерацию с этим текстом
    await perform_generation(callback.message, state, user_text=default_text)
    await callback.answer()

# --- ADMIN & MAIN ---
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
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
