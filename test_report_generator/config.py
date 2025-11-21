"""
Rapor oluşturucu konfigürasyon ayarları
"""

import os
from pathlib import Path
from typing import Dict, Any

# Dizin yapısı
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = Path(__file__).parent / "templates"
ASSETS_DIR = Path(__file__).parent / "assets"
REPORTS_DIR = BASE_DIR / "reports"

# Rapor varsayılan ayarları
DEFAULT_CONFIG = {
    # Genel ayarlar
    "language": "tr",  # tr veya en
    "company_name": "OTOKAR",
    "logo_path": ASSETS_DIR / "otokar_logo.png",

    # PDF ayarları
    "pdf": {
        "page_size": "A4",
        "margin_top": 2.5,  # cm
        "margin_bottom": 2.5,
        "margin_left": 2.0,
        "margin_right": 2.0,
        "font_name": "Helvetica",
        "font_size": 10,
        "title_font_size": 16,
        "heading_font_size": 12,
    },

    # Word ayarları
    "word": {
        "font_name": "Calibri",
        "font_size": 11,
        "title_font_size": 18,
        "heading_font_size": 14,
    },

    # Grafik ayarları
    "charts": {
        "width": 12,  # inch
        "height": 6,
        "dpi": 150,
        "style": "seaborn-v0_8-darkgrid",
        "color_palette": "Set2",
        # Otokar kurumsal renkleri
        "otokar_colors": {
            "primary": "#003366",  # Koyu mavi
            "secondary": "#FF6600",  # Turuncu
            "success": "#00AA44",  # Yeşil
            "danger": "#DD0000",  # Kırmızı
            "warning": "#FFAA00",  # Sarı
            "info": "#0088CC",  # Açık mavi
        }
    },

    # İstatistik ayarları
    "statistics": {
        "decimal_places": 2,
        "confidence_level": 0.95,
        "tolerance": 0.02,  # %2
    },

    # Test gereksinimleri (örnek - projeye göre özelleştirilebilir)
    "requirements": {
        "SORT1": {
            "max_energy_consumption": 100,  # kWh/100km
            "max_duration": 3600,  # saniye
            "min_distance": 1000,  # metre
        },
        "SORT2": {
            "max_energy_consumption": 95,
            "max_duration": 3000,
            "min_distance": 900,
        },
        "SORT3": {
            "max_energy_consumption": 110,
            "max_duration": 4000,
            "min_distance": 1400,
        },
    }
}

# Dil çevirileri
TRANSLATIONS = {
    "tr": {
        "report_title": "Test Raporu",
        "test_results": "Test Sonuçları",
        "summary": "Özet",
        "statistics": "İstatistiksel Analiz",
        "charts": "Grafikler",
        "comparison": "Karşılaştırma",
        "requirements": "Gereksinim Kontrolü",
        "pass": "BAŞARILI",
        "fail": "BAŞARISIZ",
        "date": "Tarih",
        "vehicle": "Araç",
        "driver": "Sürücü",
        "temperature": "Sıcaklık",
        "test_type": "Test Tipi",
        "duration": "Süre",
        "distance": "Mesafe",
        "energy": "Enerji Tüketimi",
        "average": "Ortalama",
        "minimum": "Minimum",
        "maximum": "Maksimum",
        "std_dev": "Standart Sapma",
        "median": "Medyan",
        "total": "Toplam",
        "speed": "Hız",
        "time": "Zaman",
        "requirement": "Gereksinim",
        "actual": "Gerçekleşen",
        "status": "Durum",
        "page": "Sayfa",
        "of": "/",
        "generated_on": "Oluşturulma Tarihi",
        "test_date": "Test Tarihi",
        "test_number": "Test No",
        "conclusion": "Sonuç",
        "notes": "Notlar",
    },
    "en": {
        "report_title": "Test Report",
        "test_results": "Test Results",
        "summary": "Summary",
        "statistics": "Statistical Analysis",
        "charts": "Charts",
        "comparison": "Comparison",
        "requirements": "Requirements Check",
        "pass": "PASS",
        "fail": "FAIL",
        "date": "Date",
        "vehicle": "Vehicle",
        "driver": "Driver",
        "temperature": "Temperature",
        "test_type": "Test Type",
        "duration": "Duration",
        "distance": "Distance",
        "energy": "Energy Consumption",
        "average": "Average",
        "minimum": "Minimum",
        "maximum": "Maximum",
        "std_dev": "Standard Deviation",
        "median": "Median",
        "total": "Total",
        "speed": "Speed",
        "time": "Time",
        "requirement": "Requirement",
        "actual": "Actual",
        "status": "Status",
        "page": "Page",
        "of": "of",
        "generated_on": "Generated On",
        "test_date": "Test Date",
        "test_number": "Test Number",
        "conclusion": "Conclusion",
        "notes": "Notes",
    }
}


class ReportConfig:
    """Rapor konfigürasyonu yöneticisi"""

    def __init__(self, custom_config: Dict[str, Any] = None):
        """
        Args:
            custom_config: Özel ayarlar (varsayılanları geçersiz kılar)
        """
        self.config = DEFAULT_CONFIG.copy()
        if custom_config:
            self._merge_config(self.config, custom_config)

        self.language = self.config.get("language", "tr")
        self.translations = TRANSLATIONS.get(self.language, TRANSLATIONS["tr"])

    def _merge_config(self, base: Dict, custom: Dict):
        """İç içe dictionary'leri birleştirir"""
        for key, value in custom.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default=None):
        """Ayar değeri al"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def translate(self, key: str) -> str:
        """Metni çevir"""
        return self.translations.get(key, key)

    def ensure_dirs(self):
        """Gerekli dizinleri oluştur"""
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
