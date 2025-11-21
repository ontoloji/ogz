"""
CAN Log Dosyası Okuyucu
ASC ve BLF formatları desteği
Windows dosya yolları uyumlu
"""
import can
from pathlib import Path
from typing import List, Dict, Optional, Generator
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LogReader:
    """
    CAN log dosyalarını okur (ASC, BLF formatları).
    Windows dosya yolları ile uyumludur.
    """

    SUPPORTED_FORMATS = ['.asc', '.blf', '.log', '.txt']

    def __init__(self):
        """Log Reader'ı başlat."""
        self.current_file: Optional[Path] = None
        self.messages: List[Dict] = []
        self.file_format: Optional[str] = None

    def load_file(self, file_path: str, max_messages: Optional[int] = None) -> bool:
        """
        Log dosyasını yükle.

        Args:
            file_path: Log dosya yolu (Windows: C:\\logs\\candata.asc)
            max_messages: Maksimum okunacak mesaj sayısı (None = tümü)

        Returns:
            bool: Yükleme başarılı ise True

        Raises:
            Exception: Dosya okuma hatası
        """
        try:
            # Windows yolunu normalize et
            log_path = Path(file_path)

            if not log_path.exists():
                raise FileNotFoundError(f"Log dosyası bulunamadı: {file_path}")

            file_ext = log_path.suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Desteklenmeyen dosya formatı: {file_ext}\n"
                    f"Desteklenen formatlar: {', '.join(self.SUPPORTED_FORMATS)}"
                )

            self.current_file = log_path
            self.file_format = file_ext
            self.messages.clear()

            logger.info(f"Log dosyası yükleniyor: {file_path}")

            # Dosya formatına göre okuyucu seç
            if file_ext == '.asc':
                self._load_asc_file(log_path, max_messages)
            elif file_ext == '.blf':
                self._load_blf_file(log_path, max_messages)
            else:
                # Genel text-based log deneme
                self._load_generic_log(log_path, max_messages)

            logger.info(f"Toplam {len(self.messages)} mesaj yüklendi")
            return True

        except Exception as e:
            error_msg = f"Log dosyası yükleme hatası: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _load_asc_file(self, file_path: Path, max_messages: Optional[int]):
        """
        ASC formatındaki log dosyasını oku.

        Args:
            file_path: Dosya yolu
            max_messages: Maksimum mesaj sayısı
        """
        try:
            # python-can ile ASC okuma
            with can.ASCReader(str(file_path)) as reader:
                for i, msg in enumerate(reader):
                    if max_messages and i >= max_messages:
                        break

                    msg_dict = self._message_to_dict(msg)
                    self.messages.append(msg_dict)

        except Exception as e:
            logger.error(f"ASC okuma hatası: {str(e)}")
            raise

    def _load_blf_file(self, file_path: Path, max_messages: Optional[int]):
        """
        BLF formatındaki log dosyasını oku.

        Args:
            file_path: Dosya yolu
            max_messages: Maksimum mesaj sayısı
        """
        try:
            # python-can ile BLF okuma
            with can.BLFReader(str(file_path)) as reader:
                for i, msg in enumerate(reader):
                    if max_messages and i >= max_messages:
                        break

                    msg_dict = self._message_to_dict(msg)
                    self.messages.append(msg_dict)

        except Exception as e:
            logger.error(f"BLF okuma hatası: {str(e)}")
            raise

    def _load_generic_log(self, file_path: Path, max_messages: Optional[int]):
        """
        Genel text-based log dosyasını oku.

        Args:
            file_path: Dosya yolu
            max_messages: Maksimum mesaj sayısı
        """
        try:
            # Basit text log okuma
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if max_messages and i >= max_messages:
                        break

                    # Satırı parse etmeye çalış
                    msg_dict = self._parse_log_line(line)
                    if msg_dict:
                        self.messages.append(msg_dict)

        except UnicodeDecodeError:
            # UTF-8 okuma başarısız, binary deneme
            logger.warning("UTF-8 decode hatası, binary okuma deneniyor...")
            raise ValueError("Generic log okuma başarısız. ASC veya BLF formatı kullanın.")

    def _parse_log_line(self, line: str) -> Optional[Dict]:
        """
        Log satırını parse et (basit format).

        Format örneği: "timestamp ID data"
        1234.567 0x123 01 02 03 04 05 06 07 08

        Args:
            line: Log satırı

        Returns:
            Dict: Mesaj bilgileri veya None
        """
        try:
            line = line.strip()
            if not line or line.startswith('#'):
                return None

            parts = line.split()
            if len(parts) < 3:
                return None

            # Timestamp parse
            timestamp = float(parts[0])

            # CAN ID parse
            can_id_str = parts[1]
            if can_id_str.startswith('0x') or can_id_str.startswith('0X'):
                can_id = int(can_id_str, 16)
            else:
                can_id = int(can_id_str)

            # Data parse
            data_bytes = bytes([int(b, 16) for b in parts[2:]])

            return {
                'timestamp': timestamp,
                'datetime': datetime.fromtimestamp(timestamp),
                'arbitration_id': can_id,
                'data': data_bytes,
                'dlc': len(data_bytes),
                'is_extended_id': False,
                'is_error_frame': False,
                'channel': None
            }

        except Exception:
            return None

    def _message_to_dict(self, msg: can.Message) -> Dict:
        """
        python-can Message'ı dict'e dönüştür.

        Args:
            msg: can.Message objesi

        Returns:
            Dict: Mesaj bilgileri
        """
        return {
            'timestamp': msg.timestamp,
            'datetime': datetime.fromtimestamp(msg.timestamp),
            'arbitration_id': msg.arbitration_id,
            'is_extended_id': msg.is_extended_id,
            'is_error_frame': msg.is_error_frame,
            'dlc': msg.dlc,
            'data': bytes(msg.data),
            'channel': getattr(msg, 'channel', None)
        }

    def get_messages(self, start_index: int = 0, count: Optional[int] = None) -> List[Dict]:
        """
        Yüklenmiş mesajları getir.

        Args:
            start_index: Başlangıç indeksi
            count: Getirilecek mesaj sayısı (None = tümü)

        Returns:
            List[Dict]: Mesaj listesi
        """
        if count is None:
            return self.messages[start_index:]
        else:
            return self.messages[start_index:start_index + count]

    def filter_by_id(self, can_ids: List[int]) -> List[Dict]:
        """
        Belirli CAN ID'lere göre filtrele.

        Args:
            can_ids: Filtrelenecek CAN ID listesi

        Returns:
            List[Dict]: Filtrelenmiş mesaj listesi
        """
        return [msg for msg in self.messages if msg['arbitration_id'] in can_ids]

    def filter_by_time_range(self, start_time: float, end_time: float) -> List[Dict]:
        """
        Zaman aralığına göre filtrele.

        Args:
            start_time: Başlangıç timestamp
            end_time: Bitiş timestamp

        Returns:
            List[Dict]: Filtrelenmiş mesaj listesi
        """
        return [msg for msg in self.messages
                if start_time <= msg['timestamp'] <= end_time]

    def get_unique_ids(self) -> List[int]:
        """
        Log dosyasındaki tüm unique CAN ID'leri getir.

        Returns:
            List[int]: Unique CAN ID listesi
        """
        unique_ids = set(msg['arbitration_id'] for msg in self.messages)
        return sorted(list(unique_ids))

    def get_id_statistics(self, can_id: int) -> Dict:
        """
        Belirli bir CAN ID için istatistikler.

        Args:
            can_id: CAN ID

        Returns:
            Dict: İstatistik bilgileri
        """
        id_messages = [msg for msg in self.messages if msg['arbitration_id'] == can_id]

        if not id_messages:
            return {'count': 0}

        timestamps = [msg['timestamp'] for msg in id_messages]
        intervals = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]

        return {
            'count': len(id_messages),
            'first_timestamp': timestamps[0],
            'last_timestamp': timestamps[-1],
            'duration': timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
            'avg_interval': sum(intervals) / len(intervals) if intervals else 0,
            'min_interval': min(intervals) if intervals else 0,
            'max_interval': max(intervals) if intervals else 0
        }

    def get_file_info(self) -> Dict:
        """
        Yüklü log dosyası hakkında bilgi.

        Returns:
            Dict: Dosya bilgileri
        """
        if not self.current_file:
            return {
                'file_loaded': False,
                'file_path': None,
                'message_count': 0
            }

        timestamps = [msg['timestamp'] for msg in self.messages] if self.messages else []

        return {
            'file_loaded': True,
            'file_path': str(self.current_file),
            'file_name': self.current_file.name,
            'file_format': self.file_format,
            'message_count': len(self.messages),
            'unique_ids': len(self.get_unique_ids()),
            'first_timestamp': timestamps[0] if timestamps else None,
            'last_timestamp': timestamps[-1] if timestamps else None,
            'duration': timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
            'file_size_mb': self.current_file.stat().st_size / (1024 * 1024)
        }

    def export_to_csv(self, output_path: str, include_decoded: bool = False,
                     dbc_parser=None) -> bool:
        """
        Mesajları CSV formatında export et.

        Args:
            output_path: Çıktı dosya yolu
            include_decoded: DBC decode bilgilerini dahil et
            dbc_parser: DBCParser instance (decode için gerekli)

        Returns:
            bool: Export başarılı ise True
        """
        try:
            import csv

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if include_decoded and dbc_parser and dbc_parser.is_loaded:
                    # Decode edilmiş veriler dahil
                    fieldnames = ['timestamp', 'datetime', 'can_id', 'dlc',
                                'data_hex', 'message_name', 'decoded_signals']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for msg in self.messages:
                        decoded = dbc_parser.decode_message(
                            msg['arbitration_id'],
                            msg['data']
                        )

                        row = {
                            'timestamp': msg['timestamp'],
                            'datetime': msg['datetime'].isoformat(),
                            'can_id': f"0x{msg['arbitration_id']:X}",
                            'dlc': msg['dlc'],
                            'data_hex': msg['data'].hex().upper(),
                            'message_name': decoded['message_name'] if decoded else 'Unknown',
                            'decoded_signals': str(decoded['signals']) if decoded else ''
                        }
                        writer.writerow(row)
                else:
                    # Sadece raw veriler
                    fieldnames = ['timestamp', 'datetime', 'can_id', 'dlc', 'data_hex']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for msg in self.messages:
                        row = {
                            'timestamp': msg['timestamp'],
                            'datetime': msg['datetime'].isoformat(),
                            'can_id': f"0x{msg['arbitration_id']:X}",
                            'dlc': msg['dlc'],
                            'data_hex': msg['data'].hex().upper()
                        }
                        writer.writerow(row)

            logger.info(f"CSV export tamamlandı: {output_path}")
            return True

        except Exception as e:
            logger.error(f"CSV export hatası: {str(e)}")
            return False

    def clear(self):
        """Yüklü mesajları temizle."""
        self.messages.clear()
        self.current_file = None
        self.file_format = None
        logger.info("Log mesajları temizlendi")

    def iterate_messages(self, batch_size: int = 1000) -> Generator[List[Dict], None, None]:
        """
        Mesajları batch'ler halinde iterate et (büyük dosyalar için).

        Args:
            batch_size: Her batch'teki mesaj sayısı

        Yields:
            List[Dict]: Mesaj batch'i
        """
        for i in range(0, len(self.messages), batch_size):
            yield self.messages[i:i + batch_size]
