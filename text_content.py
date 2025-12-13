"""
Содержит тексты, конфигурации кнопок и логику сборки промптов
для создания поздравительных открыток.
"""

# --- CONSTANTS ---
COUNTRIES = {
    "uae": "🇦🇪 UAE",
    "ksa": "🇸🇦 Saudi Arabia",
    "india": "🇮🇳 India",
    "china": "🇨🇳 China"
}

# --- PROMPT PARTS ---
GLOBAL_SAFETY = """
GLOBAL SAFETY PROTOCOL (UAE & KSA):
STRICTLY NO ALCOHOL: No wine glasses, champagne flutes, or cocktail shakers. Use abstract cups, tea cups, or geometric tumblers only.
NO FEMALE REPRESENTATION: To ensure cultural compliance, do not depict human female figures.
RELIGION: No religious symbols (crosses, angels, saints).
FOCUS: Primary focus is secular "New Year". STRICTLY NEW YEAR / SEASONAL ONLY. NO Christmas symbols (trees, Santa Claus). Use confetti, golden lights, fireworks.
TEXT RULES: Do not generate any text, letters, or numbers UNLESS explicitly asked for the year "2026". Apart from "2026", avoid any other text.
NO GLASSES: MUST NOT use glasses with drinks to avoid confusion with wine only tea and coffee are acceptable.
HUMAN FIGURES: NO DISTINCT people or hands or other parts of human body. Women MUST be avoided or at least fully covered/abaya when used as silhouettes.
NO ZODIAK signs, strictly not allowed.
STRICTLY NO skyscrapers or city skylines allowed unless specified in the topic.
"""

GLOBAL_SAFETY_INDIA = """
GLOBAL SAFETY INDIA:
NO people in the images
TEXT RULES: Do not generate any text, letters, or numbers UNLESS explicitly asked for the year "2026". Apart from "2026", avoid any other text.
NO images of cows or bulls
NO images of pigs or pork
NO alcohol in the images
NO Christian religious symbols
NO sexuality
"""

GLOBAL_SAFETY_CHINA = """
GLOBAL SAFETY CHINA:
NO Christian religious symbols
NO revealing sexualised figures
NO only white and black colours
NO sharp objects like knives
NO pears
NO number 4
"""

COUNTRY_AESTHETICS = {
    "uae": "Aesthetic: 'Future Heritage.' Fusion of hyper-modern architecture and warm golden-hour lighting. Polished glass, steel, and gold textures. Vibe: Limitless ambition, cosmopolitan luxury. Color Palette: Gold, White, Silver, Warm Beige.",
    "ksa": "Aesthetic: Deep, rich, and regal. Blend of historic mud-brick architecture or desert landscapes with sleek modernity. Vibe: Dignity, warmth, hospitality. Color Palette: Sand, Terracotta, Deep Gold, Midnight Blue.",
    "india": "Aesthetic: Rich, luxurious, and culturally sophisticated. Blend of traditional Indian design elements with contemporary luxury. Vibe: Opulent, celebratory, refined. Color Palette: Royal jewel tones (Rani Pink, Midnight Blue, Emerald Green), Gold, Cream, Taupe, Blush Pink.",
    "china": "Aesthetic: Luxury, modern, festive, focused on future. Focus on prosperity and happiness. Color Palette: Deep red velvet, dark cherry red, gold."
}

# --- TOPICS (FINALIZED PROMPTS) ---
TOPICS = {
    "time": {
        "btn": "🕰 Почти полночь",
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
        "btn": "🎆 Салют и арабески",
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
        "btn": "🦅 Ночной сокол",
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
    "mandala": {
        "btn": "🌼 Мандала",
        "desc": "A minimalist New Year 2026 digital design featuring a unique mandala design. Best for: India.",
        "prompt": """
Role
You are a world-class designer specializing in luxury full-screen digital artwork with Indian design aesthetics. Your goal is to create sophisticated, elegant, and culturally respectful designs.
Style & Aesthetic
A minimalist New Year 2026 full-screen digital artwork featuring a unique mandala design, inspired by Sanjay Garg, Nicobar, Anavila Misra. The design uses thick, textured visual elements in shades of these colors (pick one): cream, taupe, blush pink, and deep blue, swirled background of deep blue and pink. Techniques include visual effects simulating blind embossing, gold foil stamping, copper foil stamping, and debossing to create intricate mandala motifs. The design is fine and contemporary, always featuring mandala as the key element or as floral background or on the left with text on the right. Simple, elegant text says "HAPPY NEW YEAR 2026," and in smaller letters "Wishing you a Happy and Prosperous New Year". The text appears as if printed or foiled. The overall aesthetic is sophisticated, clean, and luxurious.
CRITICAL COMPOSITION REQUIREMENTS:
- The image must be EDGE-TO-EDGE. NO white borders, NO margins, NO frames, NO physical card edges visible.
- The design must fill 100% of the canvas from edge to edge.
- NO negative space around the design. The background color/texture must extend to all edges.
- This is a full-screen digital artwork, NOT a photograph of a physical card. The entire canvas IS the design itself.
"""
    },
    "modern_royal": {
        "btn": "👑 Королевский стиль",
        "desc": "A hyper-luxurious, high-end New Year 2026 digital design designed by Sabyasachi and Manish Malhotra. Best for: India.",
        "prompt": """
Role
You are a world-class designer specializing in hyper-luxurious full-screen digital artwork with Indian royal aesthetics. Your goal is to create opulent, majestic, and culturally sophisticated designs.
Style & Aesthetic
A hyper-luxurious, high-end New Year 2026 full-screen digital artwork designed by Sabyasachi and Manish Malhotra. Center stage is the text 'Happy New Year 2026' written in majestic, custom 3D gold-leaf typography with intricate filigree details. The text floats against a deep, rich background of royal jewel tones (pick one): Rani Pink, Midnight Blue, and Emerald Green or swirled background of these 3 colors. The background also features a dense, seamless pattern of animated gold dust, sequins, and Zardozi embroidery textures. No white space. The lighting is cinematic and dramatic, creating a shimmering 'bokeh' effect that looks like falling diamonds and soft fireworks. The aesthetic is 'Modern Indian Royal', combining traditional grandeur with contemporary graphic design. Ultra-detailed, 8k resolution, metallic foil texture, photorealistic luxury paper finish.
CRITICAL COMPOSITION REQUIREMENTS:
- The image must be EDGE-TO-EDGE. NO white borders, NO margins, NO frames, NO physical card edges visible.
- The design must fill 100% of the canvas from edge to edge.
- NO negative space around the design. The background color/texture must extend to all edges.
- This is a full-screen digital artwork, NOT a photograph of a physical card. The entire canvas IS the design itself.
"""
    },
    "urban_vibes": {
        "btn": "🌃 Вечеринка в городе",
        "desc": "A luxurious, high-end New Year digital design embodying a sophisticated urban celebration. Best for: India.",
        "prompt": """
Role
You are a world-class designer specializing in luxury urban-themed full-screen digital artwork. Your goal is to create sophisticated, energetic, and aspirational designs.
Style & Aesthetic
A luxurious, high-end New Year full-screen digital artwork embodying a sophisticated urban celebration. The design features a stylized city skyline as its foundation, illuminated by dynamic, vibrant light streaks in deep jewel tones. From the heart of this metropolitan landscape, an opulent burst of effervescent gold and platinum, resembling liquid metal, elegantly erupts. This central explosion is interwoven with shimmering confetti and subtle, delicate forms suggestive, ascending towards the top. A hint of celebratory sparkle and bubbles is integrated into the design. The overall aesthetic is one of refined energy and aspirational luxury. The prominent New Year message is crafted in a 3D gold-leaf typography, subtly, anchored at the design's base. The composition is cinematic and ultra-detailed, showcasing rich metallic foil textures, a high-gloss finish, and photorealistic luxury quality, with no negative space. The lighting creates a dramatic, celebratory glow, evoking a grand urban toast.
CRITICAL COMPOSITION REQUIREMENTS:
- The image must be EDGE-TO-EDGE. NO white borders, NO margins, NO frames, NO physical card edges visible.
- The design must fill 100% of the canvas from edge to edge.
- NO negative space around the design. The background color/texture must extend to all edges.
- This is a full-screen digital artwork, NOT a photograph of a physical card. The entire canvas IS the design itself.
"""
    },
    "prosperity": {
        "btn": "🌸 Процветание",
        "desc": "Elegant festive design featuring a plum blossom branch in rich red and gold. Best for: China.",
        "prompt": """
Role
You are a world-class designer specializing in luxury Chinese New Year e-card designs. Your goal is to create elegant, festive, and culturally respectful designs.
Style & Aesthetic
Elegant festive design featuring a plum blossom branch in a rich red and gold color scheme. The branch is crafted from polished gold, adorned with blossoms made of ruby and rose quartz crystals or delicate gold outlines. Explosive gold and red fireworks illuminate the scene, potentially forming abstract patterns. Each card should include the festive text "2026". The background is a deep red velvet or textured paper, creating a luxurious and celebratory atmosphere. Includes the text 'Prosperity in Bloom' in elegant gold script. High resolution, ornate, detailed, cinematic lighting.
CRITICAL COMPOSITION REQUIREMENTS:
- The image must be EDGE-TO-EDGE. NO white borders, NO margins, NO frames, NO physical card edges visible.
- The design must fill 100% of the canvas from edge to edge.
- NO negative space around the design. The background color/texture must extend to all edges.
- This is a full-screen digital artwork, NOT a photograph of a physical card. The entire canvas IS the design itself.
"""
    },
    "abundance": {
        "btn": "🐟 Изобилие",
        "desc": "Hyper-luxurious Chinese New Year 2026 e-card with 'Modern China Vibe' featuring Cyber-Koi fish. Best for: China.",
        "prompt": """
Role
You are a world-class designer specializing in hyper-luxurious Chinese New Year e-card designs with modern digital aesthetics. Your goal is to create sophisticated, fluid, and culturally respectful designs.
Style & Aesthetic
A hyper-luxurious, high-end Chinese New Year 2026 e-card, with a 'Modern China Vibe'. The central visual features two stylized 'Cyber-Koi' fish, depicted as luminous forms of liquid gold or glowing neon data streams. They convey dynamic movement, leaving behind shimmering trails of golden particles and subtle light streaks, emphasizing flow and digital elegance.
The background is a deep, rich Dark Cherry red or dark Imperial Violet purple, subtly textured with abstract digital patterns. The overall aesthetic is sophisticated and fluid, symbolizing unimpeded energy flow.
The text 'Prosperous New Year 2026' is elegantly integrated into the composition, rendered in glowing gold or luminous neon typography. The design is balanced, with cinematic lighting creating a sense of luxury and depth. Ultra-detailed, high resolution, with metallic and holographic textures, and a photorealistic luxury paper finish. Focus on abstract, digital, flowing forms of the Koi.
CRITICAL COMPOSITION REQUIREMENTS:
- The image must be EDGE-TO-EDGE. NO white borders, NO margins, NO frames, NO physical card edges visible.
- The design must fill 100% of the canvas from edge to edge.
- NO negative space around the design. The background color/texture must extend to all edges.
- This is a full-screen digital artwork, NOT a photograph of a physical card. The entire canvas IS the design itself.
"""
    },
    "light_happiness": {
        "btn": "✨ Свет и радость",
        "desc": "Luxurious Chinese New Year e-card with extreme macro photography of a lit golden sparkler. Best for: China.",
        "prompt": """
Role
You are a world-class designer specializing in luxury Chinese New Year e-card designs with extreme macro photography aesthetics. Your goal is to create intimate, magical, and culturally respectful designs.
Style & Aesthetic
A luxurious Chinese New Year e-card design, extreme macro photography style. A close-up view of a lit golden sparkler (bengal light) burning intensely. The core is molten gold. Branching, crystalline golden sparks fly intensely outwards and upwards, creating a feathery, organic pattern of light. The very tips of the branching sparks terminate in tiny, soft glowing pearl-like spheres before fading, creating a magical, jewel-like effect. The background is a dark, rich, blurred bokeh of deep reds and gold lights, very intimate and warm. The year "2026" is subtly formed by the trailing light of the sparkler. The feeling is personal joy and holding magic in one's hands.
CRITICAL COMPOSITION REQUIREMENTS:
- The image must be EDGE-TO-EDGE. NO white borders, NO margins, NO frames, NO physical card edges visible.
- The design must fill 100% of the canvas from edge to edge.
- NO negative space around the design. The background color/texture must extend to all edges.
- This is a full-screen digital artwork, NOT a photograph of a physical card. The entire canvas IS the design itself.
"""
    }
}

# --- LOGIC HELPERS ---

def get_tips(country: str) -> str:
    """Возвращает экспертный совет на основе страны"""
    # UAE
    if country == "uae":
        return "💡 **Рекомендации:** Для эмиратцев фокус на Видении и Процветании.\n😎 **Профессиональный совет:** 'Сокол' или 'Почти полночь' - отличный уважительный выбор. Избегайте упоминания вечеринок или Рождества, придерживайтесь Поздравлений с сезоном или Новым годом."

    # KSA
    if country == "ksa":
        return "💡 **Рекомендации:** Офисы модернизируются, но этикет остается консервативным.\n😎 **Профессиональный совет:** Темы 'Почти полночь' или 'Ночной сокол' - безопасный, премиальный выбор для ваших поздравлений. Избегайте упоминания вечеринок или Рождества, придерживайтесь Поздравлений с сезоном или Новым годом."

    # India
    if country == "india":
        return "💡 **Рекомендации:** Индийская культура ценит роскошь и традиции.\n😎 **Профессиональный совет:** Темы 'Мандала', 'Королевский стиль' или 'Вечеринка в городе' - отличный выбор для индийских получателей. Все темы учитывают культурные особенности и безопасность."

    # China
    if country == "china":
        return "💡 **Рекомендации:** В Китае Новый год — это второстепенный праздник по сравнению с Лунным новым годом. В 2026 году он выпадает на 17 февраля, а праздники продлятся с 16 февраля до 3 марта. Обязательно поздравьте ваших коллег с Лунным новым годом.\n💡 Новый год в западном стиле отмечают только в крупных городах.\n💡 Не поздравляйте ваших китайских коллег с Рождеством, даже если они проживают на западе.\n😎 **Профессиональный совет:** Темы 'Процветание', 'Изобилие' или 'Свет и радость' - отличный выбор для китайских получателей. Все темы учитывают культурные особенности и безопасность."

    return "💡 **Совет:** Помните золотое правило: Будьте уважительны, исключайте изображения алкоголя и религиозные элементы, фокусируйтесь на общих ценностях, таких как процветание, свет и тепло."

def get_available_topics(country: str):
    """Возвращает доступные топики в зависимости от страны"""
    if country == "india":
        # Для Индии: mandala, modern_royal, urban_vibes
        return ["mandala", "modern_royal", "urban_vibes"]
    elif country == "china":
        # Для Китая: prosperity, abundance, light_happiness
        return ["prosperity", "abundance", "light_happiness"]
    else:
        # Для UAE и KSA: time, fireworks, falcon
        return ["time", "fireworks", "falcon"]

def build_final_prompt(country_code, topic_code):
    """Сборка финального промпта для AI"""
    
    # 1. Достаем данные
    c_data = COUNTRY_AESTHETICS.get(country_code, "")
    t_data = TOPICS[topic_code]["prompt"]
    
    # 2. Выбираем правильный safety protocol в зависимости от страны
    if country_code == "india":
        safety_protocol = GLOBAL_SAFETY_INDIA
    elif country_code == "china":
        safety_protocol = GLOBAL_SAFETY_CHINA
    else:
        safety_protocol = GLOBAL_SAFETY
    
    # 3. Контекст страны
    country_context = c_data

    # 4. Структура: Subject -> Colors (Country) -> Safety
    
    full_prompt = (
        f"--- ROLE & TASK ---\n"
        f"{t_data}\n\n"
        
        f"--- COLOR PALETTE & SETTING ---\n"
        f"Country Context: {country_context}\n"
        f"Use the Color Palette of {COUNTRIES[country_code]}.\n\n"
        
        f"--- TECHNICAL CONSTRAINTS & SAFETY ---\n"
        f"VIEW: Full-screen digital art, edge-to-edge. NO physical card on a table. No borders.\n"
        f"{safety_protocol}"
    )
    
    return full_prompt
