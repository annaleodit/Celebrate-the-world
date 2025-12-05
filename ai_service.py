import os
import logging
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Библиотека Google
from google import genai
from google.genai import types

load_dotenv()

# --- КОНФИГУРАЦИЯ ---
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash-image" 

# Инициализация клиента
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    logging.error("GOOGLE_API_KEY is missing!")
    client = None

# Настройки безопасности
SAFETY_SETTINGS = [
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_LOW_AND_ABOVE"
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_LOW_AND_ABOVE"
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_LOW_AND_ABOVE"
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_LOW_AND_ABOVE"
    ),
]

async def generate_image_bytes(positive_prompt: str) -> BytesIO:
    """
    Генерирует изображение через generate_content и возвращает BytesIO.
    """
    if not client:
        return None

    try:
        logging.info(f"🎨 Generating with model {MODEL_NAME}...")
        
        # 1. Запрос к API
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=positive_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                safety_settings=SAFETY_SETTINGS,
                # ИСПРАВЛЕНИЕ: Убрали number_of_images=1, так как Pydantic ругается
                image_config=types.ImageConfig(aspect_ratio="1:1")
            )
        )

        # 2. Проверка ответа
        if not response.candidates or not response.candidates[0].content.parts:
            logging.error("Google API returned empty content parts.")
            return None

        # 3. Извлечение картинки
        image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                # Библиотека может вернуть bytes или base64 string
                if isinstance(part.inline_data.data, bytes):
                    image_bytes = part.inline_data.data
                else:
                    try:
                        image_bytes = base64.b64decode(part.inline_data.data)
                    except:
                        image_bytes = part.inline_data.data
                break
            elif part.text:
                logging.warning(f"Model returned text: {part.text}")

        if not image_bytes:
            logging.error("No image bytes found.")
            return None

        # 4. Обработка через Pillow (конвертация в JPEG)
        try:
            image = Image.open(BytesIO(image_bytes))
            
            output_io = BytesIO()
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            image.save(output_io, format='JPEG', quality=90)
            output_io.seek(0)
            return output_io
            
        except Exception as img_err:
            logging.error(f"PIL Error: {img_err}")
            return BytesIO(image_bytes) # Возвращаем сырые байты, если PIL не справился

    except Exception as e:
        logging.error(f"Generate Error: {e}")
        return None
