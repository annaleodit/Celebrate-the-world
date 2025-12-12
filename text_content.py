"""
Содержит тексты, конфигурации кнопок и логику сборки промптов
для GCC региона.
"""

# --- CONSTANTS ---
COUNTRIES = {
    "uae": "🇦🇪 UAE",
    "ksa": "🇸🇦 Saudi Arabia",
    "qatar": "🇶🇦 Qatar",
    "kuwait": "🇰🇼 Kuwait",
    "bahrain": "🇧🇭 Bahrain",
    "oman": "🇴🇲 Oman"
}

AUDIENCES = {
    "western_expats": "Western Expats",
    "eastern_expats": "Eastern Expats",
    "locals": "Locals",
    "mixed": "Mixed Culture Group"
}

# --- PROMPT PARTS ---
GLOBAL_SAFETY = """
GLOBAL GCC SAFETY PROTOCOL:
STRICTLY NO ALCOHOL: No wine glasses, champagne flutes, or cocktail shakers. Use abstract cups, tea cups, or geometric tumblers only.
NO FEMALE REPRESENTATION: To ensure cultural compliance, do not depict human female figures.
RELIGION: No religious symbols (crosses, angels, saints).
FOCUS: Primary focus is secular "New Year". If "Christmas" is requested, use seasonal winter aesthetics (snow, trees, lights) instead of religious icons. NO Santa Claus except for Western and Eastern expatriate audience and only if explicitly requested in the user prompt. Santa Claus must be depicted as a fun, non-religious fairytale mascot (e.g., wearing sunglasses, carrying shopping bags, or in a futuristic sleigh). NO traditional St. Nicholas religious styling.
TEXT RULES: Do not generate any text, letters, or numbers UNLESS explicitly asked for the year "2026". Apart from "2026", avoid any other text.
NO GLASSES: MUST NOT use glasses with drinks to avoid confusion with wine only tea and coffee are acceptable.
HUMAN FIGURES: NO DISTINCT people or hands or other parts of human body. Women MUST be avoided or at least fully covered/abaya when used as silhouettes.
NO ZODIAK signs, strictly not allowed.
STRICTLY NO skyscrapers or city skylines allowed unless specified in the topic.
"""

COUNTRY_AESTHETICS = {
    "uae": "Aesthetic: 'Future Heritage.' Fusion of hyper-modern architecture and warm golden-hour lighting. Polished glass, steel, and gold textures. Vibe: Limitless ambition, cosmopolitan luxury. Color Palette: Gold, White, Silver, Warm Beige.",
    "ksa": "Aesthetic: Deep, rich, and regal. Blend of historic mud-brick architecture or desert landscapes with sleek modernity. Vibe: Dignity, warmth, 'Kashta' hospitality. Color Palette: Sand, Terracotta, Deep Gold, Midnight Blue.",
    "qatar": "Aesthetic: Artistic and architectural refinement. Geometric patterns, calligraphy, clean lines. Vibe: National pride, sophistication. Color Palette: Dominant Maroon (Burgundy) and White.",
    "kuwait": "Aesthetic: Maritime and mercantile. Sea, dhows, 'Chalet' lifestyle. Strict Restrictions: Family-centric, private. Vibe: Old Money feel, peaceful. Color Palette: Azure Blue, Sand, White, Gold.",
    "bahrain": "Aesthetic: Island city life. Pearl diving heritage. Vibe: Breezy, liberal, social. Visuals: Sea, pearls, fireworks. Color Palette: Coral, Pearl White, Red, Blue.",
    "oman": "Aesthetic: Dramatic nature and heritage. Rugged mountains, ancient forts, low-rise white architecture. Vibe: Humble, grounded, serene. Visuals: Frankincense smoke, mountains, starry nights. Color Palette: Earth tones, White, Green, Silver."
}

AUDIENCE_RULES = {
    "western_expats": "Audience Vibe: Nostalgic, cozy. Holiday Logic: 'Christmas' themes PERMITTED (festive trees, lights). Apply Global safety protocol.",
    "eastern_expats": "Audience Vibe: Nostalgic, cozy. Holiday Logic: 'Christmas' themes PERMITTED. Apply Global safety protocol.",
    "locals": "Audience Vibe: Professional, respectful. Holiday Logic: STRICTLY NEW YEAR / SEASONAL ONLY. NO Christmas symbols (trees). Use confetti, golden lights, fireworks.",
    "mixed": "Audience Vibe: Professional, inclusive. Holiday Logic: STRICTLY NEW YEAR / SEASONAL ONLY. NO Christmas symbols."
}

# --- TOPICS (FINALIZED PROMPTS) ---
TOPICS = {
    "time": {
        "btn": "🕰 Circle of time",
        "desc": "A sophisticated celestial-themed illustration featuring '2026' formed by glowing constellations. Best for: Business Partners & Visionaries.",
        "prompt": """
Role
You are a world-class illustrator specializing in sophisticated, celestial-themed luxury art. Your goal is to create a precise, elegant, and mystical geometric illustration featuring high-contrast metallics and glowing elements.
Style & Aesthetic: High-end luxury ecard design. The look must simulate metallic hot-foil stamping (Gold, Silver, Rose Gold) on premium textured matte paper. 
IMPORTANT: The background color of the paper MUST match the 'Color Palette' defined in the Country Aesthetic section.
The vibe is minimalist, geometric, and expensive.
Scene Description: A composition featuring a large, minimalist clock face with a fine metallic rim.
CRITICAL: The clock hands position must be as described. One 2 hands, the shorter hand facing exactly upright. longer hand - 5 degrees left so that they are indicating 11:55 (five minutes to midnight). The countdown is almost over.
The year "2026" is in the bottom part of the card in a sophisticated serif or script typeface. Around the 2026 stylized orbital rings and small planetary spheres sweep upwards in ellipses, intertwining with the clock to create a seamless celestial countdown theme.
"""
    },
    "fireworks": {
        "btn": "🎆 Firebesque",
        "desc": "Clean, expensive, and structurally precise geometric fireworks. Best for: Mixed Groups & Locals.",
        "prompt": """
Role
You are a high-end graphic designer specializing in luxury vector illustrations and typography for premium greeting cards. Your aesthetic is clean, expensive, structurally precise, and influenced by modern geometric patterns and high-contrast metallic textures.
Style & Aesthetic
No organic sparks or smoke; the aesthetic is clean, expensive, and structurally precise, influenced by modern Islamic geometry. The entire design, including the text, is rendered in luxurious polished gold and brushed copper foil textures, with optional accents of brushed silver foil.
IMPORTANT: The background is a deep, matte tone derived from the 'Color Palette' in the Country Aesthetic section.
Scene Description
A sophisticated contemporary vector illustration for a luxury New Year greeting card featuring the year "2026" stylistically integrated into an abstract, geometric firework explosion. The numbers "2026" are rendered in a custom, linear geometric typeface, acting as the structural core or base of the design.
The composition consists of intersecting fine lines, polygons, and crystalline facets radiating directly from the typography, creating a dynamic architectural burst or a symmetrical mandala effect.
"""
    },
    "falcon": {
        "btn": "🦅 Celestial Falcon",
        "desc": "A high-end e-card featuring a geometric falcon and '2026' as a constellation. Best for: Locals & VIPs.",
        "prompt": """
Role
You are a premier digital artist creating high-end e-cards with a focus on celestial energy and "digital luxury." Your style combines geometric forms with atmospheric, volumetric lighting effects to create immersive, glowing scenes.
Style & Aesthetic
The overall impression is one of celestial energy and digital luxury. The design is composed of golden and bronze beams, connecting points, and shimmering stardust particles on background that emit a warm, volumetric glow against a deep dark, nebular void background (use the Country Aesthetic palette for the void color tone). The light blooms at intersections, creating an atmospheric effect.
Scene Description
A high-end e-card featuring a geometric falcon soaring the air in the left or middle part of the image and the year '2026' rendered as a glowing constellation of light.
"""
    },
    "kashta": {
        "btn": "⛺ Kashta Night",
        "desc": "Cinematic camping scene under the stars. Best for: Locals (KSA, Kuwait) & Authentic vibes.",
        "prompt": """
Role & Style
You are a world-class commercial photographer specializing in luxury travel and mystical landscapes. Your goal is to create cinematic, high-budget photographs with a magical, premium feel, inspired by "1001 Arabian Nights." BUT STRICTLY NO CRESCENT MOON, ONLY FULL MOON ALLOWED.
Lighting: Cinematic and dramatic deep night or "blue hour." High contrast. Focus on the interplay between the deep blue darkness and the warm, welcoming orange glow of the tent.
Fidelity: Photorealistic magic realism. Minimalist, mysterious, and expensive.

Scene Description
A dramatic, wide-angle shot of a landscape at deep night.
**Terrain Logic (Must match the Country Context):**
- IF Bahrain: The setting is a quiet seaside/beach with sand and water reflections.
- IF Oman: The setting is a rugged mountain slope or a rocky Wadi.
- IF KSA/Qatar/Kuwait/UAE: The setting is majestic sand dunes.

**Composition & Framing:**
A single large Kashta tent glows intensely with warm light at the top of a slope or hill.
IMPORTANT: Avoid placing the tent in the dead center. Use the **Rule of Thirds**: place the tent to the left or right side of the frame, or use a low angle to make the hill look vast.
A magical, winding path of small warm lights (lanterns or decorative bulbs) leads up the slope towards the tent, guiding the viewer's eye.
The foreground is dark and textured (sand ripples or rocks). The sky is deep and starry, with a Full Moon or galaxy spiral adding to the mystery.
"""
    },
    "christmas_eve": {
        "btn": "🎄 Christmas in dunes",
        "desc": "A cozy villa terrace overlooking the desert, decorated for Christmas. Best for: Western Expats ONLY.",
        "prompt": """
Role & Style
You are a world-class photographer specializing in luxury travel and mystical landscapes. Your goal is to create cinematic, high-budget photographs with a magical, premium feel, inspired by "1001 Arabian Nights." BUT STRICTLY NO CRESCENT MOON, ONLY FULL MOON ALLOWED.
Lighting: Cinematic and dramatic deep night or "blue hour." High contrast. Use warm, golden artificial lights (lanterns, magic glow) against deep cool blues and indigos of the sky and shadows.
Color Palette: Rich and deep. Dominant colors are deep indigo/navy blue and warm gold/copper/orange.
Texture & Scale: Emphasize the tactile nature of sand ripples and the vast, majestic scale of the dunes. The images must feel expensive and immersive.
Fidelity: Photorealistic magic realism. Not a cartoon.
Scene Description
Terrace of a villa in one of the GCC countries with a rich garden in front, but overlooking a desert. The view is from inside the house or from terrace entrance. This is an expatriate home, so it is decorated for Christmas and the Christmas tree is on the terrace. Also sofa, pillows. The terrace is warm and cozy, decorated in European style. Warm light, a lot of bokeh, Christmas setting. STRICTLY NO RAMADAN FANOUS. Magical, shimmering particles resembling snow or stardust are falling from the starry skies on the terrace.
"""
    },
    "parol": {
        "btn": "🌟 Parol Lantern",
        "desc": "A glowing Filipino star lantern, warm and inviting. Best for: Eastern Expats.",
        "prompt": """
Role & Style
You are a world-class creative director and high-end photographer supervising a holiday campaign for a premium post cards brand. Your goal is to ensure every image generated looks luxurious, expensive, sophisticated, and heartwarming.
1. Lighting is Key (Cinematic Warmth):
NEVER use flat, bright, or harsh lighting. ALWAYS use cinematic, professional lighting schemes. Think "Golden Hour," warm studio softboxes, dramatic rim lighting to separate the subject from the background, and deep, rich shadows that add volume. The light must feel cozy, expensive, inviting, and not dark.
2. Composition & Depth (Professional Photography):
Use a shallow depth of field (strong bokeh effect). The main subject (the "hero" Paról lantern) should be tack sharp and the clear focus. The background must be a beautiful, blurry wash of warm holiday lights (garlands, fireplace glow) and rich colors. The composition must be balanced and elegant.
3. Color Palette (Rich & Deep):
Automatic color grading towards rich, deep tones. Focus on burgundy, forest green, deep navy, warm cream, gold, copper, and natural wood tones. Avoid oversaturated primary colors unless they are deeply pigmented accents within a luxury material.
4. Fidelity (Tactile Reality):
The final output must be a photorealistic photograph of the object/scene, even if the style is illustrative (like watercolor or cartoon). It should feel tactile, as if you can reach out and touch the luxury material. We are photographing the art piece, not just rendering a flat image.
5. COMPOSITION & FRAMING (CRITICAL):
The image must be EDGE-TO-EDGE. The scene or texture must fill the entire canvas. The "camera" should be close enough that the subject and the magical atmosphere fill 100% of the image.
Scene Description
A photo showcasing a Filipino Christmas Paról lantern, all illuminated and set against a dark, nighttime background with softly blurred streetlights. The Paról should be a five-pointed star shape, but can be in different materials and styles, traditional red and blue or monochromatic.
"""
    }
}

# --- LOGIC HELPERS ---

def get_tips(country: str, audience: str) -> str:
    """Возвращает экспертный совет на основе комбинации"""
    # UAE
    if country == "uae" and audience == "mixed":
        return "💡 **Insider Scoop:** The UAE is a global melting pot.\n😎 **Pro Tip:** 'Fireworks' or 'Time' themes work perfectly here for mixed audiences. They are sophisticated and neutral."
    if country == "uae" and audience == "locals":
        return "💡 **Insider Scoop:** For Emiratis, focus on Vision & Prosperity.\n😎 **Pro Tip:** 'Falcon' or 'Time' are excellent respectful choices. Avoid mentioning parties or Christmas, stick to Season's Greetings or New Year."

    # KSA
    if country == "ksa" and audience == "locals":
        return "💡 **Insider Scoop:** It's 'Kashta' Time! The desert is KSA winter wonderland.\n😎 **Pro Tip:** Impress your friends and partners with the 'Kashta' theme. It hits right in the heart. Avoid mentioning parties or Christmas, stick to Season's Greetings or New Year."
    if country == "ksa" and audience == "mixed":
        return "💡 **Insider Scoop:** Offices are modernizing but etiquette remains conservative.\n😎 **Pro Tip:** 'Time' or 'Falcon' themes are safe, premium choices for your greetings. Avoid mentioning parties or Christmas, stick to Season's Greetings or New Year."

    # Kuwait
    if country == "kuwait" and audience == "locals":
        return "💡 **Insider Scoop:** A Kashta break is a must in winter.\n😎 **Pro Tip:** 'Kashta' or 'Time' themes respect their privacy and love for the desert winter."

    # Oman
    if country == "oman" and audience == "locals":
        return "💡 **Insider Scoop:** These country chooses serenity over noise.\n😎 **Pro Tip:** 'Falcon' or 'Time' fit the Omani values of dignity and nature."
    
    # Generalized Audiences
    if audience == "eastern_expats":
        return (
            "💡 **Insider Scoop:** This is a very mixed audience. Choose visuals and messages carefully.\n"
            "😎 **Pro Tips:** If you have Filipino colleagues or friends, 'Parol Lantern' is a winner. "
            "There is a 90% chance they celebrate Christmas. Check it and get your greeting right!\n\n"
            "Your colleagues from Russia and CIS celebrate New Year rather than Christmas."
            "Christmas, if celebrated, is on January 7th. Remember that it is a more religious holiday than in western countries and that there is a lagre muslim comunity in CIS.\n\n"
            "For Indian colleagues, remember that many celebrate Diwali, but New Year is generally universally accepted."
        )
    if audience == "western_expats":
        return "💡 **Insider Scoop:** Winter = BBQ Season.\n😎 **Pro Tip:** 'Christmas in dunes' theme perfectly combines the tradition with Gulf desert vibe."
    
    if country == "qatar":
        return "💡 **Insider Scoop:** Qatar National Day is on December 18th, don't miss it.\n😎 **Pro Tip:** Themes like 'Time' or 'Fireworks' work well. Maroon Elegance would be a good choice. The AI will try to respect the local palette."
    
    if country == "bahrain":
        return "💡 **Insider Scoop:** Bahrain is famously open and social and has an Island Vibe.\n😎 **Pro Tip:** You can be a bit more relaxed here! 'Fireworks' are very welcome here as well as celebrations generally."

    return "💡 **Tip:** Remember the Golden Rule of GCC: Be respectful, exclude alcohol imagery and religious elements, focus on shared values like prosperity, light, and warmth."

def get_available_topics(audience: str):
    """Фильтрует топики для безопасности"""
    keys = list(TOPICS.keys())
    
    # ПРАВИЛА БЕЗОПАСНОСТИ:
    
    # 1. Christmas Eve только для Western Expats
    if audience != "western_expats":
        if "christmas_eve" in keys:
            keys.remove("christmas_eve")
            
    # 2. Parol только для Eastern Expats
    if audience != "eastern_expats":
        if "parol" in keys:
            keys.remove("parol")
            
    # 3. Для Locals и Mixed убираем специфические "чужие" праздники (на всякий случай, хотя правила выше уже отработали)
    # Оставляем только нейтральные/локальные: time, fireworks, falcon, kashta
    if audience in ["locals", "mixed"]:
        # Убедимся, что экспатские темы точно удалены
        for unsafe in ["christmas_eve", "parol"]:
            if unsafe in keys:
                keys.remove(unsafe)
                
    return keys

def build_final_prompt(country_code, audience_code, topic_code):
    """Сборка финального промпта для AI (Prioritizing Audience Vibe)"""
    
    # 1. Достаем данные
    c_data = COUNTRY_AESTHETICS.get(country_code, "")
    a_data = AUDIENCE_RULES.get(audience_code, "")
    t_data = TOPICS[topic_code]["prompt"]
    
    # 2. Умная фильтрация контекста (Smart Context)
    # Если тема "Kashta", "Falcon" или "Christmas Eve" (природные/традиционные), 
    # мы игнорируем описание современной архитектуры страны, оставляя только цвета.
    country_context = c_data
    if topic_code in ["kashta", "falcon", "christmas_eve"]:
        country_context = (
            f"COUNTRY SETTING: {COUNTRIES[country_code]}.\n"
            "IMPORTANT: Ignore modern architecture descriptions (skyscrapers, glass, steel). "
            "Focus ONLY on the local Color Palette and Vibe defined below."
        )

    # 3. Новая структура: Subject -> MOOD (Audience) -> Colors (Country) -> Safety
    
    full_prompt = (
        f"--- ROLE & TASK ---\n"
        f"{t_data}\n\n"
        
        f"--- MOOD & EMOTIONAL TONE (CRITICAL) ---\n"
        f"The atmosphere of the image must match this target audience:\n"
        f"{a_data}\n"
        f"Adjust lighting and 'feeling' to match this vibe (e.g., Cozy/Nostalgic vs. Proud/Majestic).\n\n"
        
        f"--- COLOR PALETTE & SETTING ---\n"
        f"Country Context: {country_context}\n"
        f"Use the Color Palette of {COUNTRIES[country_code]}.\n\n"
        
        f"--- TECHNICAL CONSTRAINTS & SAFETY ---\n"
        f"VIEW: Full-screen digital art, edge-to-edge. NO physical card on a table. No borders.\n"
        f"{GLOBAL_SAFETY}"
    )
    
    return full_prompt
