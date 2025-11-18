"""
SORT Test Otomasyon Sistemi - Yardımcı Fonksiyonlar
Windows ortamı için elektrikli ve içten yanmalı araç test otomasyon yazılımı
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Yapılandırma yöneticisi"""

    DEFAULT_CONFIG = {
        "can": {
            "channel": 0,
            "bitrate": 500000,
            "tx_id": 217056130,  # 0xCF00002
            "rx_id": 770  # 0x302
        },
        "arduino": {
            "port": "COM3",
            "baudrate": 115200,
            "timeout": 1.0,
            "daf_min_voltage": 0.5,
            "daf_max_voltage": 4.5,
            "ibk_min_voltage": 2.5,
            "ibk_max_voltage": 4.5
        },
        "edaq": {
            "ip": "192.168.1.100",
            "port": 8080,
            "endpoint": "/measurement/data",
            "channel_name": "Energy",
            "poll_interval": 0.4
        },
        "pid": {
            "kp": 2.0,
            "ki": 0.5,
            "kd": 0.1,
            "update_interval": 0.1,
            "tolerance": 1.0,
            "output_min": 0.0,
            "output_max": 100.0
        },
        "test": {
            "accel_pedal_default": 50,
            "max_speed_limit": 80,
            "brake_tolerance": 5.0,
            "wait_time_segment": 20
        },
        "gui": {
            "update_interval": 50,
            "graph_max_points": 1000,
            "graph_time_window": 10.0,
            "graph_distance_window": 150.0
        },
        "data": {
            "save_directory": "data",
            "log_directory": "logs"
        }
    }

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Yapılandırmayı yükle"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Varsayılan config ile merge et
                config = self.DEFAULT_CONFIG.copy()
                self._deep_update(config, user_config)
                return config
            except Exception as e:
                logging.error(f"Yapılandırma yüklenemedi: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # İlk çalıştırma - varsayılan config'i kaydet
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Yapılandırmayı kaydet"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Yapılandırma kaydedilemedi: {e}")

    def get(self, *keys):
        """İç içe yapılandırma değeri al"""
        value = self.config
        for key in keys:
            value = value.get(key, {})
        return value

    def set(self, value, *keys):
        """İç içe yapılandırma değeri ayarla"""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()

    @staticmethod
    def _deep_update(base_dict, update_dict):
        """Sözlükleri derin birleştir"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                Config._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """Loglama sistemini kur"""
    # Log klasörünü oluştur
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    if log_file is None:
        log_file = log_dir / f"sort_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def generate_test_filename(test_type: str, direction: str, vehicle: str, driver: str) -> str:
    """Test dosya adı oluştur"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"SORT{test_type}_{direction}_{timestamp}_{vehicle}_{driver}.csv"


def format_time(seconds: float) -> str:
    """Süreyi formatla (HH:MM:SS)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_distance(meters: float) -> str:
    """Mesafeyi formatla"""
    return f"{meters:.1f} m"


def format_speed(kmh: float) -> str:
    """Hızı formatla"""
    return f"{kmh:.1f} km/h"


def format_energy(kwh: float) -> str:
    """Enerjiyi formatla"""
    return f"{kwh:.2f} kWh"


def format_pedal(percent: float) -> str:
    """Gaz pedalını formatla"""
    return f"{percent:.0f}%"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Değeri sınırlar arasında tut"""
    return max(min_value, min(max_value, value))


def map_value(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """Değeri bir aralıktan başka bir aralığa eşle"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def calculate_percentage_difference(value1: float, value2: float) -> float:
    """İki değer arasındaki yüzde farkı hesapla"""
    if value1 == 0:
        return 0.0
    return ((value2 - value1) / value1) * 100.0


def ensure_directory(path: str) -> Path:
    """Klasörün var olduğundan emin ol, yoksa oluştur"""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


class TestStatus:
    """Test durumu sabitleri"""
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class SegmentType:
    """Segment tipi sabitleri"""
    IDLE = "IDLE"
    ACCEL = "ACCEL"
    CONSTANT = "CONSTANT"
    BRAKE = "BRAKE"
    WAIT = "WAIT"


class VehicleType:
    """Araç tipi sabitleri"""
    ELECTRIC = "ELECTRIC"  # CAN mesajı
    DAF_MOTOR = "DAF_MOTOR"  # Arduino Analog Kanal 1
    IBK = "IBK"  # Arduino Analog Kanal 2


def validate_speed_range(speed: float, target_speed: float, tolerance: float = 1.0) -> bool:
    """Hızın hedef aralıkta olup olmadığını kontrol et"""
    return abs(speed - target_speed) <= tolerance


def calculate_braking_distance(initial_speed: float, final_speed: float = 0.0) -> float:
    """Frenleme mesafesini tahmin et (basit formül)"""
    # v^2 = u^2 + 2as => s = (v^2 - u^2) / (2a)
    # Ortalama yavaşlama: -2 m/s^2 (varsayım)
    u = initial_speed / 3.6  # km/h -> m/s
    v = final_speed / 3.6
    a = -2.0  # m/s^2

    if a >= 0:
        return 0.0

    distance = (v**2 - u**2) / (2 * a)
    return max(0.0, distance)


class RingBuffer:
    """Sabit boyutlu halka buffer (grafik için)"""

    def __init__(self, max_size: int):
        self.max_size = max_size
        self.data = []

    def append(self, item):
        """Eleman ekle"""
        self.data.append(item)
        if len(self.data) > self.max_size:
            self.data.pop(0)

    def clear(self):
        """Temizle"""
        self.data.clear()

    def get_all(self):
        """Tüm verileri al"""
        return self.data.copy()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


if __name__ == "__main__":
    # Test
    config = Config()
    print("Yapılandırma yüklendi:")
    print(json.dumps(config.config, indent=2, ensure_ascii=False))

    setup_logging()
    logging.info("Loglama sistemi test edildi")

    print(f"\nTest dosya adı: {generate_test_filename('1', 'GIDIS', 'EV001', 'AHMET')}")
    print(f"Zaman formatı: {format_time(3665)}")
    print(f"Mesafe formatı: {format_distance(1234.5)}")
    print(f"Hız formatı: {format_speed(45.7)}")
    print(f"Enerji formatı: {format_energy(12.345)}")
