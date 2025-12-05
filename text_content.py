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
NO FEMALE REPRESENTATION: Do not depict human female figures. Use abstract silhouettes, hands only, or focus on objects/scenery.
RELIGION: No religious symbols (crosses, angels, saints).
FOCUS: Primary focus is secular "New Year". If "Christmas" logic applies, use seasonal winter aesthetics only. NO traditional St. Nicholas.
NO TEXT: Do not generate any text, letters, or numbers on the image. Pure visual art only.
"""

COUNTRY_AESTHETICS = {
    "uae": "Aesthetic: 'Future Heritage.' Fusion of hyper-modern architecture and warm golden-hour lighting. Polished glass, steel, and gold textures. Vibe: Limitless ambition, cosmopolitan luxury.",
    "ksa": "Aesthetic: Deep, rich, and regal. Blend of historic mud-brick architecture or desert landscapes with sleek modernity. Palette: Sand, Terracotta, Deep Gold, Midnight Blue. Vibe: Dignity, warmth, 'Kashta' hospitality.",
    "qatar": "Aesthetic: Artistic and architectural refinement. Geometric patterns, calligraphy, clean lines. Palette: Dominant Maroon (Burgundy) and White. Vibe: National pride, sophistication.",
    "kuwait": "Aesthetic: Maritime and mercantile. Sea, water towers, 'Chalet' lifestyle. Strict Restrictions: Family-centric, private. Vibe: Old Money feel, peaceful.",
    "bahrain": "Aesthetic: Island city life. Iconic wind-turbine skyscrapers, pearl diving heritage. Vibe: Breezy, liberal, social. Visuals: Sea, pearls, sunset.",
    "oman": "Aesthetic: Dramatic nature and heritage. Rugged mountains, ancient forts, low-rise white architecture. Vibe: Humble, grounded, serene. Visuals: Frankincense smoke, mountains, starry nights."
}

AUDIENCE_RULES = {
    "western_expats": "Audience Vibe: Nostalgic, cozy. Holiday Logic: 'Christmas' themes PERMITTED (festive trees, lights). Apply Global safety protocol.",
    "eastern_expats": "Audience Vibe: Nostalgic, cozy. Holiday Logic: 'Christmas' themes PERMITTED. Apply Global safety protocol.",
    "locals": "Audience Vibe: Professional, respectful. Holiday Logic: STRICTLY NEW YEAR / SEASONAL ONLY. NO Christmas symbols (trees). Use confetti, golden lights, fireworks.",
    "mixed": "Audience Vibe: Professional, inclusive. Holiday Logic: STRICTLY NEW YEAR / SEASONAL ONLY. NO Christmas symbols."
}

# --- TOPICS ---
TOPICS = {
    "fireworks": {
        "btn": "🎆 Fireworks",
        "desc": "Universal symbol of joy. Best for mixed groups/locals to say 'Bright successful year' without religious sensitivities.",
        "prompt": "Spectacular, colorful fireworks exploding in a dark night sky filled with stars and a full moon. The scene is festive and bright. The warm, vibrant light reflects on water/glass/sand. Cinematic lighting, high res celebration."
    },
    "clocks": {
        "btn": "🕰 Clocks & Time",
        "desc": "Abstract, premium. Symbolizes progress, Vision 2030, and new financial cycles. Best for Management/Investors.",
        "prompt": "A majestic, abstract representation of time transitioning into a new era. Colossal golden gears, flowing sand made of light and gold dust, or futuristic digital timeline. Luxurious, visionary style. Focus on progress."
    },
    "skylines": {
        "btn": "🏙 Skylines & Towers",
        "desc": "Respectful compliment to the country's ambition and development. Best for Business Partners & Locals.",
        "prompt": "Breathtaking panoramic view of a modern city skyline deep into the night. Dark sky, stars, full moon. Tall futuristic skyscrapers with warm illuminated windows. Warm directional light reflects off glass/water. Stylized regional architecture."
    },
    "abstract": {
        "btn": "✨ Abstract Celebration",
        "desc": "The 'Gold Standard' of corporate diplomacy. Safe, elegant, high style. Zero-risk option for VIPs.",
        "prompt": "Beautiful abstract background representing celebration. Flowing ribbons of gold and silver light, confetti, geometric 3D shapes. Clean, corporate, festive. No specific objects, expensive textures."
    },
    "desert": {
        "btn": "🌌 Desert Starlight (Kashta)",
        "desc": "Authentic 'Winter Wonderland' for locals. Shows deep respect for traditions (camping/Kashta).",
        "prompt": "Luxurious traditional desert camp scene deep in the night. Dark sky, bright stars, full moon. Warm directional light from fire pits, brass lanterns, fairy lights reflects on sand dunes and tents. Peaceful, majestic."
    },
    "lanterns": {
        "btn": "🌟 Lanterns of Hope",
        "desc": "Inspired by Parols. A 'warm hug' for Eastern expats. Universal symbol of joy and light.",
        "prompt": "Close-up focus on magnificent, glowing star-shaped lanterns (inspired by Filipino Parols). Intricate, translucent shells/brass. Dark night background with soft warm bokeh fairy lights. Emphasis on hope and warmth."
    },
    "terrace": {
        "btn": "☕ Warm Winter Terrace",
        "desc": "Captures the ideal Gulf winter lifestyle: outdoors and cozy. Best for Western Expats/Mixed.",
        "prompt": "Cozy inviting scene on an outdoor luxury terrace deep in the night. Dark starry sky, full moon. Palm trees wrapped in fairy lights. Warm directional light from candles reflects on tables. Lounge seating. Relaxed, sophisticated."
    },
    "christmas": {
        "btn": "🎄 Christmas Stories",
        "desc": "Classic nostalgia. Use ONLY if you are 100% sure the recipient celebrates. Not for Locals.",
        "prompt": "Cozy, stylized seasonal winter scene at night. Decorated pine tree or festive corner with wrapped gifts. Dark starry sky, full moon. Warm fairy lights and candlelight reflections. Magical, warm atmosphere."
    }
}

# --- LOGIC HELPERS ---

def get_tips(country: str, audience: str) -> str:
    """Возвращает экспертный совет на основе комбинации"""
    key = (country, audience)
    
    # Logic implementation based on the detailed Brief
    if country == "uae" and audience == "mixed":
        return "💡 **Insider Scoop:** The UAE is a global melting pot.\n😎 **Pro Tip:** You have creative freedom! 'Fireworks' over Burj Khalifa or 'Abstract Gold' are perfect. 'Cool Santa' works for shopping vibes, but keep it secular."
    
    if country == "uae" and audience == "locals":
        return "💡 **Insider Scoop:** For Emiratis, Santa is just a commercial mall character. \n😎 **Pro Tip:** Focus on 'Vision & Prosperity'. Use Skylines or Abstract Art. Frame it as 'Continued Success'. Avoid party vibes."
    
    if country == "ksa" and audience == "locals":
        return "💡 **Insider Scoop:** It's 'Kashta' Time! The desert is their winter wonderland.\n😎 **Pro Tip:** Impress them with 'Desert Starlight'. Coffee pots? Yes. Champagne? NEVER."
    
    if country == "ksa" and audience == "mixed":
        return "💡 **Insider Scoop:** Offices are modernizing but etiquette remains conservative.\n😎 **Pro Tip:** Play it safe. Avoid Santa. Choose 'Skylines' or 'Clocks' to celebrate Vision 2030 and shared goals."

    if country == "kuwait" and audience == "locals":
        return "💡 **Insider Scoop:** A quiet winter break.\n😎 **Pro Tip:** Choose 'Peaceful Winter Atmosphere' or 'Desert'. It respects their privacy and family time."

    if country == "oman" and audience == "locals":
        return "💡 **Insider Scoop:** Serenity over noise. \n😎 **Pro Tip:** Avoid the bling. Choose 'Desert Starlight' or Nature themes. Respect the Omani soul."
    
    # Generalized Logic
    if audience == "eastern_expats":
        return "💡 **Insider Scoop:** The 'Ber' Months! \n😎 **Pro Tip:** 'Lanterns of Hope' (Parol vibe) is a winner. It acts as a universal symbol of joy without risking religious mistakes."
    
    if country == "qatar":
        return "💡 **Insider Scoop:** The 'Maroon' Elegance.\n😎 **Pro Tip:** Skip generic Red. Use 'Abstract' or themes with Maroon & White to blend with National Day pride."
    
    if audience == "western_expats":
        return "💡 **Insider Scoop:** Winter = BBQ Season.\n😎 **Pro Tip:** 'Warm Winter Terrace' captures their reality better than fake snow. Or go 'Christmas Stories' for nostalgia."
    
    if country == "bahrain":
        return "💡 **Insider Scoop:** The Island Vibe.\n😎 **Pro Tip:** Friendly and open! 'Fireworks' or 'Skylines' (World Trade Center) work perfectly."

    return "💡 **Tip:** Remember the Golden Rule of GCC: Be respectful, avoid alcohol imagery, and focus on shared values like prosperity, light, and warmth."

def get_available_topics(audience: str):
    """Фильтрует топики для безопасности"""
    keys = list(TOPICS.keys())
    # Удаляем Christmas для местных и смешанных групп
    if audience in ["locals", "mixed"]:
        if "christmas" in keys:
            keys.remove("christmas")
    return keys

def build_final_prompt(country_code, audience_code, topic_code):
    """Сборка финального промпта для AI"""
    c_data = COUNTRY_AESTHETICS.get(country_code, "")
    a_data = AUDIENCE_RULES.get(audience_code, "")
    t_data = TOPICS[topic_code]["prompt"]
    
    # Инъекция специфических визуалов для стран (из текста ТЗ)
    extra_visuals = ""
    if country_code == "bahrain":
        extra_visuals = "Include subtle visual hints of World Trade Center turbines or sea/pearls elements."
    if country_code == "oman" and topic_code == "desert":
        extra_visuals = "Include rugged mountains in the background, traditional khanjar aesthetic abstractly."
    if country_code == "qatar":
        extra_visuals = "Color palette MUST emphasize Maroon (Burgundy) and White."

    full_prompt = (
        f"{GLOBAL_SAFETY}\n\n"
        f"CONTEXT: Generating a greeting card for {COUNTRIES[country_code]} targetting {AUDIENCES[audience_code]}.\n"
        f"{c_data}\n"
        f"{a_data}\n"
        f"{extra_visuals}\n\n"
        f"IMAGE SUBJECT DESCRIPTION:\n{t_data}\n\n"
        f"Style: Photorealistic, cinematic 8k, highly detailed, cultural respect."
    )
    return full_prompt
