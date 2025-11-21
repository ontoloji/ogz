"""
Yardımcı Fonksiyonlar
Windows uyumlu yardımcı utilities
"""
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def format_can_id(can_id: int, is_extended: bool = False) -> str:
    """
    CAN ID'yi formatla.

    Args:
        can_id: CAN ID
        is_extended: Genişletilmiş ID (29-bit)

    Returns:
        str: Formatlanmış ID (örn: "0x123" veya "0x12345678")
    """
    if is_extended:
        return f"0x{can_id:08X}"
    else:
        return f"0x{can_id:03X}"


def format_data_hex(data: bytes, separator: str = ' ') -> str:
    """
    CAN verisini hex formatında göster.

    Args:
        data: CAN verisi (bytes)
        separator: Byte'lar arası ayırıcı

    Returns:
        str: Formatlanmış veri (örn: "01 02 03 04")
    """
    return separator.join([f"{b:02X}" for b in data])


def format_data_dec(data: bytes, separator: str = ' ') -> str:
    """
    CAN verisini decimal formatında göster.

    Args:
        data: CAN verisi (bytes)
        separator: Byte'lar arası ayırıcı

    Returns:
        str: Formatlanmış veri (örn: "1 2 3 4")
    """
    return separator.join([f"{b:3d}" for b in data])


def parse_hex_data(hex_string: str) -> Optional[bytes]:
    """
    Hex string'i byte'lara dönüştür.

    Args:
        hex_string: Hex string (örn: "01 02 03" veya "010203")

    Returns:
        bytes: Byte verisi veya None
    """
    try:
        # Boşlukları ve özel karakterleri temizle
        hex_clean = hex_string.replace(' ', '').replace('0x', '').replace('0X', '')

        # Her 2 karakterde bir byte oluştur
        if len(hex_clean) % 2 != 0:
            logger.warning(f"Geçersiz hex string uzunluğu: {hex_string}")
            return None

        data = bytes.fromhex(hex_clean)
        return data

    except ValueError as e:
        logger.error(f"Hex parse hatası: {str(e)}")
        return None


def validate_can_id(can_id: int, is_extended: bool = False) -> bool:
    """
    CAN ID'nin geçerliliğini kontrol et.

    Args:
        can_id: CAN ID
        is_extended: Genişletilmiş ID (29-bit)

    Returns:
        bool: Geçerli ise True
    """
    if is_extended:
        return 0 <= can_id <= 0x1FFFFFFF  # 29-bit
    else:
        return 0 <= can_id <= 0x7FF  # 11-bit


def validate_can_data(data: bytes) -> bool:
    """
    CAN verisinin geçerliliğini kontrol et.

    Args:
        data: CAN verisi

    Returns:
        bool: Geçerli ise True
    """
    return 0 <= len(data) <= 8


def get_timestamp_string(timestamp: float = None) -> str:
    """
    Timestamp'i okunabilir string'e dönüştür.

    Args:
        timestamp: Unix timestamp (None ise şu anki zaman)

    Returns:
        str: Formatlanmış zaman string'i
    """
    if timestamp is None:
        dt = datetime.now()
    else:
        dt = datetime.fromtimestamp(timestamp)

    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Milisaniye hassasiyeti


def ensure_directory_exists(file_path: str) -> Path:
    """
    Dosya yolundaki dizinin var olduğundan emin ol. Yoksa oluştur.

    Args:
        file_path: Dosya yolu (Windows: C:\\path\\to\\file.txt)

    Returns:
        Path: Normalize edilmiş Path objesi
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: str) -> str:
    """
    Dosya uzantısını getir (küçük harf).

    Args:
        file_path: Dosya yolu

    Returns:
        str: Dosya uzantısı (örn: ".dbc", ".asc")
    """
    return Path(file_path).suffix.lower()


def format_file_size(size_bytes: int) -> str:
    """
    Dosya boyutunu okunabilir formata çevir.

    Args:
        size_bytes: Byte cinsinden boyut

    Returns:
        str: Formatlanmış boyut (örn: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """
    Süreyi okunabilir formata çevir.

    Args:
        seconds: Saniye cinsinden süre

    Returns:
        str: Formatlanmış süre (örn: "1h 23m 45s")
    """
    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes = int(seconds // 60)
    secs = seconds % 60

    if minutes < 60:
        return f"{minutes}m {secs:.1f}s"

    hours = minutes // 60
    mins = minutes % 60

    return f"{hours}h {mins}m {secs:.0f}s"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Değeri belirli aralıkta sınırla.

    Args:
        value: Değer
        min_value: Minimum değer
        max_value: Maksimum değer

    Returns:
        float: Sınırlanmış değer
    """
    return max(min_value, min(value, max_value))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Güvenli bölme işlemi (sıfıra bölme kontrolü).

    Args:
        numerator: Bölünen
        denominator: Bölen
        default: Sıfıra bölme durumunda dönecek değer

    Returns:
        float: Bölme sonucu veya default değer
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


class RateLimiter:
    """
    Rate limiting için yardımcı sınıf.
    Belirli bir sürede maksimum işlem sayısını sınırlar.
    """

    def __init__(self, max_calls: int, time_window: float):
        """
        Rate Limiter oluştur.

        Args:
            max_calls: Zaman penceresi içinde maksimum çağrı sayısı
            time_window: Zaman penceresi (saniye)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def allow(self) -> bool:
        """
        Yeni işlemin izin verilip verilmeyeceğini kontrol et.

        Returns:
            bool: İzin veriliyorsa True
        """
        now = datetime.now().timestamp()

        # Eski çağrıları temizle
        self.calls = [call_time for call_time in self.calls
                     if now - call_time < self.time_window]

        # Limit kontrolü
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True

        return False

    def reset(self):
        """Rate limiter'ı sıfırla."""
        self.calls.clear()


class MovingAverage:
    """
    Hareketli ortalama hesaplama sınıfı.
    """

    def __init__(self, window_size: int = 10):
        """
        Moving Average oluştur.

        Args:
            window_size: Pencere boyutu
        """
        from collections import deque
        self.window_size = window_size
        self.values = deque(maxlen=window_size)

    def add(self, value: float):
        """
        Yeni değer ekle.

        Args:
            value: Değer
        """
        self.values.append(value)

    def get_average(self) -> Optional[float]:
        """
        Hareketli ortalamayı getir.

        Returns:
            float: Ortalama değer veya None
        """
        if not self.values:
            return None

        return sum(self.values) / len(self.values)

    def clear(self):
        """Değerleri temizle."""
        self.values.clear()


def windows_safe_filename(filename: str) -> str:
    """
    Windows için güvenli dosya adı oluştur.

    Args:
        filename: Orijinal dosya adı

    Returns:
        str: Güvenli dosya adı
    """
    # Windows'ta yasak karakterler
    forbidden_chars = '<>:"/\\|?*'

    safe_name = filename
    for char in forbidden_chars:
        safe_name = safe_name.replace(char, '_')

    # Windows'ta yasak isimler
    forbidden_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]

    name_only = Path(safe_name).stem.upper()
    if name_only in forbidden_names:
        safe_name = f"_{safe_name}"

    return safe_name


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Uzun string'i kısalt.

    Args:
        text: Orijinal text
        max_length: Maksimum uzunluk
        suffix: Kısaltma soneki

    Returns:
        str: Kısaltılmış text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
