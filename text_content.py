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
HUMAN FIGURES: NO DISTINCT people or hands or other parts of human body. Only abstract silhouettes are acceptable if necessary, women MUST be avoided or at least fully covered/abaya when used as silhouettes.
NO ZODIAK signs, strictly not allowed.
STRICTLY NO skyscrapers or city skylines allowed unless specified in the topic.
"""

COUNTRY_AESTHETICS = {
    "uae": "Aesthetic: 'Future Heritage.' Fusion of hyper-modern architecture and warm golden-hour lighting. Polished glass, steel, and gold textures. Vibe: Limitless ambition, cosmopolitan luxury. Color Palette: Gold, White, Silver, Warm Beige.",
    "ksa": "Aesthetic: Deep, rich, and regal. Blend of historic mud-brick architecture or desert landscapes with sleek modernity. Vibe: Dignity, warmth, 'Kashta' hospitality. Color Palette: Sand, Terracotta, Deep Gold, Midnight Blue.",
    "qatar": "Aesthetic: Artistic and architectural refinement. Geometric patterns, calligraphy, clean lines. Vibe: National pride, sophistication. Color Palette: Dominant Maroon (Burgundy) and White.",
    "kuwait": "Aesthetic: Maritime and mercantile. Sea, dhows, 'Chalet' lifestyle. Strict Restrictions: Family-centric, private. Vibe: Old Money feel, peaceful. Color Palette: Azure Blue, Sand, White, Gold.",
    "bahrain": "Aesthetic: Island city life. Iconic wind-turbine world trade center, pearl diving heritage. Vibe: Breezy, liberal, social. Visuals: Sea, pearls, sunset. Color Palette: Coral, Pearl White, Red, Blue.",
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
CRITICAL: The clock hands are indicating 11:55 (five minutes to midnight). The countdown is almost over.
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
- IF KSA/Kuwait/UAE: The setting is majestic sand dunes.

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
You are a world-class photographer specializing in luxury travel and mystical landscapes. Your goal is to create cinematic, high-budget photographs with a
