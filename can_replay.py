"""
CAN Bus Replay Attack Modülü
Kvaser Memorator 2xHS - Windows

Yakalanan CAN trafiğini tekrar oynatma (replay attack)
Güvenlik testleri için kullanılır
"""

import logging
import time
import threading
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import pickle
import json

from can_pentest_core import CANPentestCore, CANMessage, PentestMode


@dataclass
class ReplayConfig:
    """Replay konfigürasyonu"""
    # Timing
    preserve_timing: bool = True  # Orijinal timing'i koru
    speed_multiplier: float = 1.0  # Hız çarpanı (1.0 = normal, 2.0 = 2x hızlı)
    loop_count: int = 1  # Kaç kez tekrarla (0 = sonsuz)

    # Filtering
    filter_ids: Optional[List[int]] = None  # Sadece bu ID'leri replay et
    exclude_ids: Optional[List[int]] = None  # Bu ID'leri hariç tut

    # Modification
    modify_data: bool = False  # Data'yı değiştir
    modify_callback: Optional[Callable[[CANMessage], CANMessage]] = None

    # Safety
    safety_mode: bool = True  # Kritik mesajları engelle


@dataclass
class ReplayResult:
    """Replay sonucu"""
    start_time: datetime
    end_time: datetime
    total_replayed: int
    total_skipped: int
    errors: int
    success: bool


class CANReplay:
    """
    CAN Replay Attack Tool

    Yakalanan CAN trafiğini tekrar oynatır
    """

    # Kritik mesajlar (güvenli modda replay edilmez)
    CRITICAL_IDS = [
        0x140,  # Engine RPM
        0x220,  # Steering
        0x224,  # Brake
        0x244,  # Speed
        0x320,  # Airbag
    ]

    def __init__(self, pentest_core: CANPentestCore):
        """
        Args:
            pentest_core: CAN pentest core instance
        """
        self.core = pentest_core
        self.config = ReplayConfig()

        # Replay data
        self.messages: List[CANMessage] = []
        self.current_index = 0

        # State
        self.is_running = False
        self.replay_thread = None

        # Stats
        self.stats = {
            'replayed': 0,
            'skipped': 0,
            'errors': 0,
            'start_time': None,
            'loop_number': 0
        }

        # Callbacks
        self.progress_callback: Optional[Callable[[int, int], None]] = None
        self.complete_callback: Optional[Callable[[ReplayResult], None]] = None

        self.logger = logging.getLogger(__name__)

    def load_capture(self, messages: List[CANMessage]) -> bool:
        """
        Capture'ı yükle (memory'den)

        Args:
            messages: CAN mesaj listesi

        Returns:
            Başarı durumu
        """
        if not messages:
            self.logger.error("Boş mesaj listesi!")
            return False

        self.messages = messages.copy()
        self.logger.info(f"{len(self.messages)} mesaj yüklendi")
        return True

    def load_from_file(self, filename: str) -> bool:
        """
        Capture dosyasından yükle

        Desteklenen formatlar:
        - .csv: CSV format (core.export_capture)
        - .pkl: Pickle format (binary)
        - .json: JSON format

        Args:
            filename: Dosya yolu

        Returns:
            Başarı durumu
        """
        try:
            if filename.endswith('.csv'):
                return self._load_csv(filename)
            elif filename.endswith('.pkl'):
                return self._load_pickle(filename)
            elif filename.endswith('.json'):
                return self._load_json(filename)
            else:
                self.logger.error(f"Desteklenmeyen dosya formatı: {filename}")
                return False

        except Exception as e:
            self.logger.error(f"Dosya yükleme hatası: {e}")
            return False

    def _load_csv(self, filename: str) -> bool:
        """CSV dosyasından yükle"""
        import csv

        messages = []
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    msg = CANMessage(
                        timestamp=float(row['Timestamp']),
                        can_id=int(row['CAN_ID'], 16),
                        dlc=int(row['DLC']),
                        data=bytes.fromhex(row['Data'])
                    )
                    messages.append(msg)
                except Exception as e:
                    self.logger.warning(f"CSV satır hatası: {e}")

        return self.load_capture(messages)

    def _load_pickle(self, filename: str) -> bool:
        """Pickle dosyasından yükle"""
        with open(filename, 'rb') as f:
            messages = pickle.load(f)
        return self.load_capture(messages)

    def _load_json(self, filename: str) -> bool:
        """JSON dosyasından yükle"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = []
        for item in data:
            msg = CANMessage(
                timestamp=item['timestamp'],
                can_id=item['can_id'],
                dlc=item['dlc'],
                data=bytes.fromhex(item['data'])
            )
            messages.append(msg)

        return self.load_capture(messages)

    def save_to_file(self, filename: str) -> bool:
        """
        Mesajları dosyaya kaydet

        Args:
            filename: Dosya yolu (.pkl, .json, .csv)

        Returns:
            Başarı durumu
        """
        try:
            if filename.endswith('.pkl'):
                with open(filename, 'wb') as f:
                    pickle.dump(self.messages, f)

            elif filename.endswith('.json'):
                data = []
                for msg in self.messages:
                    data.append({
                        'timestamp': msg.timestamp,
                        'can_id': msg.can_id,
                        'dlc': msg.dlc,
                        'data': msg.data.hex()
                    })
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

            elif filename.endswith('.csv'):
                # Core'un export metodunu kullan
                self.core.message_buffer = self.messages
                return self.core.export_capture(filename)

            else:
                self.logger.error("Desteklenmeyen format")
                return False

            self.logger.info(f"Kaydedildi: {filename}")
            return True

        except Exception as e:
            self.logger.error(f"Kaydetme hatası: {e}")
            return False

    def start_replay(self, config: Optional[ReplayConfig] = None) -> bool:
        """
        Replay başlat

        Args:
            config: Replay konfigürasyonu

        Returns:
            Başarı durumu
        """
        if self.is_running:
            self.logger.warning("Replay zaten çalışıyor!")
            return False

        if not self.core.is_connected:
            self.logger.error("CAN bağlantısı yok!")
            return False

        if not self.messages:
            self.logger.error("Replay için mesaj yok!")
            return False

        if config:
            self.config = config

        # Safety kontrolü
        if self.config.safety_mode:
            self.logger.warning("SAFETY MODE: Kritik mesajlar replay edilmeyecek")

        # Core'u REPLAY moduna al
        self.core.set_mode(PentestMode.REPLAY)

        # Stats sıfırla
        self._reset_stats()

        # Thread başlat
        self.is_running = True
        self.replay_thread = threading.Thread(
            target=self._replay_loop,
            daemon=True,
            name="Replay"
        )
        self.replay_thread.start()

        self.logger.info("Replay başlatıldı")
        return True

    def stop_replay(self):
        """Replay durdur"""
        self.is_running = False

        if self.replay_thread:
            self.replay_thread.join(timeout=2.0)

        self.core.set_mode(PentestMode.PASSIVE)
        self.logger.info("Replay durduruldu")

    def _reset_stats(self):
        """Stats sıfırla"""
        self.stats = {
            'replayed': 0,
            'skipped': 0,
            'errors': 0,
            'start_time': time.time(),
            'loop_number': 0
        }
        self.current_index = 0

    def _replay_loop(self):
        """Replay ana döngüsü"""
        loop = 0

        while self.is_running:
            loop += 1
            self.stats['loop_number'] = loop

            self.logger.info(f"Replay loop {loop} başlıyor...")

            # Mesajları replay et
            self._replay_messages()

            # Loop kontrolü
            if self.config.loop_count > 0 and loop >= self.config.loop_count:
                self.logger.info(f"Loop limit reached: {loop}")
                break

            # Sonsuz loop için kısa bekle
            if self.config.loop_count == 0:
                time.sleep(0.1)

        self.is_running = False

        # Complete callback
        if self.complete_callback:
            result = self._get_result()
            self.complete_callback(result)

    def _replay_messages(self):
        """Mesajları replay et"""
        if not self.messages:
            return

        # İlk mesajın timestamp'i
        first_ts = self.messages[0].timestamp
        start_time = time.time()

        for i, msg in enumerate(self.messages):
            if not self.is_running:
                break

            # Filter kontrolü
            if not self._should_replay(msg):
                self.stats['skipped'] += 1
                continue

            # Timing
            if self.config.preserve_timing:
                # Orijinal timing'i koru
                elapsed = msg.timestamp - first_ts
                elapsed /= self.config.speed_multiplier

                target_time = start_time + elapsed
                current_time = time.time()

                if current_time < target_time:
                    time.sleep(target_time - current_time)

            # Modification
            replay_msg = msg
            if self.config.modify_data and self.config.modify_callback:
                replay_msg = self.config.modify_callback(msg)

            # Send
            try:
                if self.core.send_message(replay_msg.can_id, replay_msg.data, replay_msg.dlc):
                    self.stats['replayed'] += 1
                else:
                    self.stats['errors'] += 1
            except Exception as e:
                self.logger.error(f"Replay hatası: {e}")
                self.stats['errors'] += 1

            # Progress callback
            if self.progress_callback and i % 100 == 0:
                progress = int((i / len(self.messages)) * 100)
                self.progress_callback(progress, i)

    def _should_replay(self, msg: CANMessage) -> bool:
        """Mesaj replay edilmeli mi?"""
        can_id = msg.can_id

        # Safety mode
        if self.config.safety_mode and can_id in self.CRITICAL_IDS:
            return False

        # Include filter
        if self.config.filter_ids is not None:
            if can_id not in self.config.filter_ids:
                return False

        # Exclude filter
        if self.config.exclude_ids is not None:
            if can_id in self.config.exclude_ids:
                return False

        return True

    def _get_result(self) -> ReplayResult:
        """Sonuç oluştur"""
        return ReplayResult(
            start_time=datetime.fromtimestamp(self.stats['start_time']),
            end_time=datetime.now(),
            total_replayed=self.stats['replayed'],
            total_skipped=self.stats['skipped'],
            errors=self.stats['errors'],
            success=self.stats['errors'] == 0
        )

    def get_statistics(self) -> Dict[str, Any]:
        """İstatistikleri al"""
        elapsed = 0
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']

        replay_rate = 0
        if elapsed > 0:
            replay_rate = self.stats['replayed'] / elapsed

        return {
            'running': self.is_running,
            'elapsed': elapsed,
            'loop_number': self.stats['loop_number'],
            'replayed': self.stats['replayed'],
            'skipped': self.stats['skipped'],
            'errors': self.stats['errors'],
            'rate': replay_rate,
            'total_messages': len(self.messages)
        }


if __name__ == "__main__":
    # Test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Core
    core = CANPentestCore(channel=0, bitrate=500000)

    if core.connect():
        # Replay oluştur
        replay = CANReplay(core)

        # Dummy mesajlar oluştur (test)
        test_messages = []
        for i in range(100):
            msg = CANMessage(
                timestamp=i * 0.01,  # 10ms interval
                can_id=0x100 + (i % 10),
                data=bytes([i % 256] * 8),
                dlc=8
            )
            test_messages.append(msg)

        # Load
        replay.load_capture(test_messages)

        # Config
        config = ReplayConfig(
            preserve_timing=True,
            speed_multiplier=1.0,
            loop_count=2,
            safety_mode=True
        )

        # Progress callback
        def on_progress(percent, count):
            print(f"Progress: {percent}% ({count} messages)")

        def on_complete(result: ReplayResult):
            print(f"\nReplay tamamlandı:")
            print(f"  Replayed: {result.total_replayed}")
            print(f"  Skipped: {result.total_skipped}")
            print(f"  Errors: {result.errors}")

        replay.progress_callback = on_progress
        replay.complete_callback = on_complete

        # Start
        print("Replay başlatılıyor...")
        replay.start_replay(config)

        try:
            while replay.is_running:
                time.sleep(1)
                stats = replay.get_statistics()
                print(f"Stats: Loop {stats['loop_number']}, "
                      f"{stats['replayed']} replayed, {stats['rate']:.1f} msg/s")
        except KeyboardInterrupt:
            print("\nDuruyor...")

        replay.stop_replay()
        core.disconnect()
