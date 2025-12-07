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

# Конфигурация Canvas
CANVAS_SIZE = (1080, 1920)
IMAGE_SIZE = (1080, 1080)
FONT_PATH = "Cinzel-Regular.ttf"

# Настройки текста
MAX_FONT_SIZE = 120    # Начинаем с этого
MIN_FONT_SIZE = 40     # Меньше этого не уменьшаем
TEXT_COLOR = (230, 180, 60)
BG_COLOR = (255, 255, 255)
FRAME_WIDTH = 15

# Область для текста (отступ сверху, максимальная ширина, максимальная высота)
TEXT_START_Y = 1200       # Сразу под картинкой с отступом
TEXT_MAX_WIDTH = 900      # 1080 - отступы по бокам
TEXT_MAX_HEIGHT = 650     # Сколько места есть до низа (1920 - 1200 - отступ снизу)

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

# --- УМНАЯ РАБОТА С ТЕКСТОМ ---

def wrap_text(text, font, max_width, draw_obj):
    """Разбивает текст на строки, чтобы он влезал по ширине."""
    lines = []
    words = text.split()
    current_line = words[0]
    
    for word in words[1:]:
        test_line = current_line + " " + word
        if draw_obj.textlength(test_line, font=font) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def get_text_height(lines, font):
    """Считает общую высоту блока текста."""
    line_height = font.size * 1.3
    return len(lines) * line_height

async def compose_final_card(ai_image_io: BytesIO, user_text: str) -> BytesIO:
    try:
        # 1. Холст
        canvas = Image.new('RGB', CANVAS_SIZE, BG_COLOR)
        draw = ImageDraw.Draw(canvas)

        # 2. Картинка AI
        ai_image = Image.open(ai_image_io)
        if ai_image.mode != 'RGB': ai_image = ai_image.convert('RGB')
        ai_image = ai_image.resize(IMAGE_SIZE, Image.LANCZOS)
        canvas.paste(ai_image, (0, 0))

        # 3. Адаптивный текст
        if user_text:
            current_font_size = MAX_FONT_SIZE
            final_lines = []
            final_font = None
            
            # Цикл подбора размера
            while current_font_size >= MIN_FONT_SIZE:
                try:
                    font = ImageFont.truetype(FONT_PATH, current_font_size)
                except IOError:
                    font = ImageFont.load_default()
                    break # Если шрифта нет, выходим из цикла подбора
                
                # Разбиваем на строки с текущим размером
                lines = wrap_text(user_text, font, TEXT_MAX_WIDTH, draw)
                # Считаем высоту
                total_height = get_text_height(lines, font)
                
                # Если влезает в отведенную область - отлично, останавливаемся
                if total_height <= TEXT_MAX_HEIGHT:
                    final_lines = lines
                    final_font = font
                    break
                
                # Если не влезает - уменьшаем шрифт
                current_font_size -= 5
            
            # Если даже самый маленький шрифт не влез, используем его (обрежется, но что поделать)
            if final_font is None:
                 try:
                    final_font = ImageFont.truetype(FONT_PATH, MIN_FONT_SIZE)
                 except:
                    final_font = ImageFont.load_default()
                 final_lines = wrap_text(user_text, final_font, TEXT_MAX_WIDTH, draw)

            # Рисуем подобранным шрифтом
            line_height = final_font.size * 1.3
            y_offset = TEXT_START_Y + (TEXT_MAX_HEIGHT - get_text_height(final_lines, final_font)) / 2 # Центрируем по вертикали в блоке
            
            for line in final_lines:
                line_width = draw.textlength(line, font=final_font)
                x = (CANVAS_SIZE[0] - line_width) / 2
                draw.text((x, y_offset), line, font=final_font, fill=TEXT_COLOR)
                y_offset += line_height

        # 4. Рамка
        draw.rectangle([(0, 0), (CANVAS_SIZE[0]-1, CANVAS_SIZE[1]-1)], outline=TEXT_COLOR, width=FRAME_WIDTH)

        # 5. Сжатие
        output_io = BytesIO()
        quality = 95
        while quality > 10:
            output_io.seek(0)
            output_io.truncate()
            canvas.save(output_io, format='JPEG', quality=quality)
            if output_io.tell() / 1024 <= 300: break
            quality -= 5

        output_io.seek(0)
        return output_io

    except Exception as e:
        logging.error(f"Composition Error: {e}")
        return None
