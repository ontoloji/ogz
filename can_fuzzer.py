"""
CAN Bus Fuzzer Modülü
Kvaser Memorator 2xHS - Windows

ISO 21434 ve UN R155 uyumlu fuzzing testleri
Otomotiv sistemlerinde güvenlik açıklarını tespit etmek için kullanılır
"""

import logging
import random
import time
import threading
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from can_pentest_core import CANPentestCore, CANMessage, PentestMode, SecurityLevel


class FuzzingStrategy(Enum):
    """Fuzzing stratejileri"""
    RANDOM = "random"              # Tamamen rastgele
    SEQUENTIAL = "sequential"      # Sıralı ID tarama
    KNOWN_IDS = "known_ids"        # Bilinen ID'lere fuzzing
    BIT_FLIP = "bit_flip"          # Bit flipping
    BOUNDARY = "boundary"          # Sınır değerler
    SMART = "smart"                # Akıllı fuzzing (öğrenme)


class DataPattern(Enum):
    """Veri pattern'leri"""
    RANDOM = "random"              # Rastgele
    ALL_ZERO = "all_zero"          # 0x00000000
    ALL_ONE = "all_one"            # 0xFFFFFFFF
    ALTERNATING = "alternating"    # 0xAA, 0x55
    INCREMENTAL = "incremental"    # 0x00, 0x01, 0x02, ...
    BOUNDARY_VALUES = "boundary"   # Min/Max değerler


@dataclass
class FuzzingConfig:
    """Fuzzing konfigürasyonu"""
    strategy: FuzzingStrategy = FuzzingStrategy.RANDOM
    data_pattern: DataPattern = DataPattern.RANDOM

    # CAN ID aralığı
    can_id_min: int = 0x000
    can_id_max: int = 0x7FF

    # Mesaj parametreleri
    dlc_min: int = 1
    dlc_max: int = 8

    # Zamanlama
    interval_ms: int = 10  # Mesajlar arası süre (ms)
    duration_sec: int = 60  # Test süresi (saniye)
    max_messages: int = 10000  # Maksimum mesaj sayısı

    # Güvenlik
    safety_mode: bool = True  # Güvenli mod (kritik ID'leri atla)
    exclude_ids: List[int] = None  # Hariç tutulacak ID'ler

    # Monitoring
    monitor_responses: bool = True  # Yanıtları izle
    detect_crashes: bool = True     # ECU crash tespiti


@dataclass
class FuzzingResult:
    """Fuzzing test sonucu"""
    config: FuzzingConfig
    start_time: datetime
    end_time: datetime
    total_sent: int
    responses_received: int
    anomalies_detected: int
    crashes_detected: int
    interesting_findings: List[Dict[str, Any]]
    success: bool


class CANFuzzer:
    """
    CAN Bus Fuzzer

    Otomotiv sistemlerinde güvenlik açıklarını tespit etmek için
    çeşitli fuzzing teknikleri uygular.
    """

    # Kritik CAN ID'ler (güvenli modda korunur)
    CRITICAL_IDS = [
        0x140,  # Engine RPM
        0x220,  # Steering
        0x224,  # Brake pressure
        0x244,  # Speed
        0x320,  # Airbag
        0x3B0,  # Transmission
        # ISO-TP / UDS
        range(0x7E0, 0x7EF),
        0x7DF,
    ]

    def __init__(self, pentest_core: CANPentestCore):
        """
        Args:
            pentest_core: CAN pentest core instance
        """
        self.core = pentest_core
        self.config = FuzzingConfig()

        # Test durumu
        self.is_running = False
        self.fuzzing_thread = None

        # İstatistikler
        self.stats = {
            'messages_sent': 0,
            'responses_received': 0,
            'anomalies': 0,
            'crashes': 0,
            'start_time': None,
            'current_id': 0,
            'current_data': bytearray(8)
        }

        # Sonuçlar
        self.interesting_findings: List[Dict[str, Any]] = []

        # Callback'ler
        self.progress_callback: Optional[Callable[[int, int], None]] = None
        self.finding_callback: Optional[Callable[[Dict], None]] = None

        self.logger = logging.getLogger(__name__)

    def configure(self, config: FuzzingConfig):
        """Fuzzing konfigürasyonu ayarla"""
        self.config = config
        self.logger.info(f"Fuzzing config: {config.strategy.value}, {config.data_pattern.value}")

    def start_fuzzing(self, config: Optional[FuzzingConfig] = None) -> bool:
        """
        Fuzzing başlat

        Args:
            config: Fuzzing konfigürasyonu (opsiyonel)

        Returns:
            Başarı durumu
        """
        if self.is_running:
            self.logger.warning("Fuzzing zaten çalışıyor!")
            return False

        if not self.core.is_connected:
            self.logger.error("CAN bağlantısı yok!")
            return False

        if config:
            self.config = config

        # Güvenlik kontrolü
        if self.config.safety_mode:
            self.logger.warning("GÜVENLİK MODU AKTİF - Kritik ID'ler korunacak")

        # Core'u FUZZING moduna al
        self.core.set_mode(PentestMode.FUZZING)

        # İstatistikleri sıfırla
        self._reset_stats()

        # Thread başlat
        self.is_running = True
        self.fuzzing_thread = threading.Thread(
            target=self._fuzzing_loop,
            daemon=True,
            name="Fuzzing"
        )
        self.fuzzing_thread.start()

        self.logger.info("Fuzzing başlatıldı")
        return True

    def stop_fuzzing(self):
        """Fuzzing durdur"""
        self.is_running = False

        if self.fuzzing_thread:
            self.fuzzing_thread.join(timeout=2.0)

        # Core'u PASSIVE moda al
        self.core.set_mode(PentestMode.PASSIVE)

        self.logger.info("Fuzzing durduruldu")

    def _reset_stats(self):
        """İstatistikleri sıfırla"""
        self.stats = {
            'messages_sent': 0,
            'responses_received': 0,
            'anomalies': 0,
            'crashes': 0,
            'start_time': time.time(),
            'current_id': self.config.can_id_min,
            'current_data': bytearray(8)
        }
        self.interesting_findings.clear()

    def _fuzzing_loop(self):
        """Ana fuzzing döngüsü"""
        start_time = time.time()

        while self.is_running:
            # Süre kontrolü
            elapsed = time.time() - start_time
            if elapsed > self.config.duration_sec:
                self.logger.info("Fuzzing süresi doldu")
                break

            # Mesaj sayısı kontrolü
            if self.stats['messages_sent'] >= self.config.max_messages:
                self.logger.info("Maksimum mesaj sayısına ulaşıldı")
                break

            # Fuzzing stratejisine göre mesaj üret
            can_id, data, dlc = self._generate_fuzz_message()

            # Güvenlik kontrolü
            if self.config.safety_mode and self._is_critical_id(can_id):
                continue  # Kritik ID'leri atla

            # Hariç tutulan ID kontrolü
            if self.config.exclude_ids and can_id in self.config.exclude_ids:
                continue

            # Mesaj gönder
            if self.core.send_message(can_id, data, dlc):
                self.stats['messages_sent'] += 1

                # Progress callback
                if self.progress_callback:
                    progress = int((self.stats['messages_sent'] / self.config.max_messages) * 100)
                    self.progress_callback(progress, self.stats['messages_sent'])

            # Interval bekle
            time.sleep(self.config.interval_ms / 1000.0)

        self.is_running = False

    def _generate_fuzz_message(self) -> tuple:
        """
        Fuzzing mesajı üret

        Returns:
            (can_id, data, dlc) tuple
        """
        strategy = self.config.strategy

        if strategy == FuzzingStrategy.RANDOM:
            return self._random_fuzzing()
        elif strategy == FuzzingStrategy.SEQUENTIAL:
            return self._sequential_fuzzing()
        elif strategy == FuzzingStrategy.KNOWN_IDS:
            return self._known_ids_fuzzing()
        elif strategy == FuzzingStrategy.BIT_FLIP:
            return self._bit_flip_fuzzing()
        elif strategy == FuzzingStrategy.BOUNDARY:
            return self._boundary_fuzzing()
        elif strategy == FuzzingStrategy.SMART:
            return self._smart_fuzzing()
        else:
            return self._random_fuzzing()

    def _random_fuzzing(self) -> tuple:
        """Tamamen rastgele fuzzing"""
        can_id = random.randint(self.config.can_id_min, self.config.can_id_max)
        dlc = random.randint(self.config.dlc_min, self.config.dlc_max)
        data = self._generate_data_pattern(dlc)
        return can_id, data, dlc

    def _sequential_fuzzing(self) -> tuple:
        """Sıralı ID tarama"""
        can_id = self.stats['current_id']
        dlc = random.randint(self.config.dlc_min, self.config.dlc_max)
        data = self._generate_data_pattern(dlc)

        # Sonraki ID
        self.stats['current_id'] += 1
        if self.stats['current_id'] > self.config.can_id_max:
            self.stats['current_id'] = self.config.can_id_min

        return can_id, data, dlc

    def _known_ids_fuzzing(self) -> tuple:
        """Bilinen ID'lere fuzzing"""
        # Core'daki bilinen ID'lerden rastgele seç
        known_ids = list(self.core.stats['unique_ids'])
        if not known_ids:
            # Henüz ID bulunamadıysa random yap
            return self._random_fuzzing()

        can_id = random.choice(known_ids)
        dlc = random.randint(self.config.dlc_min, self.config.dlc_max)
        data = self._generate_data_pattern(dlc)
        return can_id, data, dlc

    def _bit_flip_fuzzing(self) -> tuple:
        """Bit flipping fuzzing"""
        can_id = random.randint(self.config.can_id_min, self.config.can_id_max)
        dlc = self.config.dlc_max

        # Mevcut data'dan başla
        data = bytearray(self.stats['current_data'])

        # Rastgele bir bit flip yap
        byte_idx = random.randint(0, dlc - 1)
        bit_idx = random.randint(0, 7)
        data[byte_idx] ^= (1 << bit_idx)

        self.stats['current_data'] = data
        return can_id, bytes(data), dlc

    def _boundary_fuzzing(self) -> tuple:
        """Sınır değerler ile fuzzing"""
        can_id = random.randint(self.config.can_id_min, self.config.can_id_max)
        dlc = random.randint(self.config.dlc_min, self.config.dlc_max)

        # Sınır değerleri
        boundary_values = [
            0x00, 0x01, 0x7F, 0x80, 0xFF,  # 8-bit
            0x7FFF, 0x8000, 0xFFFF,        # 16-bit
            0x7FFFFFFF, 0x80000000, 0xFFFFFFFF  # 32-bit
        ]

        data = bytearray(dlc)
        for i in range(dlc):
            data[i] = random.choice(boundary_values) & 0xFF

        return can_id, bytes(data), dlc

    def _smart_fuzzing(self) -> tuple:
        """Akıllı fuzzing (öğrenen)"""
        # TODO: Gelişmiş fuzzing - feedback based
        # Şu an için random + known IDs kombinasyonu
        if random.random() < 0.5:
            return self._known_ids_fuzzing()
        else:
            return self._random_fuzzing()

    def _generate_data_pattern(self, dlc: int) -> bytes:
        """Data pattern üret"""
        pattern = self.config.data_pattern
        data = bytearray(dlc)

        if pattern == DataPattern.RANDOM:
            for i in range(dlc):
                data[i] = random.randint(0, 255)

        elif pattern == DataPattern.ALL_ZERO:
            data = bytearray(dlc)  # Zaten 0

        elif pattern == DataPattern.ALL_ONE:
            for i in range(dlc):
                data[i] = 0xFF

        elif pattern == DataPattern.ALTERNATING:
            for i in range(dlc):
                data[i] = 0xAA if i % 2 == 0 else 0x55

        elif pattern == DataPattern.INCREMENTAL:
            for i in range(dlc):
                data[i] = i % 256

        elif pattern == DataPattern.BOUNDARY_VALUES:
            boundaries = [0x00, 0x7F, 0x80, 0xFF]
            for i in range(dlc):
                data[i] = random.choice(boundaries)

        return bytes(data)

    def _is_critical_id(self, can_id: int) -> bool:
        """CAN ID kritik mi kontrol et"""
        for critical in self.CRITICAL_IDS:
            if isinstance(critical, range):
                if can_id in critical:
                    return True
            elif can_id == critical:
                return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Fuzzing istatistiklerini al"""
        elapsed = 0
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']

        msg_rate = 0
        if elapsed > 0:
            msg_rate = self.stats['messages_sent'] / elapsed

        return {
            'running': self.is_running,
            'elapsed_time': elapsed,
            'messages_sent': self.stats['messages_sent'],
            'message_rate': msg_rate,
            'responses': self.stats['responses_received'],
            'anomalies': self.stats['anomalies'],
            'crashes': self.stats['crashes'],
            'findings': len(self.interesting_findings)
        }

    def get_results(self) -> FuzzingResult:
        """Fuzzing sonuçlarını al"""
        return FuzzingResult(
            config=self.config,
            start_time=datetime.fromtimestamp(self.stats['start_time']),
            end_time=datetime.now(),
            total_sent=self.stats['messages_sent'],
            responses_received=self.stats['responses_received'],
            anomalies_detected=self.stats['anomalies'],
            crashes_detected=self.stats['crashes'],
            interesting_findings=self.interesting_findings.copy(),
            success=self.stats['messages_sent'] > 0
        )


if __name__ == "__main__":
    # Test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Pentest core oluştur
    core = CANPentestCore(channel=0, bitrate=500000)

    if core.connect():
        # Fuzzer oluştur
        fuzzer = CANFuzzer(core)

        # Config
        config = FuzzingConfig(
            strategy=FuzzingStrategy.RANDOM,
            data_pattern=DataPattern.RANDOM,
            interval_ms=50,
            duration_sec=10,
            max_messages=100,
            safety_mode=True
        )

        # Progress callback
        def on_progress(percent, count):
            print(f"Progress: {percent}% ({count} messages)")

        fuzzer.progress_callback = on_progress

        # Fuzzing başlat
        print("Fuzzing başlatılıyor...")
        fuzzer.start_fuzzing(config)

        try:
            while fuzzer.is_running:
                time.sleep(1)
                stats = fuzzer.get_statistics()
                print(f"Stats: {stats['messages_sent']} sent, "
                      f"{stats['message_rate']:.1f} msg/s")
        except KeyboardInterrupt:
            print("\nDuruyor...")

        fuzzer.stop_fuzzing()

        # Sonuçlar
        results = fuzzer.get_results()
        print(f"\nFuzzing tamamlandı:")
        print(f"  Toplam: {results.total_sent} mesaj")
        print(f"  Yanıt: {results.responses_received}")
        print(f"  Anomali: {results.anomalies_detected}")

        core.disconnect()
