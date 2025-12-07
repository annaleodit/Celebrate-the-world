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
FONT_PATH = "CinzelDecorative-Regular.ttf"

# Настройки текста
MAX_FONT_SIZE = 180    # УВЕЛИЧИЛИ: Начинаем с очень крупного
MIN_FONT_SIZE = 50     # Меньше этого будет нечитабельно
TEXT_COLOR = (212, 175, 55) # Золото (Cinzel Gold)
BG_COLOR = (255, 255, 255)
FRAME_WIDTH = 20       # Рамка чуть жирнее

# Область для текста
TEXT_START_Y = 1150       # Чуть выше
TEXT_MAX_WIDTH = 950      # Шире область
TEXT_MAX_HEIGHT = 700     

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
    """Разбивает текст на строки."""
    lines = []
    words = text.split()
    if not words: return []
    
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        # Используем textbbox для точного измерения
        bbox = draw_obj.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def get_text_block_size(lines, font, draw_obj):
    """Считает реальную высоту и ширину блока текста."""
    if not lines: return 0, 0
    
    # Высота строки (ascent + descent)
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + 15 # +15 пикселей межстрочный
    total_height = len(lines) * line_height
    
    # Максимальная ширина
    max_w = 0
    for line in lines:
        bbox = draw_obj.textbbox((0, 0), line, font=font)
        max_w = max(max_w, bbox[2] - bbox[0])
        
    return max_w, total_height, line_height

async def compose_final_card(ai_image_io: BytesIO, user_text: str) -> BytesIO:
    try:
        canvas = Image.new('RGB', CANVAS_SIZE, BG_COLOR)
        draw = ImageDraw.Draw(canvas)

        # Картинка AI
        ai_image = Image.open(ai_image_io)
        if ai_image.mode != 'RGB': ai_image = ai_image.convert('RGB')
        ai_image = ai_image.resize(IMAGE_SIZE, Image.LANCZOS)
        canvas.paste(ai_image, (0, 0))

        # Текст
        if user_text:
            current_font_size = MAX_FONT_SIZE
            final_lines = []
            final_font = None
            final_line_height = 0
            
            # 1. Подбор размера (Iterative sizing)
            while current_font_size >= MIN_FONT_SIZE:
                try:
                    font = ImageFont.truetype(FONT_PATH, current_font_size)
                except IOError:
                    logging.critical(f"🚨 FONT ERROR: Could not find {FONT_PATH}. Using ugly default!")
                    # Если шрифта нет, используем дефолтный и прерываем цикл,
                    # так как дефолтный не меняет размер
                    font = ImageFont.load_default()
                    final_lines = wrap_text(user_text, font, TEXT_MAX_WIDTH, draw)
                    final_font = font
                    _, _, final_line_height = get_text_block_size(final_lines, font, draw)
                    break 
                
                lines = wrap_text(user_text, font, TEXT_MAX_WIDTH, draw)
                _, total_height, line_height = get_text_block_size(lines, font, draw)
                
                if total_height <= TEXT_MAX_HEIGHT:
                    final_lines = lines
                    final_font = font
                    final_line_height = line_height
                    break # Влезло!
                
                current_font_size -= 10 # Уменьшаем шаг
            
            # Если вышли из цикла и шрифт не найден (fallback logic)
            if final_font is None:
                 try:
                    final_font = ImageFont.truetype(FONT_PATH, MIN_FONT_SIZE)
                 except:
                    final_font = ImageFont.load_default()
                 final_lines = wrap_text(user_text, final_font, TEXT_MAX_WIDTH, draw)
                 _, _, final_line_height = get_text_block_size(final_lines, final_font, draw)

            # 2. Рисование по центру блока
            # Считаем реальную высоту финального блока
            block_height = len(final_lines) * final_line_height
            # Центрируем блок по вертикали в доступном пространстве
            start_y = TEXT_START_Y + (TEXT_MAX_HEIGHT - block_height) / 2
            
            for line in final_lines:
                # Центрируем строку по горизонтали
                bbox = draw.textbbox((0, 0), line, font=final_font)
                text_width = bbox[2] - bbox[0]
                x = (CANVAS_SIZE[0] - text_width) / 2
                
                draw.text((x, start_y), line, font=final_font, fill=TEXT_COLOR)
                start_y += final_line_height

        # Рамка
        draw.rectangle([(0, 0), (CANVAS_SIZE[0]-1, CANVAS_SIZE[1]-1)], outline=TEXT_COLOR, width=FRAME_WIDTH)

        # Сжатие
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
