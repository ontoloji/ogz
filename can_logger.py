"""
CAN Bus Test Arayüzü - Loglama Modülü
CAN mesaj loglama, CSV export, dosya yönetimi
"""

import csv
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from can_message_manager import ReceivedCANMessage


class CANLogger:
    """
    CAN mesaj logger
    CSV formatında mesaj kaydı ve export
    """

    def __init__(self, log_directory: str = "can_logs"):
        """
        Args:
            log_directory: Log dosyalarının kaydedileceği klasör
        """
        self.log_directory = log_directory
        self.current_log_file: Optional[str] = None
        self.is_logging = False
        self.logged_messages: List[ReceivedCANMessage] = []
        self.logger = logging.getLogger(__name__)

        # Log klasörünü oluştur
        Path(self.log_directory).mkdir(parents=True, exist_ok=True)

    def start_logging(self, session_name: str = "") -> str:
        """
        Loglama başlat

        Args:
            session_name: Opsiyonel oturum adı

        Returns:
            Log dosya yolu
        """
        if self.is_logging:
            self.logger.warning("Loglama zaten aktif")
            return self.current_log_file

        # Dosya adı oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if session_name:
            filename = f"CAN_LOG_{session_name}_{timestamp}.csv"
        else:
            filename = f"CAN_LOG_{timestamp}.csv"

        self.current_log_file = os.path.join(self.log_directory, filename)
        self.logged_messages.clear()
        self.is_logging = True

        self.logger.info(f"Loglama başlatıldı: {self.current_log_file}")
        return self.current_log_file

    def stop_logging(self) -> bool:
        """
        Loglama durdur ve dosyaya kaydet

        Returns:
            Başarılı ise True
        """
        if not self.is_logging:
            self.logger.warning("Loglama aktif değil")
            return False

        # Dosyaya kaydet
        success = self.export_to_csv(self.current_log_file)

        self.is_logging = False
        self.logger.info(f"Loglama durduruldu. Toplam {len(self.logged_messages)} mesaj kaydedildi.")

        return success

    def log_message(self, message: ReceivedCANMessage):
        """
        Mesajı log buffer'ına ekle

        Args:
            message: Loglanacak mesaj
        """
        if self.is_logging:
            self.logged_messages.append(message)

    def export_to_csv(self, filepath: str, messages: Optional[List[ReceivedCANMessage]] = None) -> bool:
        """
        Mesajları CSV dosyasına export et

        Args:
            filepath: Hedef dosya yolu
            messages: Export edilecek mesajlar (None ise buffer kullanılır)

        Returns:
            Başarılı ise True
        """
        if messages is None:
            messages = self.logged_messages

        if not messages:
            self.logger.warning("Export edilecek mesaj yok")
            return False

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(['Timestamp', 'CAN ID', 'DLC', 'Data', 'Direction'])

                # Mesajları yaz
                for msg in messages:
                    writer.writerow(msg.to_csv_row())

            self.logger.info(f"CSV export başarılı: {filepath} ({len(messages)} mesaj)")
            return True

        except Exception as e:
            self.logger.error(f"CSV export hatası: {e}")
            return False

    def export_to_txt(self, filepath: str, messages: Optional[List[ReceivedCANMessage]] = None) -> bool:
        """
        Mesajları TXT dosyasına export et (okunabilir format)

        Args:
            filepath: Hedef dosya yolu
            messages: Export edilecek mesajlar (None ise buffer kullanılır)

        Returns:
            Başarılı ise True
        """
        if messages is None:
            messages = self.logged_messages

        if not messages:
            self.logger.warning("Export edilecek mesaj yok")
            return False

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header
                f.write("=" * 80 + "\n")
                f.write("CAN Bus Mesaj Logu\n")
                f.write(f"Toplam Mesaj: {len(messages)}\n")
                f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")

                # Tablo header
                f.write(f"{'Zaman':<15} | {'CAN ID':<10} | {'DLC':<3} | {'Data':<30} | {'Dir':<3}\n")
                f.write("-" * 80 + "\n")

                # Mesajları yaz
                for msg in messages:
                    f.write(msg.to_log_string() + "\n")

            self.logger.info(f"TXT export başarılı: {filepath} ({len(messages)} mesaj)")
            return True

        except Exception as e:
            self.logger.error(f"TXT export hatası: {e}")
            return False

    def get_logged_messages(self) -> List[ReceivedCANMessage]:
        """Loglanan mesajları al"""
        return self.logged_messages.copy()

    def clear_buffer(self):
        """Log buffer'ını temizle"""
        count = len(self.logged_messages)
        self.logged_messages.clear()
        self.logger.info(f"Log buffer temizlendi ({count} mesaj silindi)")

    def get_statistics(self) -> dict:
        """Log istatistiklerini al"""
        if not self.logged_messages:
            return {
                'total_messages': 0,
                'is_logging': self.is_logging,
                'current_file': self.current_log_file,
                'unique_ids': 0,
                'rx_count': 0,
                'tx_count': 0
            }

        # Benzersiz ID'leri say
        unique_ids = len(set(msg.can_id for msg in self.logged_messages))

        # Yön bazlı sayım
        rx_count = sum(1 for msg in self.logged_messages if msg.direction == "RX")
        tx_count = sum(1 for msg in self.logged_messages if msg.direction == "TX")

        return {
            'total_messages': len(self.logged_messages),
            'is_logging': self.is_logging,
            'current_file': self.current_log_file,
            'unique_ids': unique_ids,
            'rx_count': rx_count,
            'tx_count': tx_count
        }

    def import_from_csv(self, filepath: str) -> List[ReceivedCANMessage]:
        """
        CSV dosyasından mesajları import et

        Args:
            filepath: CSV dosya yolu

        Returns:
            Import edilen mesajlar
        """
        messages = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)

                # Header'ı atla
                next(reader)

                # Mesajları oku
                for row in reader:
                    if len(row) < 5:
                        continue

                    # Timestamp parse
                    try:
                        dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
                        timestamp = dt.timestamp()
                    except:
                        timestamp = 0.0

                    # CAN ID parse
                    can_id_str = row[1].replace('0x', '').replace('0X', '')
                    can_id = int(can_id_str, 16)

                    # DLC parse
                    dlc = int(row[2])

                    # Data parse
                    data_str = row[3].replace(' ', '')
                    data = bytes.fromhex(data_str)

                    # Direction
                    direction = row[4].strip()

                    # Mesaj oluştur
                    msg = ReceivedCANMessage(
                        can_id=can_id,
                        data=data,
                        dlc=dlc,
                        timestamp=timestamp,
                        direction=direction
                    )
                    messages.append(msg)

            self.logger.info(f"CSV import başarılı: {filepath} ({len(messages)} mesaj)")
            return messages

        except Exception as e:
            self.logger.error(f"CSV import hatası: {e}")
            return []


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print("CAN Logger Test Modu")
    print("=" * 50)

    import time
    from can_message_manager import ReceivedCANMessage

    # Logger oluştur
    logger = CANLogger(log_directory="test_logs")

    # Loglama başlat
    log_file = logger.start_logging("TEST_SESSION")
    print(f"\nLog dosyası: {log_file}")

    # Test mesajları ekle
    for i in range(10):
        msg = ReceivedCANMessage(
            can_id=0x100 + i,
            data=bytes([i, i+1, i+2, i+3]),
            dlc=4,
            timestamp=time.time(),
            direction="RX" if i % 2 == 0 else "TX"
        )
        logger.log_message(msg)
        time.sleep(0.1)

    # İstatistikler
    stats = logger.get_statistics()
    print(f"\nİstatistikler: {stats}")

    # Loglama durdur ve kaydet
    logger.stop_logging()

    # TXT export
    txt_file = log_file.replace('.csv', '.txt')
    logger.export_to_txt(txt_file)

    print(f"\nExport edilen dosyalar:")
    print(f"  - CSV: {log_file}")
    print(f"  - TXT: {txt_file}")

    print("\n✓ Test tamamlandı!")
