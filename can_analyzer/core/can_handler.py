"""
CAN Bus Handler Module
Windows Kvaser Device Support
"""
import can
import threading
import time
from typing import Callable, Optional, List, Dict
from datetime import datetime
import logging

# Windows'ta logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CANHandler:
    """
    Kvaser CAN cihazları için CAN Bus iletişim yöneticisi.
    Windows 10/11 uyumlu.
    """

    def __init__(self):
        """CAN Handler'ı başlat."""
        self.bus: Optional[can.Bus] = None
        self.is_connected = False
        self.is_receiving = False
        self.receive_thread: Optional[threading.Thread] = None
        self.message_callbacks: List[Callable] = []
        self.received_messages: List[Dict] = []
        self.max_stored_messages = 10000  # Maksimum saklanan mesaj sayısı
        self._stop_event = threading.Event()

    def connect(self, channel: int = 0, bitrate: int = 500000,
                interface: str = 'kvaser', **kwargs) -> bool:
        """
        Kvaser CAN cihazına bağlan.

        Args:
            channel: CAN kanal numarası (0, 1, vb.)
            bitrate: CAN bus hızı (bps) - örn: 125000, 250000, 500000, 1000000
            interface: CAN arayüzü tipi (kvaser, socketcan, pcan, vb.)
            **kwargs: python-can Bus için ek parametreler

        Returns:
            bool: Bağlantı başarılı ise True

        Raises:
            Exception: Bağlantı hatası durumunda
        """
        try:
            if self.is_connected:
                logger.warning("Zaten bir CAN cihazına bağlı. Önce disconnect() çağırın.")
                return False

            # Windows'ta Kvaser için python-can Bus oluştur
            self.bus = can.Bus(
                channel=channel,
                interface=interface,
                bitrate=bitrate,
                **kwargs
            )

            self.is_connected = True
            logger.info(f"CAN Bus'a başarıyla bağlandı: {interface}, Kanal: {channel}, Bitrate: {bitrate}")
            return True

        except Exception as e:
            error_msg = f"CAN Bus bağlantı hatası: {str(e)}"
            logger.error(error_msg)

            # Windows'a özel hata mesajları
            if "kvaser" in str(interface).lower():
                error_msg += "\n\nKvaser CANlib SDK'nın yüklü olduğundan emin olun."
                error_msg += "\nİndirme: https://www.kvaser.com/downloads/"

            raise Exception(error_msg)

    def disconnect(self):
        """CAN Bus bağlantısını kes."""
        try:
            if self.is_receiving:
                self.stop_receiving()

            if self.bus:
                self.bus.shutdown()
                self.bus = None

            self.is_connected = False
            logger.info("CAN Bus bağlantısı kapatıldı")

        except Exception as e:
            logger.error(f"Bağlantı kesme hatası: {str(e)}")

    def send_message(self, arbitration_id: int, data: bytes,
                     is_extended_id: bool = False) -> bool:
        """
        CAN mesajı gönder.

        Args:
            arbitration_id: CAN ID (11-bit veya 29-bit)
            data: Gönderilecek veri (max 8 byte)
            is_extended_id: Genişletilmiş ID kullanımı (29-bit)

        Returns:
            bool: Gönderim başarılı ise True
        """
        try:
            if not self.is_connected or not self.bus:
                raise Exception("CAN Bus'a bağlı değil")

            if len(data) > 8:
                raise ValueError("CAN verisi maksimum 8 byte olabilir")

            message = can.Message(
                arbitration_id=arbitration_id,
                data=data,
                is_extended_id=is_extended_id
            )

            self.bus.send(message)
            logger.debug(f"Mesaj gönderildi: ID=0x{arbitration_id:X}, Data={data.hex()}")
            return True

        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {str(e)}")
            return False

    def start_receiving(self):
        """
        CAN mesajlarını almaya başla (ayrı thread'de).
        """
        if not self.is_connected:
            raise Exception("CAN Bus'a bağlı değil")

        if self.is_receiving:
            logger.warning("Zaten mesaj alımı aktif")
            return

        self._stop_event.clear()
        self.is_receiving = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        logger.info("CAN mesaj alımı başlatıldı")

    def stop_receiving(self):
        """CAN mesaj alımını durdur."""
        if not self.is_receiving:
            return

        self._stop_event.set()
        self.is_receiving = False

        if self.receive_thread:
            self.receive_thread.join(timeout=2.0)

        logger.info("CAN mesaj alımı durduruldu")

    def _receive_loop(self):
        """
        Mesaj alma döngüsü (thread içinde çalışır).
        """
        while not self._stop_event.is_set() and self.is_connected:
            try:
                message = self.bus.recv(timeout=0.1)

                if message:
                    # Mesaj bilgilerini hazırla
                    msg_dict = {
                        'timestamp': message.timestamp,
                        'datetime': datetime.fromtimestamp(message.timestamp),
                        'arbitration_id': message.arbitration_id,
                        'is_extended_id': message.is_extended_id,
                        'is_error_frame': message.is_error_frame,
                        'dlc': message.dlc,
                        'data': bytes(message.data),
                        'channel': getattr(message, 'channel', None)
                    }

                    # Mesajı kaydet (bellek kontrolü ile)
                    self._store_message(msg_dict)

                    # Callback'leri çağır
                    self._call_callbacks(msg_dict)

            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Mesaj alma hatası: {str(e)}")
                    time.sleep(0.1)

    def _store_message(self, msg_dict: Dict):
        """
        Mesajı dahili listede sakla (bellek yönetimi ile).

        Args:
            msg_dict: Mesaj bilgileri
        """
        self.received_messages.append(msg_dict)

        # Maksimum limiti aşarsa eski mesajları sil
        if len(self.received_messages) > self.max_stored_messages:
            self.received_messages = self.received_messages[-self.max_stored_messages:]

    def _call_callbacks(self, msg_dict: Dict):
        """
        Kayıtlı callback fonksiyonlarını çağır.

        Args:
            msg_dict: Mesaj bilgileri
        """
        for callback in self.message_callbacks:
            try:
                callback(msg_dict)
            except Exception as e:
                logger.error(f"Callback hatası: {str(e)}")

    def add_callback(self, callback: Callable):
        """
        Mesaj alındığında çağrılacak callback ekle.

        Args:
            callback: Callback fonksiyonu (msg_dict parametresi alır)
        """
        if callback not in self.message_callbacks:
            self.message_callbacks.append(callback)
            logger.debug(f"Callback eklendi: {callback.__name__}")

    def remove_callback(self, callback: Callable):
        """
        Callback'i kaldır.

        Args:
            callback: Kaldırılacak callback fonksiyonu
        """
        if callback in self.message_callbacks:
            self.message_callbacks.remove(callback)
            logger.debug(f"Callback kaldırıldı: {callback.__name__}")

    def clear_messages(self):
        """Alınan mesaj geçmişini temizle."""
        self.received_messages.clear()
        logger.info("Mesaj geçmişi temizlendi")

    def get_messages(self, count: Optional[int] = None) -> List[Dict]:
        """
        Alınan mesajları getir.

        Args:
            count: Getirilecek mesaj sayısı (None = tümü)

        Returns:
            List[Dict]: Mesaj listesi
        """
        if count is None:
            return self.received_messages.copy()
        else:
            return self.received_messages[-count:].copy()

    def get_available_interfaces(self) -> List[str]:
        """
        Sistemde mevcut CAN arayüzlerini listele.

        Returns:
            List[str]: Mevcut arayüz isimleri
        """
        try:
            interfaces = can.detect_available_configs()
            return [f"{iface['interface']} - Channel {iface.get('channel', 'N/A')}"
                    for iface in interfaces]
        except Exception as e:
            logger.error(f"Arayüz tarama hatası: {str(e)}")
            return []

    def set_filters(self, filters: List[Dict]):
        """
        CAN ID filtreleri ayarla.

        Args:
            filters: Filtre listesi
                Örnek: [{"can_id": 0x123, "can_mask": 0x7FF, "extended": False}]
        """
        try:
            if not self.is_connected or not self.bus:
                raise Exception("CAN Bus'a bağlı değil")

            self.bus.set_filters(filters)
            logger.info(f"{len(filters)} adet filtre ayarlandı")

        except Exception as e:
            logger.error(f"Filtre ayarlama hatası: {str(e)}")
            raise

    def get_statistics(self) -> Dict:
        """
        İstatistik bilgileri getir.

        Returns:
            Dict: İstatistik verileri
        """
        return {
            'is_connected': self.is_connected,
            'is_receiving': self.is_receiving,
            'total_messages': len(self.received_messages),
            'callbacks_count': len(self.message_callbacks),
            'max_stored_messages': self.max_stored_messages
        }

    def __enter__(self):
        """Context manager desteği."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - temizlik."""
        self.disconnect()

    def __del__(self):
        """Destructor - bağlantıyı kapat."""
        try:
            self.disconnect()
        except:
            pass
