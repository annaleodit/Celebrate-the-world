"""
Содержит тексты, конфигурации кнопок и логику сборки промптов
для создания поздравительных открыток.
"""

# --- CONSTANTS ---
COUNTRIES = {
    "uae": "🇦🇪 ОАЭ",
    "ksa": "🇸🇦 Саудовская Аравия",
    "india": "🇮🇳 Индия",
    "china": "🇨🇳 Китай"
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
NO Chinese cheracters or letters
NO revealing sexualised figures
NO only white and black colours
NO sharp objects like knives
NO pears
NO number 4
TEXT RULES: You may include the year "2026" and specific festive text mentioned in the prompt (such as "Prosperity in Bloom" or "Prosperous New Year 2026"). Do not generate any other text, letters, or numbers.
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
        "btn": "🌌 Космос",
        "desc": "Динамичный футуризм с текущим золотом и голографической фольгой. Космические вихри энергии — символ безграничных возможностей и элегантного прогресса.",
        "prompt": """
Role: Conceptual Luxury Artist & E-card Designer.

Aesthetic & Mood: Visualize a fusion of Dynamic Futurism and Fluid Luxury. The feeling should be one of limitless possibility, rapid evolution, and elegant, unstoppable progress. Think celestial motion rendered with opulent materials. The canvas is a deep, rich matte surface. The primary visual elements are a interplay of molten, flowing liquid gold and shifting, iridescent holographic foil that catches light like nebula dust.

Scene Description: Create an abstract celestial composition that embodies movement into the future. Think of a vortex, a sweeping, organic flow of energy—a cosmic current or pathway made of curving light trails, stardust, and orbital lines that draws the eye forward.
Integrate abstract, cosmic forms within this flow. These could be stylized planetary spheres, shimmering dust clouds, or geometric light or star constructs, all caught in the dynamic current. Orbital rings and small planetary spheres sweep upwards in ellipses, intertwining with each other. Avoid mechanical gears; focus on fluid, organic celestial curves.
The year "2026" should be integrated into the design. It shouldn't just be placed; it should emerge from or be formed by the flowing gold, stardust, or holographic trails, using a sleek, contemporary display typeface that feels like part of the movement. However it should be readable and not fully merged.
"""
    },
    "fireworks": {
        "btn": "🎆 Геометрия света",
        "desc": "Абстрактный узор, напоминающий салют, выполненный чистыми золотыми линиями на темном фоне.",
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
        "btn": "🦅 Сквозь звезды",
        "desc": "Сияющий силуэт сокола на фоне ночного неба. Символ силы, статуса и высоких целей.",
        "prompt": """
Role
You are a premier digital artist creating high-end e-cards with a focus on celestial energy and "digital luxury." Your style combines intricate geometric forms with atmospheric, volumetric lighting effects to create immersive, glowing scenes that feel expensive and advanced.
Style & Aesthetic
The overall impression is one of kinetic celestial energy and opulent digital craftsmanship. The design is composed of golden and warm bronze beams, interconnected glowing nodes, and shimmering stardust particles. These elements emit a powerful, warm volumetric glow against a deep dark, nebular void background (use the Country Aesthetic palette for the void color tone). The light blooms intensely at intersections and along edges, creating a soft, atmospheric haze.
Scene Description
Visualize a magnificent, faceted geometric falcon, constructed as if from interwoven golden light beams and polished bronze filigree, soaring dynamically across the middle-left of the frame. It is a creature of pure energy. As it flies, it leaves a turbulent, sparkling wake of light trails and data particles. This wake flows across the scene and coalesces on the right side to forge the glowing constellation of the year '2026'. The numbers are formed by dense clusters of stars and geometric light connections, appearing as a stellar blueprint brought to life by the falcon's passage.
"""
    },
    "mandala": {
        "btn": "🌼 Цветение",
        "desc": "Лаконичная открытка с крупным рельефным орнаментом в спокойных, приятных глазу тонах.",
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
        "btn": "👑 Сокровища",
        "desc": "Глубокие насыщенные цвета, текстура дорогой ткани и золотое сияние. Традиционно и торжественно.",
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
        "btn": "🌃 Огни мегаполиса",
        "desc": "Динамичный вид ночного города с яркими вспышками. Для тех, кто ценит современный ритм жизни.",
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
        "btn": "🌸 Ветвь удачи",
        "desc": "Классическая цветущая ветвь в красных и золотых тонах. Традиционный символ весны и обновления.",
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
        "btn": "🐟 Поток изобилия",
        "desc": "Современная цифровая интерпретация карпов кои. Яркий и энергичный образ движения вперед.",
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
        "btn": "✨ Искры",
        "desc": "Вариации на тему бенгальского огня. Теплая, уютная и очень личная атмосфера праздника.",
        "prompt": """
Role
You are a world-class designer specializing in luxury Chinese New Year e-card designs with extreme macro photography aesthetics. Your goal is to create intimate, magical, and culturally respectful designs.
Style & Aesthetic
A striking, full-frame macro shot capturing the essence of New Year joy. Close-up on a reaction of golden light and heat, rendered with hyper-realistic optical physics. The focus is on the intricate dance of sparks which look like tiny comets with pearl-like heads, leaving trails of warm exposure light. The background is a luxurious, blurry city, bokeh and wash of dark wine-reds and deep shadow, making the gold pop with intense contrast. The image is borderless and cinematic. The year "2026" is written in the air with long-exposure light painting, continuing the spark pattern. Stylish, festive, non-traditional, masterpiece quality. The feeling is personal joy and holding happiness in one's hands.
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
        return "💡 Рекомендации:\n- ОАЭ это котел культур. В Дубае символы католического рождества повсюду. Но в других Эмиратах их гораздо меньше или нет вовсе.\n- В поздравлениях избегайте упоминания Рождества и религиозных символов, придерживайтесь поздравлений с Новым годом.\n- Этот бот сейчас умеет делать открытки для Эмирати или смешанных групп. Но помните, что в ОАЭ живет огромное число экспатов и они могут иметь свои особые традиции. Например, большинство Филиппинцев празднуют рождество 25-го декабря, также как европейцы или американцы, но со своими атрибутами и символами."

    # KSA
    if country == "ksa":
        return "💡 Рекомендации:\n- Саудовская Аравия - страна глубоких исламских традиций, но быстрых перемен. Рождество здесь не празднуют, и поздравлять с ним местных партнеров нельзя.\n- 1 января не является официальным народным праздником, но в бизнес-среде и крупных городах к нему относятся лояльно, часто в контексте фестиваля Riyadh Season.\n- Для поздравления используйте нейтральные формулировки про Новый год без религиозного подтекста и упоминаний или изображений алкоголя."

    # India
    if country == "india":
        return "💡 Рекомендации:\n- Западный Новый год отмечают в основном в крупных городах и бизнес среде.\n- В каждом штате Индии отмечают свой индуистский или другой традиционный новый год, спросите вашего коллегу из какого он штата и какой праздник для него - Новый год. Не забудьте поздравить его в соответствующую дату.\n- Индия - невероятно разнообразная в языковом смысле страна, поэтому мы рекомендуем ограничиться английским, так как не известно, владеет ли ваш коллега хинди, тамильским или керала."

    # China
    if country == "china":
        return "💡 Рекомендации:\n- В Китае Новый год это второстепенный праздник по сравнению с Лунным новым годом. В 2026 году Лунный новый год выпадает на 17 февраля, а праздники продлятся с 16 февраля до 3 марта. Обязательно поздравьте ваших коллег с Лунным новым годом.\n- Новый год в западном стиле отмечают только в крупных городах.\n- Не поздравляйте ваших китайских коллег с Рождеством, даже если они проживают на западе."

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
    import json
    import os
    
    # #region agent log
    # Debug logging (опционально, только для локальной разработки)
    DEBUG_LOG_ENABLED = os.getenv("DEBUG_LOG_ENABLED", "false").lower() == "true"
    if DEBUG_LOG_ENABLED:
        DEBUG_LOG_PATH = os.path.join(os.getcwd(), ".cursor", "debug.log")
        try:
            log_dir = os.path.dirname(DEBUG_LOG_PATH)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "C",
                "location": "text_content.py:227",
                "message": "build_final_prompt ENTRY",
                "data": {"country_code": country_code, "topic_code": topic_code},
                "timestamp": 0
            }
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Игнорируем ошибки логирования
    # #endregion
    
    # ВАЛИДАЦИЯ входных параметров (гипотеза C)
    if country_code not in COUNTRIES:
        raise ValueError(f"Invalid country_code: {country_code}")
    if topic_code not in TOPICS:
        raise ValueError(f"Invalid topic_code: {topic_code}")
    
    # #region agent log
    if DEBUG_LOG_ENABLED:
        try:
            avail_topics = get_available_topics(country_code)
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "C",
                "location": "text_content.py:245",
                "message": "build_final_prompt VALIDATION",
                "data": {"country": country_code, "topic": topic_code, "available_topics": avail_topics, "is_valid": topic_code in avail_topics},
                "timestamp": 0
            }
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Игнорируем ошибки логирования
    # #endregion
    
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
