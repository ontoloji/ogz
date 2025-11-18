"""
CAN Bus Test Arayüzü - DBC Dosya Yöneticisi
DBC dosya parsing, mesaj decode ve sinyal analizi
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    import cantools
    CANTOOLS_AVAILABLE = True
except ImportError:
    CANTOOLS_AVAILABLE = False
    logging.warning("cantools kütüphanesi bulunamadı. DBC özellikleri devre dışı.")


@dataclass
class DBCSignal:
    """DBC Sinyal bilgisi"""
    name: str
    start_bit: int
    length: int
    byte_order: str  # 'little_endian' veya 'big_endian'
    is_signed: bool
    scale: float
    offset: float
    minimum: float
    maximum: float
    unit: str
    comment: str = ""

    def decode_value(self, raw_value: int) -> float:
        """
        Ham değeri fiziksel değere çevir

        Args:
            raw_value: Ham sinyal değeri

        Returns:
            Fiziksel değer (scale ve offset uygulanmış)
        """
        return (raw_value * self.scale) + self.offset

    def encode_value(self, physical_value: float) -> int:
        """
        Fiziksel değeri ham değere çevir

        Args:
            physical_value: Fiziksel değer

        Returns:
            Ham sinyal değeri
        """
        raw = (physical_value - self.offset) / self.scale
        return int(raw)


@dataclass
class DBCMessage:
    """DBC Mesaj bilgisi"""
    can_id: int
    name: str
    dlc: int
    sender: str
    signals: List[DBCSignal]
    comment: str = ""
    cycle_time: int = 0  # ms

    def get_signal(self, signal_name: str) -> Optional[DBCSignal]:
        """
        Sinyal adına göre sinyal bul

        Args:
            signal_name: Sinyal adı

        Returns:
            DBCSignal veya None
        """
        for signal in self.signals:
            if signal.name == signal_name:
                return signal
        return None


class DBCManager:
    """
    DBC dosya yöneticisi
    DBC parsing, mesaj decode ve sinyal erişimi
    """

    def __init__(self):
        self.database: Optional[cantools.database.Database] = None
        self.file_path: str = ""
        self.messages: Dict[int, DBCMessage] = {}  # CAN ID -> DBCMessage
        self.logger = logging.getLogger(__name__)

        if not CANTOOLS_AVAILABLE:
            self.logger.error("cantools kütüphanesi yüklü değil!")

    def load_dbc(self, filepath: str) -> bool:
        """
        DBC dosyasını yükle

        Args:
            filepath: DBC dosya yolu

        Returns:
            Başarılı ise True
        """
        if not CANTOOLS_AVAILABLE:
            self.logger.error("cantools kütüphanesi gerekli")
            return False

        try:
            # DBC dosyasını parse et
            self.database = cantools.database.load_file(filepath)
            self.file_path = filepath
            self.logger.info(f"DBC dosyası yüklendi: {filepath}")

            # Mesajları dictionary'e dönüştür
            self._parse_messages()

            self.logger.info(f"Toplam {len(self.messages)} mesaj yüklendi")
            return True

        except Exception as e:
            self.logger.error(f"DBC yükleme hatası: {e}")
            return False

    def _parse_messages(self):
        """DBC mesajlarını parse et ve dictionary'e ekle"""
        self.messages.clear()

        for msg in self.database.messages:
            # Sinyalleri parse et
            signals = []
            for sig in msg.signals:
                signal = DBCSignal(
                    name=sig.name,
                    start_bit=sig.start,
                    length=sig.length,
                    byte_order='little_endian' if sig.byte_order == 'little_endian' else 'big_endian',
                    is_signed=sig.is_signed,
                    scale=sig.scale,
                    offset=sig.offset,
                    minimum=sig.minimum if sig.minimum is not None else 0,
                    maximum=sig.maximum if sig.maximum is not None else 0,
                    unit=sig.unit if sig.unit else "",
                    comment=sig.comment if sig.comment else ""
                )
                signals.append(signal)

            # Mesaj objesi oluştur
            dbc_msg = DBCMessage(
                can_id=msg.frame_id,
                name=msg.name,
                dlc=msg.length,
                sender=msg.senders[0] if msg.senders else "Unknown",
                signals=signals,
                comment=msg.comment if msg.comment else "",
                cycle_time=msg.cycle_time if msg.cycle_time else 0
            )

            self.messages[msg.frame_id] = dbc_msg

    def get_messages(self) -> List[DBCMessage]:
        """Tüm DBC mesajlarını al"""
        return list(self.messages.values())

    def get_message_by_id(self, can_id: int) -> Optional[DBCMessage]:
        """
        CAN ID'ye göre mesaj bul

        Args:
            can_id: CAN mesaj ID

        Returns:
            DBCMessage veya None
        """
        return self.messages.get(can_id)

    def get_message_by_name(self, name: str) -> Optional[DBCMessage]:
        """
        Mesaj adına göre mesaj bul

        Args:
            name: Mesaj adı

        Returns:
            DBCMessage veya None
        """
        for msg in self.messages.values():
            if msg.name == name:
                return msg
        return None

    def decode_message(self, can_id: int, data: bytes) -> Optional[Dict[str, float]]:
        """
        CAN mesajını decode et

        Args:
            can_id: CAN mesaj ID
            data: Mesaj data (bytes)

        Returns:
            Sinyal adı -> değer dictionary'si veya None
        """
        if not CANTOOLS_AVAILABLE or not self.database:
            return None

        try:
            # Mesajı bul
            msg = self.database.get_message_by_frame_id(can_id)
            if not msg:
                return None

            # Decode et
            decoded = msg.decode(data)
            return decoded

        except Exception as e:
            self.logger.error(f"Decode hatası (ID: 0x{can_id:X}): {e}")
            return None

    def encode_message(self, can_id: int, signal_values: Dict[str, float]) -> Optional[bytes]:
        """
        Sinyal değerlerinden CAN mesajı oluştur

        Args:
            can_id: CAN mesaj ID
            signal_values: Sinyal adı -> değer dictionary'si

        Returns:
            Encode edilmiş data (bytes) veya None
        """
        if not CANTOOLS_AVAILABLE or not self.database:
            return None

        try:
            # Mesajı bul
            msg = self.database.get_message_by_frame_id(can_id)
            if not msg:
                return None

            # Encode et
            data = msg.encode(signal_values)
            return data

        except Exception as e:
            self.logger.error(f"Encode hatası (ID: 0x{can_id:X}): {e}")
            return None

    def get_signal_value(self, can_id: int, data: bytes, signal_name: str) -> Optional[float]:
        """
        Belirli bir sinyalin değerini al

        Args:
            can_id: CAN mesaj ID
            data: Mesaj data
            signal_name: Sinyal adı

        Returns:
            Sinyal değeri veya None
        """
        decoded = self.decode_message(can_id, data)
        if decoded and signal_name in decoded:
            return decoded[signal_name]
        return None

    def is_loaded(self) -> bool:
        """DBC dosyası yüklü mü?"""
        return self.database is not None

    def get_info(self) -> dict:
        """DBC dosya bilgilerini al"""
        if not self.database:
            return {
                'loaded': False,
                'file': '',
                'messages': 0,
                'nodes': 0
            }

        return {
            'loaded': True,
            'file': self.file_path,
            'messages': len(self.messages),
            'nodes': len(self.database.nodes) if hasattr(self.database, 'nodes') else 0,
            'version': self.database.version if hasattr(self.database, 'version') else ""
        }


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print("DBC Manager Test Modu")
    print("=" * 50)

    manager = DBCManager()

    # Test sinyali oluştur
    test_signal = DBCSignal(
        name="EngineRPM",
        start_bit=0,
        length=16,
        byte_order='little_endian',
        is_signed=False,
        scale=0.25,
        offset=0,
        minimum=0,
        maximum=16383.75,
        unit="rpm"
    )

    # Fiziksel değer -> Ham değer
    physical = 2450.0
    raw = test_signal.encode_value(physical)
    decoded = test_signal.decode_value(raw)

    print(f"\nTest Sinyal: {test_signal.name}")
    print(f"Fiziksel Değer: {physical} {test_signal.unit}")
    print(f"Ham Değer: {raw}")
    print(f"Decode: {decoded} {test_signal.unit}")

    # DBC info
    info = manager.get_info()
    print(f"\nDBC Info: {info}")

    print("\n✓ Test tamamlandı!")
