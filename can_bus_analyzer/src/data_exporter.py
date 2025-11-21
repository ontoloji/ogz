"""
Veri Export Modülü
CAN mesajlarını ve sinyalleri CSV, Excel formatlarında export eder.
"""

import csv
import pandas as pd
from typing import List, Dict, Optional, Any
import os
import logging
from datetime import datetime

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataExporter:
    """
    CAN verilerini farklı formatlarda export etme sınıfı.
    CSV ve Excel formatlarını destekler.
    """

    def __init__(self):
        """Data exporter başlatıcı."""
        pass

    def export_messages_to_csv(self, messages: List[Dict], output_file: str,
                               include_decoded: bool = False) -> bool:
        """
        CAN mesajlarını CSV formatında export et.

        Args:
            messages: Export edilecek mesajlar
            output_file: Çıktı dosya yolu
            include_decoded: Decode edilmiş verileri de dahil et

        Returns:
            bool: Başarılı ise True
        """
        if not messages:
            logger.warning("Export edilecek mesaj yok")
            return False

        try:
            output_file = os.path.normpath(output_file)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                # CSV header
                fieldnames = ['Timestamp', 'DateTime', 'CAN_ID', 'CAN_ID_Hex',
                             'DLC', 'Data_Hex', 'Data_Dec']

                if include_decoded and 'decoded' in messages[0]:
                    fieldnames.extend(['Message_Name', 'Signals'])

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                # Mesajları yaz
                for msg in messages:
                    row = {
                        'Timestamp': f"{msg['timestamp']:.6f}",
                        'DateTime': msg['datetime'].strftime('%Y-%m-%d %H:%M:%S.%f'),
                        'CAN_ID': msg['arbitration_id'],
                        'CAN_ID_Hex': f"0x{msg['arbitration_id']:X}",
                        'DLC': msg['dlc'],
                        'Data_Hex': ' '.join(f"{b:02X}" for b in msg['data']),
                        'Data_Dec': ' '.join(str(b) for b in msg['data'])
                    }

                    if include_decoded and 'decoded' in msg and msg['decoded']:
                        row['Message_Name'] = msg['decoded'].get('message_name', '')
                        signals = msg['decoded'].get('signals', {})
                        row['Signals'] = str(signals)

                    writer.writerow(row)

            logger.info(f"CSV dosyası oluşturuldu: {output_file} ({len(messages)} mesaj)")
            return True

        except Exception as e:
            logger.error(f"CSV export hatası: {e}")
            return False

    def export_messages_to_excel(self, messages: List[Dict], output_file: str,
                                 include_decoded: bool = False) -> bool:
        """
        CAN mesajlarını Excel formatında export et.

        Args:
            messages: Export edilecek mesajlar
            output_file: Çıktı dosya yolu (.xlsx)
            include_decoded: Decode edilmiş verileri de dahil et

        Returns:
            bool: Başarılı ise True
        """
        if not messages:
            logger.warning("Export edilecek mesaj yok")
            return False

        try:
            output_file = os.path.normpath(output_file)

            # DataFrame oluştur
            data = []
            for msg in messages:
                row = {
                    'Timestamp': msg['timestamp'],
                    'DateTime': msg['datetime'],
                    'CAN_ID': msg['arbitration_id'],
                    'CAN_ID_Hex': f"0x{msg['arbitration_id']:X}",
                    'DLC': msg['dlc'],
                    'Data_Hex': ' '.join(f"{b:02X}" for b in msg['data']),
                    'Data_Dec': ' '.join(str(b) for b in msg['data'])
                }

                if include_decoded and 'decoded' in msg and msg['decoded']:
                    row['Message_Name'] = msg['decoded'].get('message_name', '')

                    # Sinyalleri ayrı kolonlara ekle
                    signals = msg['decoded'].get('signals', {})
                    for signal_name, signal_value in signals.items():
                        row[f'Signal_{signal_name}'] = signal_value

                data.append(row)

            df = pd.DataFrame(data)

            # Excel'e yaz
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='CAN_Messages', index=False)

                # Worksheet'i formatla
                worksheet = writer.sheets['CAN_Messages']

                # Kolon genişliklerini ayarla
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            logger.info(f"Excel dosyası oluşturuldu: {output_file} ({len(messages)} mesaj)")
            return True

        except Exception as e:
            logger.error(f"Excel export hatası: {e}")
            return False

    def export_signals_to_csv(self, signal_data: Dict[str, List[Any]],
                             output_file: str) -> bool:
        """
        Sinyal verilerini CSV formatında export et.

        Args:
            signal_data: Sinyal adı -> değer listesi mapping
            output_file: Çıktı dosya yolu

        Returns:
            bool: Başarılı ise True
        """
        if not signal_data:
            logger.warning("Export edilecek sinyal verisi yok")
            return False

        try:
            output_file = os.path.normpath(output_file)

            # DataFrame oluştur
            df = pd.DataFrame(signal_data)

            # CSV'ye yaz
            df.to_csv(output_file, index=False, encoding='utf-8')

            logger.info(f"Sinyal CSV dosyası oluşturuldu: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Sinyal CSV export hatası: {e}")
            return False

    def export_signals_to_excel(self, signal_data: Dict[str, List[Any]],
                               output_file: str, sheet_name: str = 'Signals') -> bool:
        """
        Sinyal verilerini Excel formatında export et.

        Args:
            signal_data: Sinyal adı -> değer listesi mapping
            output_file: Çıktı dosya yolu
            sheet_name: Worksheet adı

        Returns:
            bool: Başarılı ise True
        """
        if not signal_data:
            logger.warning("Export edilecek sinyal verisi yok")
            return False

        try:
            output_file = os.path.normpath(output_file)

            # DataFrame oluştur
            df = pd.DataFrame(signal_data)

            # Excel'e yaz
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Worksheet'i formatla
                worksheet = writer.sheets[sheet_name]

                # Kolon genişliklerini ayarla
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            logger.info(f"Sinyal Excel dosyası oluşturuldu: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Sinyal Excel export hatası: {e}")
            return False

    def export_statistics_to_excel(self, statistics: Dict, output_file: str) -> bool:
        """
        İstatistik verilerini Excel formatında export et.

        Args:
            statistics: İstatistik verileri
            output_file: Çıktı dosya yolu

        Returns:
            bool: Başarılı ise True
        """
        try:
            output_file = os.path.normpath(output_file)

            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Genel istatistikler
                general_stats = {
                    'Metric': [],
                    'Value': []
                }

                for key, value in statistics.items():
                    if key != 'id_message_counts':
                        general_stats['Metric'].append(key)
                        general_stats['Value'].append(str(value))

                df_general = pd.DataFrame(general_stats)
                df_general.to_excel(writer, sheet_name='General_Statistics', index=False)

                # CAN ID bazında mesaj sayıları
                if 'id_message_counts' in statistics:
                    id_counts = {
                        'CAN_ID': [],
                        'Message_Count': []
                    }
                    for can_id, count in statistics['id_message_counts'].items():
                        id_counts['CAN_ID'].append(can_id)
                        id_counts['Message_Count'].append(count)

                    df_counts = pd.DataFrame(id_counts)
                    df_counts.to_excel(writer, sheet_name='Message_Counts', index=False)

            logger.info(f"İstatistik Excel dosyası oluşturuldu: {output_file}")
            return True

        except Exception as e:
            logger.error(f"İstatistik export hatası: {e}")
            return False

    def create_analysis_report(self, messages: List[Dict], statistics: Dict,
                              output_file: str, dbc_info: Optional[Dict] = None) -> bool:
        """
        Kapsamlı analiz raporu oluştur (Excel).

        Args:
            messages: CAN mesajları
            statistics: İstatistikler
            output_file: Çıktı dosya yolu
            dbc_info: DBC bilgileri (opsiyonel)

        Returns:
            bool: Başarılı ise True
        """
        try:
            output_file = os.path.normpath(output_file)

            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 1. Özet sayfa
                summary_data = {
                    'Parameter': ['Report Date', 'Total Messages', 'Unique CAN IDs',
                                 'Duration (s)', 'Messages/Second', 'Start Time', 'End Time'],
                    'Value': [
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        statistics.get('total_messages', 0),
                        statistics.get('unique_can_ids', 0),
                        f"{statistics.get('duration', 0):.2f}",
                        f"{statistics.get('messages_per_second', 0):.2f}",
                        statistics.get('start_time', 'N/A'),
                        statistics.get('end_time', 'N/A')
                    ]
                }

                if dbc_info:
                    summary_data['Parameter'].extend(['DBC File', 'DBC Messages', 'DBC Signals'])
                    summary_data['Value'].extend([
                        dbc_info.get('file_path', 'N/A'),
                        dbc_info.get('message_count', 0),
                        dbc_info.get('signal_count', 0)
                    ])

                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)

                # 2. Mesaj sayıları
                if 'id_message_counts' in statistics:
                    id_counts = []
                    for can_id, count in sorted(statistics['id_message_counts'].items()):
                        id_counts.append({
                            'CAN_ID': can_id,
                            'Message_Count': count,
                            'Percentage': f"{(count / statistics['total_messages'] * 100):.2f}%"
                        })

                    df_counts = pd.DataFrame(id_counts)
                    df_counts.to_excel(writer, sheet_name='Message_Distribution', index=False)

                # 3. İlk N mesaj (örnek olarak)
                if messages:
                    sample_messages = messages[:100]  # İlk 100 mesaj
                    msg_data = []

                    for msg in sample_messages:
                        msg_data.append({
                            'Timestamp': msg['timestamp'],
                            'DateTime': msg['datetime'],
                            'CAN_ID': f"0x{msg['arbitration_id']:X}",
                            'DLC': msg['dlc'],
                            'Data': ' '.join(f"{b:02X}" for b in msg['data'])
                        })

                    df_messages = pd.DataFrame(msg_data)
                    df_messages.to_excel(writer, sheet_name='Sample_Messages', index=False)

            logger.info(f"Analiz raporu oluşturuldu: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Rapor oluşturma hatası: {e}")
            return False

    @staticmethod
    def prepare_signal_dataframe(messages: List[Dict], signal_names: List[str]) -> pd.DataFrame:
        """
        Sinyal verilerini DataFrame olarak hazırla.

        Args:
            messages: Decode edilmiş mesajlar
            signal_names: İlgilenilen sinyal isimleri

        Returns:
            pd.DataFrame: Sinyal verileri
        """
        data = {
            'Timestamp': [],
            'DateTime': []
        }

        # Sinyal kolonlarını başlat
        for signal_name in signal_names:
            data[signal_name] = []

        # Verileri doldur
        for msg in messages:
            if 'decoded' in msg and msg['decoded']:
                signals = msg['decoded'].get('signals', {})

                data['Timestamp'].append(msg['timestamp'])
                data['DateTime'].append(msg['datetime'])

                for signal_name in signal_names:
                    value = signals.get(signal_name, None)
                    data[signal_name].append(value)

        return pd.DataFrame(data)


if __name__ == "__main__":
    # Test kodu
    print("Data Exporter Modülü Test Ediliyor...")

    exporter = DataExporter()

    # Örnek mesajlar
    example_messages = [
        {
            'timestamp': 1234567890.123456,
            'datetime': datetime.now(),
            'arbitration_id': 0x123,
            'dlc': 8,
            'data': [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        }
    ]

    # Test CSV export
    # exporter.export_messages_to_csv(example_messages, "test_output.csv")

    print("Test tamamlandı")
