"""
Log Dosya Okuyucu Modülü
ASC ve BLF formatındaki CAN log dosyalarını okur ve analiz eder.
"""

import can
from typing import List, Dict, Optional, Generator
import os
import logging
from datetime import datetime

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogReader:
    """
    CAN log dosyalarını okuma ve analiz sınıfı.
    ASC ve BLF formatlarını destekler.
    """

    SUPPORTED_FORMATS = ['.asc', '.blf', '.log', '.trc']

    def __init__(self):
        """Log reader başlatıcı."""
        self.file_path: Optional[str] = None
        self.messages: List[Dict] = []
        self.file_format: Optional[str] = None

    def load_log_file(self, file_path: str) -> bool:
        """
        Log dosyasını yükle.

        Args:
            file_path: Log dosya yolu (Windows path desteği)

        Returns:
            bool: Yükleme başarılı ise True
        """
        try:
            # Windows dosya yolunu normalize et
            file_path = os.path.normpath(file_path)

            if not os.path.exists(file_path):
                logger.error(f"Log dosyası bulunamadı: {file_path}")
                return False

            # Dosya formatını kontrol et
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                logger.error(f"Desteklenmeyen dosya formatı: {file_ext}")
                logger.info(f"Desteklenen formatlar: {', '.join(self.SUPPORTED_FORMATS)}")
                return False

            self.file_path = file_path
            self.file_format = file_ext
            logger.info(f"Log dosyası yükleniyor: {file_path}")

            # Mesajları oku
            self.messages = self._read_messages()

            logger.info(f"Toplam {len(self.messages)} mesaj yüklendi")
            return True

        except Exception as e:
            logger.error(f"Log dosyası yükleme hatası: {e}")
            return False

    def _read_messages(self) -> List[Dict]:
        """
        Dosyadan tüm mesajları oku.

        Returns:
            List[Dict]: Mesaj listesi
        """
        messages = []

        try:
            # python-can ile log dosyasını aç
            with can.LogReader(self.file_path) as log_reader:
                for msg in log_reader:
                    if isinstance(msg, can.Message):
                        msg_dict = {
                            'timestamp': msg.timestamp,
                            'datetime': datetime.fromtimestamp(msg.timestamp),
                            'arbitration_id': msg.arbitration_id,
                            'is_extended_id': msg.is_extended_id,
                            'dlc': msg.dlc,
                            'data': list(msg.data),
                            'is_error_frame': msg.is_error_frame,
                            'is_remote_frame': msg.is_remote_frame,
                            'channel': getattr(msg, 'channel', 0)
                        }
                        messages.append(msg_dict)

        except Exception as e:
            logger.error(f"Mesaj okuma hatası: {e}")

        return messages

    def get_messages(self, start_index: int = 0, count: Optional[int] = None) -> List[Dict]:
        """
        Mesajları al (pagination desteği).

        Args:
            start_index: Başlangıç indeksi
            count: Alınacak mesaj sayısı (None ise tümü)

        Returns:
            List[Dict]: Mesaj listesi
        """
        if count is None:
            return self.messages[start_index:]
        else:
            return self.messages[start_index:start_index + count]

    def filter_by_can_id(self, can_ids: List[int]) -> List[Dict]:
        """
        CAN ID'ye göre mesajları filtrele.

        Args:
            can_ids: Filtrelenecek CAN ID listesi

        Returns:
            List[Dict]: Filtrelenmiş mesajlar
        """
        return [msg for msg in self.messages if msg['arbitration_id'] in can_ids]

    def filter_by_time_range(self, start_time: float, end_time: float) -> List[Dict]:
        """
        Zaman aralığına göre mesajları filtrele.

        Args:
            start_time: Başlangıç zamanı (timestamp)
            end_time: Bitiş zamanı (timestamp)

        Returns:
            List[Dict]: Filtrelenmiş mesajlar
        """
        return [msg for msg in self.messages
                if start_time <= msg['timestamp'] <= end_time]

    def get_unique_can_ids(self) -> List[int]:
        """
        Dosyadaki unique CAN ID'leri al.

        Returns:
            List[int]: Unique CAN ID listesi (sıralı)
        """
        unique_ids = set(msg['arbitration_id'] for msg in self.messages)
        return sorted(list(unique_ids))

    def get_statistics(self) -> Dict:
        """
        Log dosyası istatistiklerini al.

        Returns:
            Dict: İstatistik bilgileri
        """
        if not self.messages:
            return {
                'total_messages': 0,
                'unique_can_ids': 0,
                'duration': 0,
                'start_time': None,
                'end_time': None,
                'messages_per_second': 0
            }

        timestamps = [msg['timestamp'] for msg in self.messages]
        start_time = min(timestamps)
        end_time = max(timestamps)
        duration = end_time - start_time

        unique_ids = self.get_unique_can_ids()

        # CAN ID bazında mesaj sayıları
        id_counts = {}
        for msg in self.messages:
            can_id = msg['arbitration_id']
            id_counts[can_id] = id_counts.get(can_id, 0) + 1

        return {
            'total_messages': len(self.messages),
            'unique_can_ids': len(unique_ids),
            'can_id_list': [f"0x{id:X}" for id in unique_ids],
            'duration': duration,
            'start_time': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f'),
            'end_time': datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S.%f'),
            'messages_per_second': len(self.messages) / duration if duration > 0 else 0,
            'file_path': self.file_path,
            'file_format': self.file_format,
            'id_message_counts': {f"0x{k:X}": v for k, v in sorted(id_counts.items())}
        }

    def get_message_count_by_id(self) -> Dict[int, int]:
        """
        Her CAN ID için mesaj sayısını al.

        Returns:
            Dict[int, int]: CAN ID -> mesaj sayısı mapping
        """
        counts = {}
        for msg in self.messages:
            can_id = msg['arbitration_id']
            counts[can_id] = counts.get(can_id, 0) + 1
        return counts

    def search_data_pattern(self, pattern: List[int], mask: Optional[List[int]] = None) -> List[Dict]:
        """
        Veri pattern'ine göre mesaj ara.

        Args:
            pattern: Aranacak veri pattern'i
            mask: Maske (None ise exact match)

        Returns:
            List[Dict]: Eşleşen mesajlar
        """
        matches = []

        for msg in self.messages:
            data = msg['data']

            # Pattern uzunluğu kontrolü
            if len(data) < len(pattern):
                continue

            # Pattern kontrolü
            is_match = True
            for i, pattern_byte in enumerate(pattern):
                if mask:
                    # Mask ile karşılaştır
                    if (data[i] & mask[i]) != (pattern_byte & mask[i]):
                        is_match = False
                        break
                else:
                    # Exact match
                    if data[i] != pattern_byte:
                        is_match = False
                        break

            if is_match:
                matches.append(msg)

        return matches

    def export_to_asc(self, output_file: str, messages: Optional[List[Dict]] = None) -> bool:
        """
        Mesajları ASC formatında export et.

        Args:
            output_file: Çıktı dosya yolu
            messages: Export edilecek mesajlar (None ise tümü)

        Returns:
            bool: Başarılı ise True
        """
        if messages is None:
            messages = self.messages

        if not messages:
            logger.warning("Export edilecek mesaj yok")
            return False

        try:
            output_file = os.path.normpath(output_file)

            with open(output_file, 'w', encoding='utf-8') as f:
                # ASC header
                f.write("date " + datetime.now().strftime("%a %b %d %I:%M:%S %p %Y") + "\n")
                f.write("base hex  timestamps absolute\n")
                f.write("internal events logged\n")
                f.write("Begin Triggerblock " + datetime.now().strftime("%a %b %d %I:%M:%S %p %Y") + "\n")

                # Mesajları yaz
                for msg in messages:
                    timestamp = msg['timestamp']
                    can_id = msg['arbitration_id']
                    dlc = msg['dlc']
                    data = msg['data']

                    # ASC format: timestamp channel ID Rx/Tx d length data
                    data_str = ' '.join(f"{b:02X}" for b in data)
                    f.write(f"{timestamp:12.6f} 1  {can_id:X}  Rx   d {dlc} {data_str}\n")

                f.write("End TriggerBlock\n")

            logger.info(f"ASC dosyası oluşturuldu: {output_file}")
            return True

        except Exception as e:
            logger.error(f"ASC export hatası: {e}")
            return False

    def get_time_range(self) -> tuple:
        """
        Log dosyasının zaman aralığını al.

        Returns:
            tuple: (min_timestamp, max_timestamp)
        """
        if not self.messages:
            return (0, 0)

        timestamps = [msg['timestamp'] for msg in self.messages]
        return (min(timestamps), max(timestamps))

    def clear(self):
        """Yüklü verileri temizle."""
        self.messages = []
        self.file_path = None
        self.file_format = None
        logger.info("Log veriler temizlendi")


class LogWriter:
    """
    CAN mesajlarını log dosyasına yazma sınıfı.
    """

    def __init__(self, file_path: str, file_format: str = 'asc'):
        """
        Log writer başlatıcı.

        Args:
            file_path: Çıktı dosya yolu
            file_format: Dosya formatı ('asc', 'blf', 'csv')
        """
        self.file_path = os.path.normpath(file_path)
        self.file_format = file_format.lower()
        self.writer: Optional[can.Logger] = None

    def open(self) -> bool:
        """
        Log dosyasını yazmak için aç.

        Returns:
            bool: Başarılı ise True
        """
        try:
            self.writer = can.Logger(self.file_path)
            logger.info(f"Log writer açıldı: {self.file_path}")
            return True

        except Exception as e:
            logger.error(f"Log writer açma hatası: {e}")
            return False

    def write_message(self, can_id: int, data: List[int], timestamp: Optional[float] = None):
        """
        CAN mesajı yaz.

        Args:
            can_id: CAN ID
            data: Veri bytes
            timestamp: Zaman damgası (None ise otomatik)
        """
        if not self.writer:
            logger.error("Log writer açık değil!")
            return

        try:
            message = can.Message(
                arbitration_id=can_id,
                data=data,
                timestamp=timestamp or datetime.now().timestamp()
            )
            self.writer(message)

        except Exception as e:
            logger.error(f"Mesaj yazma hatası: {e}")

    def close(self):
        """Log dosyasını kapat."""
        if self.writer:
            self.writer.stop()
            self.writer = None
            logger.info("Log writer kapatıldı")


if __name__ == "__main__":
    # Test kodu
    print("Log Reader Modülü Test Ediliyor...")

    reader = LogReader()

    # Örnek kullanım
    # if reader.load_log_file("example.asc"):
    #     stats = reader.get_statistics()
    #     print(f"İstatistikler: {stats}")
    #
    #     messages = reader.get_messages(0, 10)
    #     print(f"\nİlk 10 mesaj: {len(messages)}")

    print("Test tamamlandı (gerçek test için log dosyası gerekli)")
