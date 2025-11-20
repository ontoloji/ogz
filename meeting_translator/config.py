"""
Yapılandırma ayarları
"""
import os

class Config:
    # Ses ayarları
    SAMPLE_RATE = 16000  # Whisper için optimize edilmiş
    CHUNK_DURATION = 3  # Saniye cinsinden ses parçası süresi
    CHANNELS = 1  # Mono

    # Whisper modeli ayarları
    WHISPER_MODEL = "base"  # tiny, base, small, medium, large
    WHISPER_LANGUAGE = "en"  # İngilizce olarak algıla

    # Çeviri ayarları
    SOURCE_LANG = "en"
    TARGET_LANG = "tr"

    # Altyazı ayarları
    SUBTITLE_FONT_SIZE = 24
    SUBTITLE_BG_COLOR = "#000000"
    SUBTITLE_TEXT_COLOR = "#FFFFFF"
    SUBTITLE_OPACITY = 0.7
    SUBTITLE_POSITION = "bottom"  # bottom, top
    SUBTITLE_WIDTH = 800
    SUBTITLE_HEIGHT = 150

    # Diğer ayarlar
    MIN_AUDIO_LENGTH = 0.5  # Minimum ses uzunluğu (saniye)
    SILENCE_THRESHOLD = 500  # Sessizlik eşiği

    # API Anahtarları (gerekirse)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
