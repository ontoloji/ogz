"""
CAN Bus Sniffer ve Traffic Analyzer Modülü
Kvaser Memorator 2xHS - Windows

CAN bus trafiğini yakalama, analiz ve görselleştirme
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import struct

from can_pentest_core import CANPentestCore, CANMessage, PentestMode


@dataclass
class MessageStats:
    """Tek bir CAN ID için istatistikler"""
    can_id: int
    count: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0
    min_interval: float = float('inf')
    max_interval: float = 0.0
    avg_interval: float = 0.0
    data_samples: List[bytes] = field(default_factory=list)
    max_samples: int = 100


@dataclass
class TrafficAnalysis:
    """Traffic analiz sonuçları"""
    start_time: datetime
    end_time: datetime
    total_messages: int
    unique_ids: int
    bus_load_percent: float
    top_talkers: List[tuple]  # (can_id, count)
    message_stats: Dict[int, MessageStats]
    anomalies: List[str]


class CANSniffer:
    """
    CAN Bus Sniffer ve Analyzer

    Pasif mod CAN bus dinleme ve analiz
    """

    # Bilinen CAN protokolleri ve ID aralıkları
    PROTOCOLS = {
        'ISO-TP': range(0x7E0, 0x7EF),
        'UDS': [0x7DF, 0x7E0, 0x7E8],
        'OBD-II': [0x7DF, 0x7E0, 0x7E8],
        'J1939': range(0x00, 0x1FFFFFFF),  # 29-bit
    }

    # Bilinen serviler (örnek)
    KNOWN_SERVICES = {
        0x10: "Diagnostic Session Control",
        0x11: "ECU Reset",
        0x14: "Clear Diagnostic Information",
        0x19: "Read DTC Information",
        0x22: "Read Data By Identifier",
        0x23: "Read Memory By Address",
        0x27: "Security Access",
        0x28: "Communication Control",
        0x2E: "Write Data By Identifier",
        0x31: "Routine Control",
        0x34: "Request Download",
        0x35: "Request Upload",
        0x36: "Transfer Data",
        0x37: "Request Transfer Exit",
        0x3E: "Tester Present",
    }

    def __init__(self, pentest_core: CANPentestCore):
        """
        Args:
            pentest_core: CAN pentest core instance
        """
        self.core = pentest_core

        # İstatistikler
        self.message_stats: Dict[int, MessageStats] = {}
        self.total_messages = 0
        self.start_time = None

        # Traffic analiz
        self.bus_bitrate = self.core.bitrate
        self.bus_load = 0.0

        # Anomali tespiti
        self.anomalies: List[str] = []
        self.enable_anomaly_detection = True

        # Callback'ler
        self.message_callback: Optional[Callable[[CANMessage], None]] = None
        self.stats_callback: Optional[Callable[[MessageStats], None]] = None
        self.anomaly_callback: Optional[Callable[[str], None]] = None

        # Filtering
        self.filter_ids: Optional[List[int]] = None  # None = tümü
        self.filter_mode: str = "include"  # include / exclude

        self.logger = logging.getLogger(__name__)

    def start_capture(self):
        """CAN capture başlat"""
        self.core.set_mode(PentestMode.PASSIVE)

        # Core'a callback ekle
        self.core.message_callback = self._on_message

        self.start_time = time.time()
        self.total_messages = 0
        self.message_stats.clear()
        self.anomalies.clear()

        self.logger.info("CAN capture başlatıldı (PASSIVE mode)")

    def stop_capture(self):
        """Capture durdur"""
        self.core.message_callback = None
        self.logger.info("CAN capture durduruldu")

    def _on_message(self, msg: CANMessage):
        """Her CAN mesajında çağrılır"""
        # Filter kontrolü
        if not self._filter_check(msg.can_id):
            return

        # İstatistik güncelle
        self._update_stats(msg)

        # Anomali tespiti
        if self.enable_anomaly_detection:
            self._detect_anomalies(msg)

        # User callback
        if self.message_callback:
            self.message_callback(msg)

    def _filter_check(self, can_id: int) -> bool:
        """Mesaj filter kontrolü"""
        if self.filter_ids is None:
            return True  # Filter yok, tümü geç

        if self.filter_mode == "include":
            return can_id in self.filter_ids
        else:  # exclude
            return can_id not in self.filter_ids

    def _update_stats(self, msg: CANMessage):
        """İstatistikleri güncelle"""
        self.total_messages += 1

        can_id = msg.can_id

        # Yeni ID
        if can_id not in self.message_stats:
            self.message_stats[can_id] = MessageStats(
                can_id=can_id,
                first_seen=msg.timestamp
            )

        stats = self.message_stats[can_id]
        stats.count += 1
        stats.last_seen = msg.timestamp

        # İnterval hesapla
        if stats.count > 1:
            interval = msg.timestamp - stats.last_seen
            stats.min_interval = min(stats.min_interval, interval)
            stats.max_interval = max(stats.max_interval, interval)

            # Average interval (moving average)
            alpha = 0.1
            if stats.avg_interval == 0:
                stats.avg_interval = interval
            else:
                stats.avg_interval = alpha * interval + (1 - alpha) * stats.avg_interval

        # Data sample sakla (limited)
        if len(stats.data_samples) < stats.max_samples:
            stats.data_samples.append(msg.data)

        # Stats callback
        if self.stats_callback:
            self.stats_callback(stats)

    def _detect_anomalies(self, msg: CANMessage):
        """Anomali tespiti"""
        can_id = msg.can_id

        # 1. Yeni ID tespiti
        if can_id not in self.message_stats or self.message_stats[can_id].count == 1:
            anomaly = f"Yeni CAN ID tespit edildi: 0x{can_id:03X}"
            self._report_anomaly(anomaly)

        # 2. Beklenmeyen protocol tespiti
        if self._is_diagnostic_message(msg):
            anomaly = f"Diagnostik mesaj: ID=0x{can_id:03X}, Data={msg.data.hex()}"
            self._report_anomaly(anomaly)

        # 3. Data değişimi tespiti
        stats = self.message_stats.get(can_id)
        if stats and len(stats.data_samples) > 1:
            # Son 2 sample'ı karşılaştır
            if stats.data_samples[-1] != stats.data_samples[-2]:
                # Data değişti (normal olabilir, ama raporla)
                pass

        # 4. Interval anomalisi
        if stats and stats.count > 10:
            interval = msg.timestamp - stats.last_seen
            # Çok hızlı veya çok yavaş
            if interval < stats.min_interval * 0.5 or interval > stats.max_interval * 2:
                anomaly = f"Interval anomalisi: ID=0x{can_id:03X}, interval={interval:.3f}s"
                self._report_anomaly(anomaly)

    def _is_diagnostic_message(self, msg: CANMessage) -> bool:
        """Diagnostik mesaj mı kontrol et"""
        # UDS / ISO-TP mesajları
        if msg.can_id in [0x7DF] or (0x7E0 <= msg.can_id <= 0x7EF):
            return True

        # UDS service ID kontrolü
        if len(msg.data) > 0:
            service_id = msg.data[0]
            if service_id in self.KNOWN_SERVICES:
                return True

        return False

    def _report_anomaly(self, anomaly: str):
        """Anomali raporla"""
        if anomaly not in self.anomalies:
            self.anomalies.append(anomaly)
            self.logger.warning(f"ANOMALY: {anomaly}")

            if self.anomaly_callback:
                self.anomaly_callback(anomaly)

    def set_filter(self, ids: Optional[List[int]], mode: str = "include"):
        """
        CAN ID filtresi ayarla

        Args:
            ids: CAN ID listesi (None = tümü)
            mode: "include" veya "exclude"
        """
        self.filter_ids = ids
        self.filter_mode = mode
        self.logger.info(f"Filter ayarlandı: {mode} {len(ids) if ids else 'all'} IDs")

    def calculate_bus_load(self) -> float:
        """
        Bus load hesapla (%)

        CAN mesajının ortalama boyutu: ~111 bit (standard frame)
        """
        if not self.start_time:
            return 0.0

        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0.0

        # Mesaj rate
        msg_rate = self.total_messages / elapsed

        # Her mesaj ~111 bit (worst case)
        bits_per_message = 111

        # Bus load
        bits_per_second = msg_rate * bits_per_message
        bus_load = (bits_per_second / self.bus_bitrate) * 100

        self.bus_load = min(bus_load, 100.0)
        return self.bus_load

    def get_top_talkers(self, top_n: int = 10) -> List[tuple]:
        """
        En çok mesaj gönderen CAN ID'ler

        Args:
            top_n: Kaç tane gösterilecek

        Returns:
            [(can_id, count), ...] listesi
        """
        sorted_ids = sorted(
            self.message_stats.items(),
            key=lambda x: x[1].count,
            reverse=True
        )
        return [(can_id, stats.count) for can_id, stats in sorted_ids[:top_n]]

    def analyze_traffic(self) -> TrafficAnalysis:
        """Traffic analizi yap"""
        return TrafficAnalysis(
            start_time=datetime.fromtimestamp(self.start_time) if self.start_time else datetime.now(),
            end_time=datetime.now(),
            total_messages=self.total_messages,
            unique_ids=len(self.message_stats),
            bus_load_percent=self.calculate_bus_load(),
            top_talkers=self.get_top_talkers(),
            message_stats=self.message_stats.copy(),
            anomalies=self.anomalies.copy()
        )

    def decode_uds_message(self, msg: CANMessage) -> Optional[str]:
        """
        UDS mesajını decode et

        Args:
            msg: CAN mesajı

        Returns:
            Decoded string veya None
        """
        if len(msg.data) == 0:
            return None

        # UDS kontrolü
        if not self._is_diagnostic_message(msg):
            return None

        service_id = msg.data[0]

        # Positive response kontrolü (0x40 + service_id)
        if service_id >= 0x40:
            original_service = service_id - 0x40
            service_name = self.KNOWN_SERVICES.get(original_service, f"Unknown (0x{original_service:02X})")
            return f"UDS Response: {service_name}"

        # Negative response (0x7F)
        if service_id == 0x7F and len(msg.data) >= 3:
            failed_service = msg.data[1]
            nrc = msg.data[2]  # Negative Response Code
            service_name = self.KNOWN_SERVICES.get(failed_service, f"Unknown (0x{failed_service:02X})")
            return f"UDS Negative Response: {service_name}, NRC=0x{nrc:02X}"

        # Normal request
        service_name = self.KNOWN_SERVICES.get(service_id, f"Unknown (0x{service_id:02X})")
        return f"UDS Request: {service_name}"

    def export_statistics(self, filename: str) -> bool:
        """
        İstatistikleri CSV olarak export et

        Args:
            filename: Export dosyası

        Returns:
            Başarı durumu
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("CAN_ID,Count,First_Seen,Last_Seen,Min_Interval,Max_Interval,Avg_Interval\n")

                # Data
                for can_id, stats in sorted(self.message_stats.items()):
                    f.write(
                        f"0x{can_id:03X},"
                        f"{stats.count},"
                        f"{stats.first_seen:.6f},"
                        f"{stats.last_seen:.6f},"
                        f"{stats.min_interval:.6f},"
                        f"{stats.max_interval:.6f},"
                        f"{stats.avg_interval:.6f}\n"
                    )

            self.logger.info(f"Statistics exported: {filename}")
            return True

        except Exception as e:
            self.logger.error(f"Export error: {e}")
            return False

    def print_summary(self):
        """Özet bilgileri ekrana yazdır"""
        print("\n" + "=" * 60)
        print("CAN BUS TRAFFIC SUMMARY")
        print("=" * 60)

        elapsed = 0
        if self.start_time:
            elapsed = time.time() - self.start_time

        print(f"Capture Time: {elapsed:.1f} seconds")
        print(f"Total Messages: {self.total_messages}")
        print(f"Unique IDs: {len(self.message_stats)}")
        print(f"Bus Load: {self.calculate_bus_load():.2f}%")
        print(f"Anomalies: {len(self.anomalies)}")

        print("\nTop 10 Talkers:")
        print("-" * 40)
        for can_id, count in self.get_top_talkers(10):
            percent = (count / self.total_messages) * 100 if self.total_messages > 0 else 0
            print(f"  0x{can_id:03X}: {count:6d} messages ({percent:5.1f}%)")

        if self.anomalies:
            print("\nAnomalies Detected:")
            print("-" * 40)
            for anomaly in self.anomalies[:10]:  # İlk 10
                print(f"  - {anomaly}")

        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Core oluştur
    core = CANPentestCore(channel=0, bitrate=500000)

    if core.connect():
        # Sniffer oluştur
        sniffer = CANSniffer(core)

        # Message callback
        def on_message(msg: CANMessage):
            decoded = sniffer.decode_uds_message(msg)
            if decoded:
                print(f"[{msg.timestamp:.3f}] {decoded}")
            else:
                print(f"[{msg.timestamp:.3f}] ID: 0x{msg.can_id:03X} Data: {msg.data.hex()}")

        sniffer.message_callback = on_message

        # Capture başlat
        sniffer.start_capture()

        print("CAN Sniffer başlatıldı. CTRL+C ile çıkış...")
        try:
            while True:
                time.sleep(5)
                # Her 5 saniyede özet
                print(f"\n[Stats] Messages: {sniffer.total_messages}, "
                      f"IDs: {len(sniffer.message_stats)}, "
                      f"Load: {sniffer.calculate_bus_load():.1f}%")
        except KeyboardInterrupt:
            print("\nDuruyor...")

        sniffer.stop_capture()

        # Özet
        sniffer.print_summary()

        # Export
        sniffer.export_statistics("can_traffic_stats.csv")

        core.disconnect()
