"""
CAN Bus Test Arayüzü - Mesaj Yönetim Modülü
Çoklu mesaj gönderimi, alma, filtreleme ve loglama
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional, List, Dict
from datetime import datetime

try:
    from canlib import canlib, Frame
    CANLIB_AVAILABLE = True
except ImportError:
    CANLIB_AVAILABLE = False
    logging.warning("Kvaser CANlib bulunamadı. CAN işlevselliği sınırlı olacak.")


@dataclass
class CANMessage:
    """CAN Mesaj tanımı"""
    can_id: int
    data: bytes
    dlc: int
    period_ms: int = 0  # 0 = tek seferlik, >0 = periyodik
    enabled: bool = True
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"MSG_0x{self.can_id:X}"

    def to_dict(self) -> dict:
        """Mesajı dictionary'e çevir"""
        return {
            'can_id': self.can_id,
            'data': self.data.hex().upper(),
            'dlc': self.dlc,
            'period_ms': self.period_ms,
            'enabled': self.enabled,
            'name': self.name
        }

    @staticmethod
    def from_dict(d: dict) -> 'CANMessage':
        """Dictionary'den mesaj oluştur"""
        return CANMessage(
            can_id=d['can_id'],
            data=bytes.fromhex(d['data']),
            dlc=d['dlc'],
            period_ms=d.get('period_ms', 0),
            enabled=d.get('enabled', True),
            name=d.get('name', '')
        )


@dataclass
class ReceivedCANMessage:
    """Alınan CAN mesajı"""
    can_id: int
    data: bytes
    dlc: int
    timestamp: float
    direction: str = "RX"  # RX veya TX

    def to_log_string(self) -> str:
        """Log formatında string"""
        dt = datetime.fromtimestamp(self.timestamp)
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]
        data_str = ' '.join(f'{b:02X}' for b in self.data[:self.dlc])
        return f"{time_str} | 0x{self.can_id:03X} | {self.dlc} | {data_str} | {self.direction}"

    def to_csv_row(self) -> List[str]:
        """CSV satırı"""
        dt = datetime.fromtimestamp(self.timestamp)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        data_str = ' '.join(f'{b:02X}' for b in self.data[:self.dlc])
        return [time_str, f"0x{self.can_id:X}", str(self.dlc), data_str, self.direction]


class CANMessageSender:
    """
    CAN mesaj gönderme yöneticisi
    Çoklu mesajı eşzamanlı ve periyodik gönderebilir
    """

    def __init__(self, can_channel):
        """
        Args:
            can_channel: canlib channel objesi
        """
        self.channel = can_channel
        self.messages: List[CANMessage] = []
        self.running = False
        self.sender_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)

        # İstatistikler
        self.sent_count = 0
        self.error_count = 0
        self.last_send_time: Dict[int, float] = {}  # message index -> timestamp

    def add_message(self, message: CANMessage) -> int:
        """
        Mesaj listesine ekle

        Returns:
            Mesaj index'i
        """
        self.messages.append(message)
        index = len(self.messages) - 1
        self.logger.info(f"Mesaj eklendi: {message.name} (index: {index})")
        return index

    def remove_message(self, index: int) -> bool:
        """
        Mesajı listeden çıkar

        Args:
            index: Mesaj index'i

        Returns:
            Başarılı ise True
        """
        if 0 <= index < len(self.messages):
            msg = self.messages.pop(index)
            self.logger.info(f"Mesaj silindi: {msg.name}")
            return True
        return False

    def update_message(self, index: int, message: CANMessage) -> bool:
        """
        Mesajı güncelle

        Args:
            index: Mesaj index'i
            message: Yeni mesaj

        Returns:
            Başarılı ise True
        """
        if 0 <= index < len(self.messages):
            self.messages[index] = message
            self.logger.info(f"Mesaj güncellendi: {message.name}")
            return True
        return False

    def toggle_message(self, index: int) -> bool:
        """
        Mesajı aktif/pasif yap

        Args:
            index: Mesaj index'i

        Returns:
            Yeni durum (True=aktif)
        """
        if 0 <= index < len(self.messages):
            self.messages[index].enabled = not self.messages[index].enabled
            return self.messages[index].enabled
        return False

    def get_messages(self) -> List[CANMessage]:
        """Tüm mesajları al"""
        return self.messages.copy()

    def clear_messages(self):
        """Tüm mesajları temizle"""
        self.messages.clear()
        self.logger.info("Tüm mesajlar temizlendi")

    def start_sending(self):
        """Gönderimi başlat"""
        if self.running:
            self.logger.warning("Gönderim zaten çalışıyor")
            return

        self.running = True
        self.sender_thread = threading.Thread(
            target=self._sender_loop,
            daemon=True,
            name="CAN_MessageSender"
        )
        self.sender_thread.start()
        self.logger.info("Mesaj gönderimi başlatıldı")

    def stop_sending(self):
        """Gönderimi durdur"""
        self.running = False
        if self.sender_thread:
            self.sender_thread.join(timeout=2.0)
        self.logger.info("Mesaj gönderimi durduruldu")

    def send_once(self, message: CANMessage) -> bool:
        """
        Tek seferlik mesaj gönder

        Args:
            message: Gönderilecek mesaj

        Returns:
            Başarılı ise True
        """
        try:
            frame = Frame(id_=message.can_id, data=message.data, dlc=message.dlc)
            self.channel.write(frame)
            self.sent_count += 1
            self.logger.debug(f"Mesaj gönderildi: {message.name}")
            return True
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Mesaj gönderme hatası: {e}")
            return False

    def _sender_loop(self):
        """Gönderici thread loop"""
        next_send_times = [0.0] * len(self.messages)

        while self.running:
            current_time = time.time()

            for i, message in enumerate(self.messages):
                # Mesaj aktif mi?
                if not message.enabled:
                    continue

                # Periyodik mesaj mı?
                if message.period_ms <= 0:
                    continue

                # Index uzunluk kontrolü
                if i >= len(next_send_times):
                    next_send_times.append(0.0)

                # Gönderme zamanı geldi mi?
                if current_time >= next_send_times[i]:
                    if self.send_once(message):
                        self.last_send_time[i] = current_time
                        next_send_times[i] = current_time + (message.period_ms / 1000.0)

            # CPU kullanımını azalt
            time.sleep(0.001)

    def get_statistics(self) -> dict:
        """İstatistikleri al"""
        return {
            'sent_count': self.sent_count,
            'error_count': self.error_count,
            'active_messages': sum(1 for m in self.messages if m.enabled),
            'total_messages': len(self.messages),
            'is_running': self.running
        }


class CANMessageReceiver:
    """
    CAN mesaj alma yöneticisi
    Filtreleme, loglama ve callback desteği
    """

    def __init__(self, can_channel):
        """
        Args:
            can_channel: canlib channel objesi
        """
        self.channel = can_channel
        self.running = False
        self.receiver_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)

        # Filtreler
        self.id_filters: List[int] = []  # Boş = tüm ID'ler
        self.byte_filters: Dict[int, int] = {}  # byte_index -> expected_value

        # Callback
        self.message_callback: Optional[Callable[[ReceivedCANMessage], None]] = None

        # İstatistikler
        self.received_count = 0
        self.filtered_count = 0

        # Mesaj buffer (son N mesaj)
        self.max_buffer_size = 1000
        self.message_buffer: List[ReceivedCANMessage] = []

    def set_id_filters(self, id_list: List[int]):
        """
        ID filtresi ayarla

        Args:
            id_list: İzlenecek CAN ID listesi (boş = tümü)
        """
        self.id_filters = id_list.copy()
        self.logger.info(f"ID filtreleri ayarlandı: {[f'0x{i:X}' for i in id_list]}")

    def add_byte_filter(self, byte_index: int, expected_value: int):
        """
        Byte değeri filtresi ekle

        Args:
            byte_index: Byte pozisyonu (0-7)
            expected_value: Beklenen değer (0-255)
        """
        self.byte_filters[byte_index] = expected_value
        self.logger.info(f"Byte filtresi eklendi: Byte[{byte_index}] = 0x{expected_value:02X}")

    def clear_byte_filters(self):
        """Tüm byte filtrelerini temizle"""
        self.byte_filters.clear()
        self.logger.info("Byte filtreleri temizlendi")

    def set_message_callback(self, callback: Callable[[ReceivedCANMessage], None]):
        """
        Mesaj alındığında çağrılacak callback ayarla

        Args:
            callback: Callback fonksiyonu (ReceivedCANMessage parametresi ile)
        """
        self.message_callback = callback

    def start_receiving(self):
        """Alma işlemini başlat"""
        if self.running:
            self.logger.warning("Alma işlemi zaten çalışıyor")
            return

        self.running = True
        self.receiver_thread = threading.Thread(
            target=self._receiver_loop,
            daemon=True,
            name="CAN_MessageReceiver"
        )
        self.receiver_thread.start()
        self.logger.info("Mesaj alma işlemi başlatıldı")

    def stop_receiving(self):
        """Alma işlemini durdur"""
        self.running = False
        if self.receiver_thread:
            self.receiver_thread.join(timeout=2.0)
        self.logger.info("Mesaj alma işlemi durduruldu")

    def get_messages(self) -> List[ReceivedCANMessage]:
        """Buffer'daki tüm mesajları al"""
        return self.message_buffer.copy()

    def clear_buffer(self):
        """Mesaj buffer'ını temizle"""
        self.message_buffer.clear()
        self.logger.info("Mesaj buffer'ı temizlendi")

    def _receiver_loop(self):
        """Alıcı thread loop"""
        timeout = 100  # ms

        while self.running:
            try:
                # Mesaj oku
                frame = self.channel.read(timeout=timeout)

                # Mesaj objesine çevir
                msg = ReceivedCANMessage(
                    can_id=frame.id,
                    data=bytes(frame.data),
                    dlc=frame.dlc,
                    timestamp=time.time(),
                    direction="RX"
                )

                # Filtreleri uygula
                if self._apply_filters(msg):
                    self._process_message(msg)
                else:
                    self.filtered_count += 1

            except canlib.CanNoMsg:
                # Timeout - normal durum
                pass
            except Exception as e:
                self.logger.error(f"Mesaj alma hatası: {e}")
                time.sleep(0.1)

    def _apply_filters(self, msg: ReceivedCANMessage) -> bool:
        """
        Filtreleri uygula

        Args:
            msg: Kontrol edilecek mesaj

        Returns:
            True = mesaj geçerli, False = filtrelendi
        """
        # ID filtresi
        if self.id_filters and msg.can_id not in self.id_filters:
            return False

        # Byte filtreleri
        for byte_idx, expected_val in self.byte_filters.items():
            if byte_idx < len(msg.data):
                if msg.data[byte_idx] != expected_val:
                    return False

        return True

    def _process_message(self, msg: ReceivedCANMessage):
        """
        Mesajı işle (buffer'a ekle ve callback çağır)

        Args:
            msg: İşlenecek mesaj
        """
        # Buffer'a ekle
        self.message_buffer.append(msg)

        # Buffer boyutu kontrolü
        if len(self.message_buffer) > self.max_buffer_size:
            # Eski mesajları sil
            self.message_buffer = self.message_buffer[-self.max_buffer_size:]

        self.received_count += 1

        # Callback çağır
        if self.message_callback:
            try:
                self.message_callback(msg)
            except Exception as e:
                self.logger.error(f"Callback hatası: {e}")

    def get_statistics(self) -> dict:
        """İstatistikleri al"""
        return {
            'received_count': self.received_count,
            'filtered_count': self.filtered_count,
            'buffer_size': len(self.message_buffer),
            'is_running': self.running,
            'active_filters': len(self.id_filters) + len(self.byte_filters)
        }


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print("CAN Message Manager Test Modu")
    print("=" * 50)

    # Test mesajları oluştur
    msg1 = CANMessage(can_id=0x123, data=bytes([0x01, 0x02, 0x03, 0x04]), dlc=4, period_ms=100, name="Test1")
    msg2 = CANMessage(can_id=0x456, data=bytes([0xAA, 0xBB, 0xCC]), dlc=3, period_ms=50, name="Test2")

    print(f"\nTest Mesajı 1: {msg1.to_dict()}")
    print(f"Test Mesajı 2: {msg2.to_dict()}")

    # Alınan mesaj test
    rx_msg = ReceivedCANMessage(
        can_id=0x789,
        data=bytes([0xFF, 0xEE, 0xDD]),
        dlc=3,
        timestamp=time.time()
    )

    print(f"\nAlınan Mesaj (Log): {rx_msg.to_log_string()}")
    print(f"Alınan Mesaj (CSV): {rx_msg.to_csv_row()}")

    print("\n✓ Test tamamlandı!")
