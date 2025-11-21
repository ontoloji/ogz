"""
DBC Parser Modülü
DBC dosyalarını yükler ve CAN mesajlarını decode eder.
"""

import cantools
from typing import Optional, Dict, List, Any
import logging
import os

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBCParser:
    """
    DBC dosya parser sınıfı.
    CAN mesajlarını decode etmek için DBC veritabanı yönetir.
    """

    def __init__(self):
        """DBC parser başlatıcı."""
        self.database: Optional[cantools.database.Database] = None
        self.dbc_file_path: Optional[str] = None
        self.is_loaded = False

    def load_dbc(self, file_path: str) -> bool:
        """
        DBC dosyasını yükle.

        Args:
            file_path: DBC dosya yolu (Windows path desteği)

        Returns:
            bool: Yükleme başarılı ise True
        """
        try:
            # Windows dosya yolunu normalize et
            file_path = os.path.normpath(file_path)

            if not os.path.exists(file_path):
                logger.error(f"DBC dosyası bulunamadı: {file_path}")
                return False

            # DBC dosyasını yükle
            self.database = cantools.database.load_file(file_path)
            self.dbc_file_path = file_path
            self.is_loaded = True

            logger.info(f"DBC dosyası yüklendi: {file_path}")
            logger.info(f"Toplam mesaj sayısı: {len(self.database.messages)}")

            return True

        except Exception as e:
            logger.error(f"DBC yükleme hatası: {e}")
            self.is_loaded = False
            return False

    def decode_message(self, can_id: int, data: bytes) -> Optional[Dict[str, Any]]:
        """
        CAN mesajını decode et.

        Args:
            can_id: CAN mesaj ID'si
            data: CAN mesaj verisi (bytes)

        Returns:
            Dict: Decode edilmiş sinyal değerleri veya None
        """
        if not self.is_loaded or not self.database:
            logger.error("DBC dosyası yüklenmemiş!")
            return None

        try:
            # Mesajı bul
            message = self.database.get_message_by_frame_id(can_id)

            # Mesajı decode et
            decoded_data = message.decode(data)

            return {
                'message_name': message.name,
                'message_id': hex(can_id),
                'signals': decoded_data,
                'comment': message.comment or ""
            }

        except KeyError:
            # Bu CAN ID için mesaj tanımı yok
            logger.debug(f"DBC'de tanımsız CAN ID: 0x{can_id:X}")
            return None
        except Exception as e:
            logger.error(f"Decode hatası (ID: 0x{can_id:X}): {e}")
            return None

    def get_message_info(self, can_id: int) -> Optional[Dict[str, Any]]:
        """
        CAN ID için mesaj bilgilerini al.

        Args:
            can_id: CAN mesaj ID'si

        Returns:
            Dict: Mesaj bilgileri
        """
        if not self.is_loaded or not self.database:
            return None

        try:
            message = self.database.get_message_by_frame_id(can_id)

            signal_list = []
            for signal in message.signals:
                signal_info = {
                    'name': signal.name,
                    'start_bit': signal.start,
                    'length': signal.length,
                    'scale': signal.scale,
                    'offset': signal.offset,
                    'minimum': signal.minimum,
                    'maximum': signal.maximum,
                    'unit': signal.unit or "",
                    'comment': signal.comment or ""
                }
                signal_list.append(signal_info)

            return {
                'name': message.name,
                'id': hex(can_id),
                'dlc': message.length,
                'cycle_time': message.cycle_time,
                'comment': message.comment or "",
                'signals': signal_list
            }

        except KeyError:
            return None
        except Exception as e:
            logger.error(f"Mesaj bilgisi alma hatası: {e}")
            return None

    def get_all_messages(self) -> List[Dict[str, Any]]:
        """
        Tüm mesaj listesini al.

        Returns:
            List[Dict]: Mesaj bilgileri listesi
        """
        if not self.is_loaded or not self.database:
            return []

        message_list = []
        for message in self.database.messages:
            msg_info = {
                'name': message.name,
                'id': hex(message.frame_id),
                'id_decimal': message.frame_id,
                'dlc': message.length,
                'cycle_time': message.cycle_time,
                'signal_count': len(message.signals),
                'comment': message.comment or ""
            }
            message_list.append(msg_info)

        return sorted(message_list, key=lambda x: x['id_decimal'])

    def get_signal_list(self, can_id: int) -> List[str]:
        """
        Belirli bir mesajın sinyal isimlerini al.

        Args:
            can_id: CAN mesaj ID'si

        Returns:
            List[str]: Sinyal isimleri
        """
        if not self.is_loaded or not self.database:
            return []

        try:
            message = self.database.get_message_by_frame_id(can_id)
            return [signal.name for signal in message.signals]
        except:
            return []

    def search_signal(self, signal_name: str) -> List[Dict[str, Any]]:
        """
        Sinyal ismini ara.

        Args:
            signal_name: Aranacak sinyal ismi (kısmi eşleşme)

        Returns:
            List[Dict]: Eşleşen sinyaller
        """
        if not self.is_loaded or not self.database:
            return []

        results = []
        signal_name_lower = signal_name.lower()

        for message in self.database.messages:
            for signal in message.signals:
                if signal_name_lower in signal.name.lower():
                    results.append({
                        'message_name': message.name,
                        'message_id': hex(message.frame_id),
                        'signal_name': signal.name,
                        'unit': signal.unit or "",
                        'min': signal.minimum,
                        'max': signal.maximum
                    })

        return results

    def encode_message(self, message_name: str, signal_values: Dict[str, Any]) -> Optional[bytes]:
        """
        Sinyal değerlerini CAN mesajına encode et.

        Args:
            message_name: Mesaj ismi
            signal_values: Sinyal değerleri dict

        Returns:
            bytes: Encode edilmiş data veya None
        """
        if not self.is_loaded or not self.database:
            logger.error("DBC dosyası yüklenmemiş!")
            return None

        try:
            message = self.database.get_message_by_name(message_name)
            encoded_data = message.encode(signal_values)
            return encoded_data

        except KeyError:
            logger.error(f"Mesaj bulunamadı: {message_name}")
            return None
        except Exception as e:
            logger.error(f"Encode hatası: {e}")
            return None

    def get_message_by_name(self, message_name: str) -> Optional[int]:
        """
        Mesaj isminden CAN ID al.

        Args:
            message_name: Mesaj ismi

        Returns:
            int: CAN ID veya None
        """
        if not self.is_loaded or not self.database:
            return None

        try:
            message = self.database.get_message_by_name(message_name)
            return message.frame_id
        except:
            return None

    def get_database_info(self) -> Dict[str, Any]:
        """
        DBC veritabanı hakkında bilgi al.

        Returns:
            Dict: Veritabanı bilgileri
        """
        if not self.is_loaded or not self.database:
            return {
                'loaded': False,
                'file_path': None,
                'message_count': 0,
                'node_count': 0
            }

        total_signals = sum(len(msg.signals) for msg in self.database.messages)

        return {
            'loaded': True,
            'file_path': self.dbc_file_path,
            'message_count': len(self.database.messages),
            'signal_count': total_signals,
            'node_count': len(self.database.nodes),
            'version': self.database.version or "N/A"
        }

    def export_message_list(self, output_file: str) -> bool:
        """
        Mesaj listesini text dosyasına export et.

        Args:
            output_file: Çıktı dosya yolu

        Returns:
            bool: Başarılı ise True
        """
        if not self.is_loaded or not self.database:
            return False

        try:
            output_file = os.path.normpath(output_file)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("DBC Mesaj Listesi\n")
                f.write(f"Dosya: {self.dbc_file_path}\n")
                f.write("=" * 80 + "\n\n")

                for message in sorted(self.database.messages, key=lambda m: m.frame_id):
                    f.write(f"Mesaj: {message.name}\n")
                    f.write(f"  ID: 0x{message.frame_id:X} ({message.frame_id})\n")
                    f.write(f"  DLC: {message.length}\n")
                    f.write(f"  Cycle Time: {message.cycle_time} ms\n")

                    if message.comment:
                        f.write(f"  Açıklama: {message.comment}\n")

                    f.write(f"\n  Sinyaller ({len(message.signals)}):\n")
                    for signal in message.signals:
                        f.write(f"    - {signal.name}")
                        if signal.unit:
                            f.write(f" [{signal.unit}]")
                        f.write(f" (Min: {signal.minimum}, Max: {signal.maximum})")
                        if signal.comment:
                            f.write(f"\n      {signal.comment}")
                        f.write("\n")

                    f.write("\n" + "-" * 80 + "\n\n")

            logger.info(f"Mesaj listesi export edildi: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Export hatası: {e}")
            return False

    def unload(self):
        """DBC dosyasını bellekten kaldır."""
        self.database = None
        self.dbc_file_path = None
        self.is_loaded = False
        logger.info("DBC dosyası bellekten kaldırıldı")


if __name__ == "__main__":
    # Test kodu
    print("DBC Parser Modülü Test Ediliyor...")

    parser = DBCParser()

    # Örnek kullanım
    # parser.load_dbc("example.dbc")
    # if parser.is_loaded:
    #     print(f"DBC bilgileri: {parser.get_database_info()}")
    #     messages = parser.get_all_messages()
    #     print(f"\nToplam {len(messages)} mesaj bulundu")
    #
    #     # Örnek decode
    #     decoded = parser.decode_message(0x123, bytes([0x01, 0x02, 0x03, 0x04]))
    #     if decoded:
    #         print(f"Decode edildi: {decoded}")

    print("Test tamamlandı (gerçek test için DBC dosyası gerekli)")
