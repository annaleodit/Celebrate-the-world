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
NO FEMALE REPRESENTATION: To ensure cultural compliance, do not depict human female figures. Use abstract silhouettes, hands only, or focus on objects/scenery.
RELIGION: No religious symbols (crosses, angels, saints).
FOCUS: Primary focus is secular "New Year". If "Christmas" is requested, use seasonal winter aesthetics (snow, trees, lights) instead of religious icons. NO Santa Claus except for Western and Eastern expatriate audience and only if explicitly requested in the user prompt. Santa Claus must be depicted as a fun, non-religious fairytale mascot (e.g., wearing sunglasses, carrying shopping bags, or in a futuristic sleigh). NO traditional St. Nicholas religious styling.
NO TEXT: Do not generate any text, letters, or numbers on the image. Pure visual art only.
NO GLASSES: MUST NOT use glasses with drinks to avoid confusion with wine only tea and coffee are acceptable.
NO DISTINCT people or hands or other parts of human body, only silhouettes are acceptable, women MUST be avoided or at least covered when used as silhouettes.
NO ZODIAK signs, strictly not allowed.
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

# --- TOPICS (FINALIZED PROMPTS) ---
TOPICS = {
    "time": {
        "btn": "🕰 Time & Constellations",
        "desc": "A sophisticated celestial-themed illustration featuring '2026' formed by glowing constellations. Best for: Business Partners & Visionaries.",
        "prompt": """
Role
You are a world-class illustrator specializing in sophisticated, celestial-themed luxury art. Your goal is to create a precise, elegant, and mystical geometric illustration featuring high-contrast metallics and glowing elements.
Style & Aesthetic
The overall aesthetic is elegant, mystical, and geometric, featuring high-contrast variations of gold and silver on deep navy or charcoal blue, with precise, thin line work and a subtle glowing effect.
The background is a deep, rich midnight blue or blue-maroon or blue-deep green with slight variations in depth and tone. Rich maroon and rich green can be used on the background if triggered by an additional prompt.
Scene Description
A sophisticated celestial-themed illustration featuring the year "2026" in the center, where the numbers are formed by glowing constellations with connected star nodes and gemstones. The year '2026' is formed by a dense, geometric constellation network. Prominent, brilliant star nodes are interconnected by thicker, continuous bands of light, creating a subtle glowing lattice. The entire structure has a subtle white glow, making the numbers appear as unified celestial forms.
Surrounding the text is a complex, symmetrical array of fine golden concentric circles and intersecting elliptical orbits of different radius. The lines crisscross and overlap each other, creating a "web" or "net" effect and mimic the chaotic but symmetrical motion of an atom or a gyroscope. Scattered throughout the orbits are small stylized planets gold or colored with luxury textures, with rings and geometric four-pointed stars. Some planets and stars are decorated with colored gemstones and jewels.
"""
    },
    "fireworks": {
        "btn": "🎆 Luxury Fireworks",
        "desc": "Clean, expensive, and structurally precise geometric fireworks. Best for: Mixed Groups & Locals.",
        "prompt": """
Role
You are a high-end graphic designer specializing in luxury vector illustrations and typography for premium greeting cards. Your aesthetic is clean, expensive, structurally precise, and influenced by modern geometric patterns and high-contrast metallic textures.
Style & Aesthetic
No organic sparks or smoke; the aesthetic is clean, expensive, and structurally precise, influenced by modern Islamic geometry. The entire design, including the text, is rendered in luxurious polished gold and brushed copper foil textures, with optional accents of brushed silver foil.
The background is a deep, matte dark tone (midnight blue or rich charcoal or charcoal blue). Rich maroon and rich green can be used on the background instead of blue and charcoal or in a mix, if triggered by an additional prompt.
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
The overall impression is one of celestial energy and digital luxury. The design is composed of golden and bronze beams, connecting points, and shimmering stardust particles on background that emit a warm, volumetric glow against a deep dark, nebular void background. The light blooms at intersections, creating an atmospheric effect.
Scene Description
A high-end e-card featuring a geometric falcon soaring the air in the left or middle part of the image and the year '2026' rendered as a glowing constellation of light.
"""
    },
    "kashta": {
        "btn": "⛺ Kashta (Desert Night)",
        "desc": "Cinematic desert camping scene under the stars. Best for: Locals (KSA, Kuwait) & Authentic vibes.",
        "prompt": """
Role & Style
You are a world-class commercial photographer specializing in luxury travel and mystical landscapes. Your goal is to create cinematic, high-budget photographs with a magical, premium feel, inspired by "1001 Arabian Nights." BUT STRICTLY NO CRESCENT MOON, ONLY FULL MOON ALLOWED.
Lighting: Cinematic and dramatic deep night or "blue hour." High contrast. Use warm, golden artificial lights (lanterns, magic glow) against deep cool blues and indigos of the sky and shadows.
Color Palette: Rich and deep. Dominant colors are deep indigo/navy blue and warm gold/copper/orange.
Texture & Scale: Emphasize the tactile nature of sand ripples and the vast, majestic scale of the dunes. The images must feel expensive and immersive.
Fidelity: Photorealistic magic realism. Not a cartoon.
Scene Description
A perspective looking up a sand dune at deep night. Other dunes and sands in the distance, sideways. At the very peak of the dune, a single large kashta tent glows intensely with warm welcoming light and is decorated with christmas-tree-like lights.
Above the tent, the deep night sky is filled with stars or FULL moon that form a swirling, galaxy-like spiral pattern. The way up the dune slope towards the tent is shown with small warm lights. “SEASONAL GREETINGS 2026” is rendered in elegant lightweight fonts, slight glow as a separate layer over the image, not part of it. Modestly in a corner without overlapping key elements of the picture.
"""
    },
    "christmas_eve": {
        "btn": "🎄 Christmas Terrace",
        "desc": "A cozy villa terrace overlooking the desert, decorated for Christmas. Best for: Western Expats ONLY.",
        "prompt": """
Role & Style
You are a world-class photographer specializing in luxury travel and mystical landscapes. Your goal is to create cinematic, high-budget photographs with a magical, premium feel, inspired by "1001 Arabian Nights." BUT STRICTLY NO CRESCENT MOON, ONLY FULL MOON ALLOWED.
Lighting: Cinematic and dramatic deep night or "blue hour." High contrast. Use warm, golden artificial lights (lanterns, magic glow) against deep cool blues and indigos of the sky and shadows.
Color Palette: Rich and deep. Dominant colors are deep indigo/navy blue and warm gold/copper/orange.
Texture & Scale: Emphasize the tactile nature of sand ripples and the vast, majestic scale of the dunes. The images must feel expensive and immersive.
Fidelity: Photorealistic magic realism. Not a cartoon.
Scene Description
Terrace of a villa in one of the GCC countries with a rich garden in front, but overlooking a desert. The view is from inside the house or from terrace entrance. This is an expatriate home, so it is decorated for Christmas and the Christmas tree is on the terrace. Also sofa, pillows. The terrace is warm and cozy, decorated in European style. Warm light, a lot of bokeh, Christmas setting. STRICTLY NO RAMADAN FANOUS. Magical, shimmering particles resembling snow or stardust are falling from the starry skies on the terrace. “SEASONAL GREETINGS 2026” is rendered in elegant lightweight fonts, slight glow as a separate layer over the image, not part of it. Modestly in a corner without overlapping key elements of the picture.
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
        return "💡 **Insider Scoop:** The UAE is a global melting pot.\n😎 **Pro Tip:** 'Luxury Fireworks' or 'Time & Constellations' work perfectly here. They are sophisticated and neutral."
    if country == "uae" and audience == "locals":
        return "💡 **Insider Scoop:** For Emiratis, focus on Vision & Prosperity.\n😎 **Pro Tip:** 'Falcon' or 'Time' (Constellations) are excellent respectful choices. Avoid party vibes."

    # KSA
    if country == "ksa" and audience == "locals":
        return "💡 **Insider Scoop:** It's 'Kashta' Time! The desert is their winter wonderland.\n😎 **Pro Tip:** Impress them with the 'Kashta' theme. It hits right in the heart."
    if country == "ksa" and audience == "mixed":
        return "💡 **Insider Scoop:** Offices are modernizing but etiquette remains conservative.\n😎 **Pro Tip:** 'Time & Constellations' or 'Falcon' are safe, premium choices celebrating 2026."

    # Kuwait
    if country == "kuwait" and audience == "locals":
        return "💡 **Insider Scoop:** A quiet winter break.\n😎 **Pro Tip:** 'Kashta' or 'Time' themes respect their privacy and love for the desert winter."

    # Oman
    if country == "oman" and audience == "locals":
        return "💡 **Insider Scoop:** Serenity over noise.\n😎 **Pro Tip:** 'Falcon' or 'Time' fit the Omani values of dignity and nature."
    
    # Generalized Audiences
    if audience == "eastern_expats":
        return "💡 **Insider Scoop:** The 'Ber' Months!\n😎 **Pro Tip:** 'Parol Lantern' is a winner. It acts as a universal symbol of joy and home."
    
    if audience == "western_expats":
        return "💡 **Insider Scoop:** Winter = BBQ Season.\n😎 **Pro Tip:** 'Christmas Terrace' captures their ideal Gulf winter evening."
    
    if country == "qatar":
        return "💡 **Insider Scoop:** Maroon Elegance.\n😎 **Pro Tip:** Themes like 'Time' or 'Fireworks' work well. The AI will try to respect the local palette."
    
    if country == "bahrain":
        return "💡 **Insider Scoop:** The Island Vibe.\n😎 **Pro Tip:** Friendly and open! 'Fireworks' are very welcome here."

    return "💡 **Tip:** Remember the Golden Rule of GCC: Be respectful, avoid alcohol imagery, and focus on shared values like prosperity, light, and warmth."

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
    """Сборка финального промпта для AI"""
    c_data = COUNTRY_AESTHETICS.get(country_code, "")
    a_data = AUDIENCE_RULES.get(audience_code, "")
    t_data = TOPICS[topic_code]["prompt"]
    
    # Инъекция специфических визуалов (минимальная, так как новые промпты очень полные)
    extra_visuals = ""
    if country_code == "qatar":
        extra_visuals = "Color palette MUST emphasize Maroon (Burgundy) and White where appropriate."

    full_prompt = (
        f"{GLOBAL_SAFETY}\n\n"
        f"CONTEXT: Generating a greeting card for {COUNTRIES[country_code]} targetting {AUDIENCES[audience_code]}.\n"
        f"{c_data}\n"
        f"{a_data}\n"
        f"{extra_visuals}\n\n"
        f"--- IMAGE GENERATION TASK ---\n{t_data}"
    )
    return full_prompt
