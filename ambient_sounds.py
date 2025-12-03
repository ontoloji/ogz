"""
Ambient Noise Ses Dosyaları Listesi
30 farklı ambient/doğa sesi

Ses dosyaları sounds/ klasöründe olmalı
Format: MP3 veya OGG (loop için optimize)
"""

AMBIENT_SOUNDS = {
    # Doğa Sesleri
    "rain": {"name": "Yağmur", "file": "rain.mp3", "category": "nature", "icon": "🌧️"},
    "thunder": {"name": "Gök Gürültüsü", "file": "thunder.mp3", "category": "nature", "icon": "⚡"},
    "wind": {"name": "Rüzgar", "file": "wind.mp3", "category": "nature", "icon": "💨"},
    "ocean": {"name": "Okyanus Dalgaları", "file": "ocean.mp3", "category": "nature", "icon": "🌊"},
    "river": {"name": "Nehir", "file": "river.mp3", "category": "nature", "icon": "〰️"},
    "waterfall": {"name": "Şelale", "file": "waterfall.mp3", "category": "nature", "icon": "💧"},
    "forest": {"name": "Orman", "file": "forest.mp3", "category": "nature", "icon": "🌲"},
    "birds": {"name": "Kuş Sesleri", "file": "birds.mp3", "category": "nature", "icon": "🐦"},
    "crickets": {"name": "Cırcırböceği", "file": "crickets.mp3", "category": "nature", "icon": "🦗"},
    "fire": {"name": "Ateş", "file": "fire.mp3", "category": "nature", "icon": "🔥"},

    # Ambient/Beyaz Gürültü
    "white_noise": {"name": "Beyaz Gürültü", "file": "white_noise.mp3", "category": "ambient", "icon": "⬜"},
    "brown_noise": {"name": "Kahverengi Gürültü", "file": "brown_noise.mp3", "category": "ambient", "icon": "🟫"},
    "pink_noise": {"name": "Pembe Gürültü", "file": "pink_noise.mp3", "category": "ambient", "icon": "🌸"},
    "fan": {"name": "Vantilatör", "file": "fan.mp3", "category": "ambient", "icon": "🌀"},
    "clock": {"name": "Saat Tik Tak", "file": "clock.mp3", "category": "ambient", "icon": "🕐"},
    "wind_chimes": {"name": "Rüzgar Çanları", "file": "wind_chimes.mp3", "category": "ambient", "icon": "🎐"},
    "coffee_shop": {"name": "Kafe", "file": "coffee_shop.mp3", "category": "ambient", "icon": "☕"},
    "library": {"name": "Kütüphane", "file": "library.mp3", "category": "ambient", "icon": "📚"},
    "train": {"name": "Tren", "file": "train.mp3", "category": "ambient", "icon": "🚂"},
    "airplane": {"name": "Uçak", "file": "airplane.mp3", "category": "ambient", "icon": "✈️"},

    # Rahatlama Sesleri
    "night": {"name": "Gece Sesleri", "file": "night.mp3", "category": "relax", "icon": "🌙"},
    "campfire": {"name": "Kamp Ateşi", "file": "campfire.mp3", "category": "relax", "icon": "🏕️"},
    "cat_purr": {"name": "Kedi Mırıltısı", "file": "cat_purr.mp3", "category": "relax", "icon": "🐱"},
    "fireplace": {"name": "Şömine", "file": "fireplace.mp3", "category": "relax", "icon": "🪵"},
    "shower": {"name": "Duş", "file": "shower.mp3", "category": "relax", "icon": "🚿"},
    "fountain": {"name": "Çeşme", "file": "fountain.mp3", "category": "relax", "icon": "⛲"},
    "frogs": {"name": "Kurbağalar", "file": "frogs.mp3", "category": "relax", "icon": "🐸"},
    "seagulls": {"name": "Martılar", "file": "seagulls.mp3", "category": "relax", "icon": "🦅"},
    "beach": {"name": "Sahil Dalgaları", "file": "beach.mp3", "category": "relax", "icon": "🏖️"},
    "underwater": {"name": "Su Altı", "file": "underwater.mp3", "category": "relax", "icon": "🌊"},
}

# Kategori renkleri
CATEGORY_COLORS = {
    "nature": "#4CAF50",  # Yeşil
    "ambient": "#2196F3",  # Mavi
    "relax": "#9C27B0",   # Mor
}

# Ses dosyaları klasörü
SOUNDS_DIR = "sounds"
