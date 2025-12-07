import os
import logging
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Библиотека Google
from google import genai
from google.genai import types

load_dotenv()

# --- КОНФИГУРАЦИЯ ---
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash-image"

# Конфигурация для сборки открытки (Stories format)
CANVAS_SIZE = (1080, 1920) # Full HD Vertical
IMAGE_SIZE = (1080, 1080)  # Квадрат сверху
FONT_PATH = "Cinzel-Regular.ttf" # Файл шрифта должен лежать рядом
FONT_SIZE = 60
TEXT_COLOR = (212, 175, 55) # Золотой цвет (RGB)
BG_COLOR = (255, 255, 255) # Белый фон
FRAME_WIDTH = 15 # Толщина рамки

# Инициализация клиента
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    logging.error("GOOGLE_API_KEY is missing!")
    client = None

# Настройки безопасности
SAFETY_SETTINGS = [
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_LOW_AND_ABOVE"),
]

async def generate_image_bytes(positive_prompt: str) -> BytesIO:
    """Генерирует квадратное изображение через Google AI."""
    if not client: return None
    try:
        logging.info(f"🎨 Generating base AI image...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=positive_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                safety_settings=SAFETY_SETTINGS,
                image_config=types.ImageConfig(aspect_ratio="1:1")
            )
        )
        if not response.candidates or not response.candidates[0].content.parts: return None

        image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data if isinstance(part.inline_data.data, bytes) else base64.b64decode(part.inline_data.data)
                break
        
        return BytesIO(image_bytes) if image_bytes else None
    except Exception as e:
        logging.error(f"Generate Error: {e}")
        return None

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РИСОВАНИЯ ---

def draw_text_wrapped(draw, text, font, max_width, start_y, color):
    """Рисует текст с автоматическим переносом строк."""
    lines = []
    words = text.split()
    current_line = words[0]
    
    for word in words[1:]:
        # Проверяем ширину, если добавить следующее слово
        test_line = current_line + " " + word
        if draw.textlength(test_line, font=font) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Рисуем строки по центру
    y_offset = start_y
    # Высота строки (примерно)
    line_height = font.size * 1.2  
    
    for line in lines:
        # Вычисляем ширину строки для центрирования
        line_width = draw.textlength(line, font=font)
        x = (CANVAS_SIZE[0] - line_width) / 2
        draw.text((x, y_offset), line, font=font, fill=color)
        y_offset += line_height

async def compose_final_card(ai_image_io: BytesIO, user_text: str) -> BytesIO:
    """
    Склеивает финальную открытку: Белый фон + AI картинка + Текст + Рамка.
    Гарантирует размер < 300 KB.
    """
    try:
        # 1. Создаем белый холст
        canvas = Image.new('RGB', CANVAS_SIZE, BG_COLOR)
        draw = ImageDraw.Draw(canvas)

        # 2. Загружаем и размещаем AI картинку сверху
        ai_image = Image.open(ai_image_io)
        if ai_image.mode != 'RGB':
            ai_image = ai_image.convert('RGB')
        ai_image = ai_image.resize(IMAGE_SIZE, Image.LANCZOS)
        canvas.paste(ai_image, (0, 0))

        # 3. Рисуем текст (если есть)
        if user_text:
            try:
                font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            except IOError:
                logging.warning("Cinzel font not found, using default.")
                font = ImageFont.load_default()
            
            # Начинаем рисовать текст под картинкой с отступом
            text_start_y = IMAGE_SIZE[1] + 150 
            # Максимальная ширина текста с отступами по бокам
            max_text_width = CANVAS_SIZE[0] - 200 
            
            draw_text_wrapped(draw, user_text, font, max_text_width, text_start_y, TEXT_COLOR)

        # 4. Рисуем золотую рамку поверх всего
        # Координаты: (x0, y0, x1, y1). Вычитаем 1 пиксель, чтобы не вылезти за край.
        draw.rectangle(
            [(0, 0), (CANVAS_SIZE[0]-1, CANVAS_SIZE[1]-1)], 
            outline=TEXT_COLOR, 
            width=FRAME_WIDTH
        )

        # 5. Сохранение с компрессией под 300 KB
        output_io = BytesIO()
        quality = 95 # Начинаем с высокого качества
        
        while quality > 10:
            output_io.seek(0)
            output_io.truncate() # Очищаем буфер
            canvas.save(output_io, format='JPEG', quality=quality)
            
            size_kb = output_io.tell() / 1024
            logging.info(f"Image Size at Q{quality}: {size_kb:.1f} KB")
            
            if size_kb <= 300: # Цель достигнута
                break
            
            quality -= 5 # Понижаем качество, если файл слишком большой

        output_io.seek(0)
        return output_io

    except Exception as e:
        logging.error(f"Composition Error: {e}")
        return None
