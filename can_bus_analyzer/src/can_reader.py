"""
CAN Bus Okuyucu Modülü
Windows Kvaser cihazları için CAN mesaj okuma işlemlerini yönetir.
"""

import can
import threading
import queue
import time
from typing import Optional, Callable, List, Dict
from datetime import datetime
import logging

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CANReader:
    """
    Kvaser CAN cihazlarından mesaj okuma sınıfı.
    Windows platformunda çalışır ve real-time CAN mesajları okur.
    """

    def __init__(self, channel: int = 0, bitrate: int = 500000, interface: str = 'kvaser'):
        """
        CAN okuyucu başlatıcı.

        Args:
            channel: CAN kanal numarası (varsayılan: 0)
            bitrate: CAN bus hızı (varsayılan: 500000 = 500Kbps)
            interface: CAN arayüzü tipi (varsayılan: 'kvaser')
        """
        self.channel = channel
        self.bitrate = bitrate
        self.interface = interface
        self.bus: Optional[can.Bus] = None
        self.is_connected = False
        self.is_reading = False

        # Thread ve kuyruk yönetimi
        self.read_thread: Optional[threading.Thread] = None
        self.message_queue = queue.Queue(maxsize=1000)

        # Callback fonksiyonları
        self.message_callbacks: List[Callable] = []

        # İstatistikler
        self.message_count = 0
        self.error_count = 0
        self.start_time: Optional[float] = None

        # Filtreler
        self.can_id_filters: List[int] = []
        self.filter_enabled = False

    def connect(self) -> bool:
        """
        CAN bus'a bağlan.

        Returns:
            bool: Bağlantı başarılı ise True
        """
        try:
            # Windows için Kvaser arayüzü yapılandırması
            self.bus = can.Bus(
                channel=self.channel,
                bustype=self.interface,
                bitrate=self.bitrate
            )
            self.is_connected = True
            self.start_time = time.time()
            logger.info(f"CAN Bus'a başarıyla bağlanıldı: {self.interface} kanal {self.channel}, {self.bitrate} bps")
            return True

        except can.CanError as e:
            logger.error(f"CAN bağlantı hatası: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """CAN bus bağlantısını kapat."""
        self.stop_reading()
        if self.bus:
            try:
                self.bus.shutdown()
                self.is_connected = False
                logger.info("CAN Bus bağlantısı kapatıldı")
            except Exception as e:
                logger.error(f"Bağlantı kapatma hatası: {e}")

    def start_reading(self):
        """CAN mesajlarını okumaya başla (thread'de)."""
        if not self.is_connected:
            logger.error("CAN Bus'a bağlı değil!")
            return False

        if self.is_reading:
            logger.warning("Okuma zaten devam ediyor")
            return False

        self.is_reading = True
        self.read_thread = threading.Thread(target=self._read_messages, daemon=True)
        self.read_thread.start()
        logger.info("CAN mesaj okuma başlatıldı")
        return True

    def stop_reading(self):
        """CAN mesaj okumayı durdur."""
        if self.is_reading:
            self.is_reading = False
            if self.read_thread:
                self.read_thread.join(timeout=2.0)
            logger.info("CAN mesaj okuma durduruldu")

    def _read_messages(self):
        """
        CAN mesajlarını sürekli okuyan thread fonksiyonu.
        Private metod - direkt çağrılmamalı.
        """
        while self.is_reading and self.bus:
            try:
                # Timeout ile mesaj oku (100ms)
                message = self.bus.recv(timeout=0.1)

                if message:
                    # Filtre kontrolü
                    if self.filter_enabled and self.can_id_filters:
                        if message.arbitration_id not in self.can_id_filters:
                            continue

                    # Mesajı işle
                    self._process_message(message)

            except can.CanError as e:
                self.error_count += 1
                logger.error(f"CAN okuma hatası: {e}")
            except Exception as e:
                self.error_count += 1
                logger.error(f"Mesaj işleme hatası: {e}")

    def _process_message(self, message: can.Message):
        """
        Gelen CAN mesajını işle.

        Args:
            message: CAN mesaj objesi
        """
        try:
            self.message_count += 1

            # Mesajı kuyruğa ekle
            if not self.message_queue.full():
                msg_dict = {
                    'timestamp': message.timestamp,
                    'datetime': datetime.fromtimestamp(message.timestamp),
                    'arbitration_id': message.arbitration_id,
                    'is_extended_id': message.is_extended_id,
                    'dlc': message.dlc,
                    'data': list(message.data),
                    'is_error_frame': message.is_error_frame,
                    'is_remote_frame': message.is_remote_frame,
                }
                self.message_queue.put(msg_dict)

            # Callback fonksiyonları çağır
            for callback in self.message_callbacks:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Callback hatası: {e}")

        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {e}")

    def add_callback(self, callback: Callable):
        """
        Mesaj callback fonksiyonu ekle.

        Args:
            callback: Her mesaj geldiğinde çağrılacak fonksiyon
        """
        if callback not in self.message_callbacks:
            self.message_callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        """Callback fonksiyonunu kaldır."""
        if callback in self.message_callbacks:
            self.message_callbacks.remove(callback)

    def get_messages(self, timeout: float = 0.1) -> List[Dict]:
        """
        Kuyruktaki mesajları al.

        Args:
            timeout: Bekleme süresi (saniye)

        Returns:
            List[Dict]: Mesaj listesi
        """
        messages = []
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                msg = self.message_queue.get_nowait()
                messages.append(msg)
            except queue.Empty:
                break

        return messages

    def send_message(self, arbitration_id: int, data: List[int],
                     is_extended_id: bool = False) -> bool:
        """
        CAN mesajı gönder.

        Args:
            arbitration_id: CAN ID
            data: Veri byte'ları (0-8 byte)
            is_extended_id: Extended ID kullanımı

        Returns:
            bool: Başarılı ise True
        """
        if not self.is_connected or not self.bus:
            logger.error("CAN Bus'a bağlı değil!")
            return False

        try:
            message = can.Message(
                arbitration_id=arbitration_id,
                data=data,
                is_extended_id=is_extended_id
            )
            self.bus.send(message)
            logger.debug(f"Mesaj gönderildi: ID=0x{arbitration_id:X}, Data={data}")
            return True

        except can.CanError as e:
            logger.error(f"Mesaj gönderme hatası: {e}")
            return False

    def set_filters(self, can_ids: List[int], enabled: bool = True):
        """
        CAN ID filtreleri ayarla.

        Args:
            can_ids: Filtrelenecek CAN ID listesi
            enabled: Filtreleme aktif/pasif
        """
        self.can_id_filters = can_ids
        self.filter_enabled = enabled
        logger.info(f"Filtre ayarlandı: {len(can_ids)} ID, Aktif: {enabled}")

    def clear_filters(self):
        """Tüm filtreleri temizle."""
        self.can_id_filters = []
        self.filter_enabled = False
        logger.info("Filtreler temizlendi")

    def get_statistics(self) -> Dict:
        """
        İstatistik bilgilerini al.

        Returns:
            Dict: İstatistik verileri
        """
        elapsed = time.time() - self.start_time if self.start_time else 0

        return {
            'message_count': self.message_count,
            'error_count': self.error_count,
            'elapsed_time': elapsed,
            'messages_per_second': self.message_count / elapsed if elapsed > 0 else 0,
            'queue_size': self.message_queue.qsize(),
            'is_connected': self.is_connected,
            'is_reading': self.is_reading
        }

    def reset_statistics(self):
        """İstatistikleri sıfırla."""
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()

    @staticmethod
    def list_available_channels() -> List[str]:
        """
        Mevcut CAN kanallarını listele.

        Returns:
            List[str]: Kullanılabilir kanal listesi
        """
        try:
            channels = []
            # Kvaser için mevcut kanalları tara
            for i in range(8):  # Maksimum 8 kanal kontrol et
                try:
                    bus = can.Bus(channel=i, bustype='kvaser', bitrate=500000)
                    channels.append(f"Kanal {i}")
                    bus.shutdown()
                except:
                    pass
            return channels if channels else ["Cihaz bulunamadı"]
        except Exception as e:
            logger.error(f"Kanal tarama hatası: {e}")
            return ["Hata: Cihaz taranamadı"]


if __name__ == "__main__":
    # Test kodu
    print("CAN Reader Modülü Test Ediliyor...")

    reader = CANReader(channel=0, bitrate=500000)

    # Callback fonksiyonu
    def test_callback(msg):
        print(f"Mesaj alındı: ID=0x{msg.arbitration_id:X}, Data={list(msg.data)}")

    reader.add_callback(test_callback)

    if reader.connect():
        reader.start_reading()
        print("5 saniye CAN mesajları dinleniyor...")
        time.sleep(5)

        stats = reader.get_statistics()
        print(f"\nİstatistikler: {stats}")

        reader.disconnect()
    else:
        print("CAN bağlantısı başarısız!")
