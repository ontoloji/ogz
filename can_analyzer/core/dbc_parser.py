"""
DBC Parser ve Sinyal Decoder Module
Windows dosya yolları ile uyumlu
"""
import cantools
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DBCParser:
    """
    DBC dosyalarını yükler ve CAN sinyallerini decode eder.
    Windows dosya yolları ile uyumludur.
    """

    def __init__(self):
        """DBC Parser'ı başlat."""
        self.database: Optional[cantools.database.Database] = None
        self.dbc_file_path: Optional[Path] = None
        self.is_loaded = False

    def load_dbc(self, file_path: str) -> bool:
        """
        DBC dosyasını yükle.

        Args:
            file_path: DBC dosya yolu (Windows yolu desteklenir: C:\\path\\to\\file.dbc)

        Returns:
            bool: Yükleme başarılı ise True

        Raises:
            Exception: DBC yükleme hatası
        """
        try:
            # Windows yolunu normalize et
            dbc_path = Path(file_path)

            if not dbc_path.exists():
                raise FileNotFoundError(f"DBC dosyası bulunamadı: {file_path}")

            if not dbc_path.suffix.lower() == '.dbc':
                raise ValueError("Dosya uzantısı .dbc olmalıdır")

            # DBC dosyasını yükle
            self.database = cantools.database.load_file(str(dbc_path))
            self.dbc_file_path = dbc_path
            self.is_loaded = True

            logger.info(f"DBC dosyası yüklendi: {file_path}")
            logger.info(f"Mesaj sayısı: {len(self.database.messages)}")

            return True

        except Exception as e:
            error_msg = f"DBC yükleme hatası: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def unload_dbc(self):
        """DBC dosyasını kaldır."""
        self.database = None
        self.dbc_file_path = None
        self.is_loaded = False
        logger.info("DBC dosyası kaldırıldı")

    def decode_message(self, can_id: int, data: bytes) -> Optional[Dict[str, Any]]:
        """
        CAN mesajını decode et.

        Args:
            can_id: CAN mesaj ID'si
            data: CAN verisi (bytes)

        Returns:
            Dict: Decode edilmiş sinyal değerleri
                  {
                      'message_name': 'EngineSpeed',
                      'signals': {'RPM': 1500, 'Temperature': 85},
                      'raw_data': b'\\x01\\x02...'
                  }
            None: Mesaj DBC'de bulunamazsa

        Raises:
            Exception: Decode hatası
        """
        try:
            if not self.is_loaded:
                raise Exception("DBC dosyası yüklü değil")

            # Mesajı DBC'den bul
            message = self.database.get_message_by_frame_id(can_id)

            if not message:
                logger.warning(f"ID 0x{can_id:X} için DBC'de mesaj tanımı bulunamadı")
                return None

            # Mesajı decode et
            decoded_data = message.decode(data)

            result = {
                'message_name': message.name,
                'message_id': can_id,
                'signals': decoded_data,
                'raw_data': data,
                'dlc': len(data)
            }

            return result

        except Exception as e:
            logger.error(f"Decode hatası (ID: 0x{can_id:X}): {str(e)}")
            return None

    def get_message_info(self, can_id: int) -> Optional[Dict]:
        """
        Belirli bir CAN ID için mesaj bilgilerini getir.

        Args:
            can_id: CAN mesaj ID'si

        Returns:
            Dict: Mesaj bilgileri (name, signals, comment, vb.)
            None: Mesaj bulunamazsa
        """
        try:
            if not self.is_loaded:
                raise Exception("DBC dosyası yüklü değil")

            message = self.database.get_message_by_frame_id(can_id)

            if not message:
                return None

            signals_info = []
            for signal in message.signals:
                signals_info.append({
                    'name': signal.name,
                    'start_bit': signal.start,
                    'length': signal.length,
                    'byte_order': signal.byte_order,
                    'is_signed': signal.is_signed,
                    'scale': signal.scale,
                    'offset': signal.offset,
                    'minimum': signal.minimum,
                    'maximum': signal.maximum,
                    'unit': signal.unit,
                    'comment': signal.comment,
                    'choices': signal.choices
                })

            return {
                'name': message.name,
                'frame_id': message.frame_id,
                'length': message.length,
                'comment': message.comment,
                'signals': signals_info,
                'cycle_time': message.cycle_time,
                'senders': message.senders
            }

        except Exception as e:
            logger.error(f"Mesaj bilgisi alma hatası: {str(e)}")
            return None

    def get_all_messages(self) -> List[Dict]:
        """
        DBC'deki tüm mesaj bilgilerini listele.

        Returns:
            List[Dict]: Mesaj bilgileri listesi
        """
        if not self.is_loaded:
            logger.warning("DBC dosyası yüklü değil")
            return []

        messages = []
        for message in self.database.messages:
            messages.append({
                'name': message.name,
                'frame_id': message.frame_id,
                'length': message.length,
                'signal_count': len(message.signals),
                'comment': message.comment
            })

        return messages

    def get_all_signals(self) -> List[Dict]:
        """
        DBC'deki tüm sinyal bilgilerini listele.

        Returns:
            List[Dict]: Sinyal bilgileri listesi
        """
        if not self.is_loaded:
            logger.warning("DBC dosyası yüklü değil")
            return []

        signals = []
        for message in self.database.messages:
            for signal in message.signals:
                signals.append({
                    'message_name': message.name,
                    'message_id': message.frame_id,
                    'signal_name': signal.name,
                    'unit': signal.unit,
                    'minimum': signal.minimum,
                    'maximum': signal.maximum,
                    'comment': signal.comment
                })

        return signals

    def search_signal(self, signal_name: str) -> List[Dict]:
        """
        İsme göre sinyal ara.

        Args:
            signal_name: Aranacak sinyal ismi (kısmi eşleşme desteklenir)

        Returns:
            List[Dict]: Bulunan sinyal bilgileri
        """
        if not self.is_loaded:
            logger.warning("DBC dosyası yüklü değil")
            return []

        results = []
        search_lower = signal_name.lower()

        for message in self.database.messages:
            for signal in message.signals:
                if search_lower in signal.name.lower():
                    results.append({
                        'message_name': message.name,
                        'message_id': message.frame_id,
                        'signal_name': signal.name,
                        'unit': signal.unit,
                        'minimum': signal.minimum,
                        'maximum': signal.maximum,
                        'comment': signal.comment
                    })

        return results

    def get_signal_value_description(self, can_id: int, signal_name: str,
                                     value: float) -> Optional[str]:
        """
        Sinyal değeri için açıklama getir (enum değerleri için).

        Args:
            can_id: CAN mesaj ID'si
            signal_name: Sinyal ismi
            value: Sinyal değeri

        Returns:
            str: Değer açıklaması (varsa)
            None: Açıklama yoksa
        """
        try:
            if not self.is_loaded:
                return None

            message = self.database.get_message_by_frame_id(can_id)
            if not message:
                return None

            signal = message.get_signal_by_name(signal_name)
            if not signal or not signal.choices:
                return None

            # Enum değeri bul
            int_value = int(value)
            return signal.choices.get(int_value)

        except Exception as e:
            logger.error(f"Değer açıklaması alma hatası: {str(e)}")
            return None

    def encode_message(self, message_name: str, signals: Dict[str, Any]) -> Optional[bytes]:
        """
        Sinyal değerlerinden CAN mesajı oluştur.

        Args:
            message_name: Mesaj ismi
            signals: Sinyal değerleri dict'i {'signal_name': value}

        Returns:
            bytes: Encode edilmiş CAN verisi
            None: Hata durumunda
        """
        try:
            if not self.is_loaded:
                raise Exception("DBC dosyası yüklü değil")

            message = self.database.get_message_by_name(message_name)
            if not message:
                raise ValueError(f"Mesaj bulunamadı: {message_name}")

            # Mesajı encode et
            data = message.encode(signals)
            return data

        except Exception as e:
            logger.error(f"Encode hatası: {str(e)}")
            return None

    def get_dbc_info(self) -> Dict:
        """
        Yüklü DBC dosyası hakkında genel bilgi.

        Returns:
            Dict: DBC bilgileri
        """
        if not self.is_loaded:
            return {
                'is_loaded': False,
                'file_path': None,
                'message_count': 0,
                'signal_count': 0
            }

        total_signals = sum(len(msg.signals) for msg in self.database.messages)

        return {
            'is_loaded': True,
            'file_path': str(self.dbc_file_path),
            'message_count': len(self.database.messages),
            'signal_count': total_signals,
            'version': getattr(self.database, 'version', 'N/A'),
            'dbc_name': self.dbc_file_path.name if self.dbc_file_path else None
        }

    def validate_message_data(self, can_id: int, data: bytes) -> Dict:
        """
        CAN mesaj verisinin geçerliliğini kontrol et.

        Args:
            can_id: CAN mesaj ID'si
            data: CAN verisi

        Returns:
            Dict: Validasyon sonucu
                {
                    'is_valid': bool,
                    'errors': List[str],
                    'warnings': List[str]
                }
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        try:
            if not self.is_loaded:
                result['is_valid'] = False
                result['errors'].append("DBC dosyası yüklü değil")
                return result

            message = self.database.get_message_by_frame_id(can_id)

            if not message:
                result['warnings'].append(f"ID 0x{can_id:X} DBC'de tanımlı değil")
                return result

            # DLC kontrolü
            if len(data) != message.length:
                result['warnings'].append(
                    f"DLC uyuşmazlığı: Beklenen={message.length}, Alınan={len(data)}"
                )

            # Decode deneme
            try:
                decoded = message.decode(data)

                # Sinyal aralık kontrolü
                for signal in message.signals:
                    if signal.name in decoded:
                        value = decoded[signal.name]

                        if signal.minimum is not None and value < signal.minimum:
                            result['warnings'].append(
                                f"{signal.name}: Değer minimum değerin altında ({value} < {signal.minimum})"
                            )

                        if signal.maximum is not None and value > signal.maximum:
                            result['warnings'].append(
                                f"{signal.name}: Değer maksimum değerin üstünde ({value} > {signal.maximum})"
                            )

            except Exception as e:
                result['is_valid'] = False
                result['errors'].append(f"Decode hatası: {str(e)}")

        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(str(e))

        return result
