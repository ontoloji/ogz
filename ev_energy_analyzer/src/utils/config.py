"""
Konfigürasyon ve sabit değerler modülü
"""
import os
from pathlib import Path

# Proje dizinleri
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Windows klasör yollarını normalize et
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# UITP SORT Test Döngüsü Parametreleri
SORT_CYCLES = {
    'SORT1': {
        'name': 'SORT 1 - Şehir İçi',
        'max_speed': 25,  # km/h
        'avg_speed': 12.5,
        'distance': 3.84,  # km
        'duration': 1100,  # saniye
        'description': 'Düşük hızlı şehir içi trafiği'
    },
    'SORT2': {
        'name': 'SORT 2 - Karışık Trafik',
        'max_speed': 40,
        'avg_speed': 20,
        'distance': 6.43,
        'duration': 1150,
        'description': 'Orta hızlı karışık trafik'
    },
    'SORT3': {
        'name': 'SORT 3 - Banliyö',
        'max_speed': 60,
        'avg_speed': 30,
        'distance': 11.44,
        'duration': 1370,
        'description': 'Yüksek hızlı banliyö trafiği'
    }
}

# Batarya Kapasiteleri (kWh)
BATTERY_CAPACITIES = [50, 75, 100, 125, 150, 200, 250, 300, 400, 500]

# Sıcaklık Aralıkları (°C)
TEMPERATURE_RANGES = {
    'Çok Soğuk': (-20, 0),
    'Soğuk': (0, 10),
    'İlıman': (10, 25),
    'Sıcak': (25, 35),
    'Çok Sıcak': (35, 50)
}

# Grafik Renkleri
CHART_COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'info': '#6C5B7B',
    'grid': '#CCCCCC',
    'text': '#333333'
}

# PDF Rapor Ayarları
PDF_SETTINGS = {
    'page_size': 'A4',
    'margin': 2.5,  # cm
    'font_family': 'Helvetica',
    'title_size': 18,
    'heading_size': 14,
    'normal_size': 10,
    'small_size': 8
}

# Excel Dosya Formatı Beklenen Sütunlar
EXCEL_COLUMNS = {
    'time': ['Zaman', 'Time', 'Süre', 'Duration', 'T', 't'],
    'speed': ['Hız', 'Speed', 'Velocity', 'V', 'v'],
    'current': ['Akım', 'Current', 'I', 'i', 'A'],
    'voltage': ['Voltaj', 'Voltage', 'U', 'u', 'V'],
    'temperature': ['Sıcaklık', 'Temperature', 'Temp', 'T', 't', '°C']
}

# Birim Dönüşümleri
UNIT_CONVERSIONS = {
    'km_to_m': 1000,
    'h_to_s': 3600,
    'ms_to_kmh': 3.6,
    'w_to_kw': 1000,
    'wh_to_kwh': 1000
}

# Varsayılan Değerler
DEFAULTS = {
    'battery_capacity': 100,  # kWh
    'regen_efficiency': 0.65,  # %65
    'battery_efficiency': 0.90,  # %90
    'motor_efficiency': 0.85,  # %85
    'soc_start': 100,  # %
    'soc_min': 20,  # %
    'ambient_temp': 25,  # °C
}

# GUI Ayarları
GUI_SETTINGS = {
    'window_title': 'Elektrikli Araç Enerji Tüketimi Analiz Sistemi',
    'window_size': '1400x900',
    'theme_colors': {
        'bg': '#F5F5F5',
        'fg': '#333333',
        'accent': '#2E86AB',
        'button': '#06A77D',
        'button_hover': '#048B5C'
    },
    'font_family': 'Segoe UI',
    'font_sizes': {
        'title': 16,
        'heading': 12,
        'normal': 10,
        'small': 8
    }
}

def get_logo_path():
    """Logo dosyasının yolunu döndürür"""
    logo_path = ASSETS_DIR / "logo.png"
    return str(logo_path) if logo_path.exists() else None

def get_output_path(filename):
    """Output dizininde dosya yolu oluşturur"""
    return str(OUTPUT_DIR / filename)

def get_data_path(filename):
    """Data dizininde dosya yolu oluşturur"""
    return str(DATA_DIR / filename)

def format_turkish_number(number, decimals=2):
    """Sayıları Türkçe formatta gösterir (virgül ile)"""
    if number is None:
        return "-"
    formatted = f"{number:,.{decimals}f}"
    # Nokta ve virgülü değiştir (Türkçe format)
    formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted
