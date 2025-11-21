"""
Veri Export Modülü
CSV ve Excel formatları desteği
Windows dosya yolları uyumlu
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataExporter:
    """
    CAN verilerini farklı formatlarda export eder (CSV, Excel).
    Windows dosya yolları ile uyumludur.
    """

    def __init__(self):
        """Data Exporter'ı başlat."""
        pass

    def export_to_csv(self, messages: List[Dict], output_path: str,
                     include_decoded: bool = False, dbc_parser=None) -> bool:
        """
        Mesajları CSV formatında export et.

        Args:
            messages: Mesaj listesi
            output_path: Çıktı dosya yolu (Windows: C:\\exports\\data.csv)
            include_decoded: DBC decode bilgilerini dahil et
            dbc_parser: DBCParser instance (decode için)

        Returns:
            bool: Export başarılı ise True

        Raises:
            Exception: Export hatası
        """
        try:
            if not messages:
                raise ValueError("Export edilecek mesaj yok")

            # Windows yolunu normalize et
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # DataFrame oluştur
            if include_decoded and dbc_parser and dbc_parser.is_loaded:
                df = self._create_decoded_dataframe(messages, dbc_parser)
            else:
                df = self._create_basic_dataframe(messages)

            # CSV'ye yaz
            df.to_csv(output_file, index=False, encoding='utf-8')

            logger.info(f"CSV export tamamlandı: {output_path}")
            logger.info(f"Toplam {len(messages)} mesaj export edildi")
            return True

        except Exception as e:
            error_msg = f"CSV export hatası: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def export_to_excel(self, messages: List[Dict], output_path: str,
                       include_decoded: bool = False, dbc_parser=None,
                       include_statistics: bool = True) -> bool:
        """
        Mesajları Excel formatında export et.

        Args:
            messages: Mesaj listesi
            output_path: Çıktı dosya yolu (Windows: C:\\exports\\data.xlsx)
            include_decoded: DBC decode bilgilerini dahil et
            dbc_parser: DBCParser instance
            include_statistics: İstatistik sayfası ekle

        Returns:
            bool: Export başarılı ise True

        Raises:
            Exception: Export hatası
        """
        try:
            if not messages:
                raise ValueError("Export edilecek mesaj yok")

            # Windows yolunu normalize et
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Excel writer oluştur
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Ana veri sayfası
                if include_decoded and dbc_parser and dbc_parser.is_loaded:
                    df_messages = self._create_decoded_dataframe(messages, dbc_parser)
                else:
                    df_messages = self._create_basic_dataframe(messages)

                df_messages.to_excel(writer, sheet_name='Messages', index=False)

                # İstatistik sayfası
                if include_statistics:
                    df_stats = self._create_statistics_dataframe(messages)
                    df_stats.to_excel(writer, sheet_name='Statistics', index=True)

                # DBC bilgileri sayfası
                if dbc_parser and dbc_parser.is_loaded:
                    df_dbc = self._create_dbc_info_dataframe(dbc_parser)
                    df_dbc.to_excel(writer, sheet_name='DBC Info', index=False)

                # Sütun genişliklerini ayarla
                self._adjust_column_widths(writer)

            logger.info(f"Excel export tamamlandı: {output_path}")
            logger.info(f"Toplam {len(messages)} mesaj export edildi")
            return True

        except Exception as e:
            error_msg = f"Excel export hatası: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def export_signals_to_excel(self, signal_data: Dict[str, List],
                               output_path: str) -> bool:
        """
        Sinyal verilerini Excel'e export et (time-series format).

        Args:
            signal_data: Sinyal verileri
                {
                    'timestamps': [t1, t2, ...],
                    'signal_name_1': [v1, v2, ...],
                    'signal_name_2': [v1, v2, ...]
                }
            output_path: Çıktı dosya yolu

        Returns:
            bool: Export başarılı ise True
        """
        try:
            if not signal_data or 'timestamps' not in signal_data:
                raise ValueError("Geçersiz sinyal verisi")

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # DataFrame oluştur
            df = pd.DataFrame(signal_data)

            # Datetime sütunu ekle
            if 'timestamps' in df.columns:
                df['datetime'] = pd.to_datetime(df['timestamps'], unit='s')
                # Sütun sırasını düzenle
                cols = ['timestamps', 'datetime'] + [col for col in df.columns
                                                     if col not in ['timestamps', 'datetime']]
                df = df[cols]

            # Excel'e yaz
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Signals', index=False)

                # Grafik ekle (ilk birkaç sinyal için)
                workbook = writer.book
                worksheet = writer.sheets['Signals']

                signal_columns = [col for col in df.columns
                                if col not in ['timestamps', 'datetime']][:5]

                if signal_columns:
                    chart = workbook.add_chart({'type': 'line'})

                    for i, signal_name in enumerate(signal_columns):
                        col_idx = df.columns.get_loc(signal_name)
                        chart.add_series({
                            'name': signal_name,
                            'categories': ['Signals', 1, 0, len(df), 0],
                            'values': ['Signals', 1, col_idx, len(df), col_idx],
                        })

                    chart.set_title({'name': 'Signal Values Over Time'})
                    chart.set_x_axis({'name': 'Timestamp'})
                    chart.set_y_axis({'name': 'Value'})
                    chart.set_size({'width': 720, 'height': 400})

                    worksheet.insert_chart('A' + str(len(df) + 3), chart)

            logger.info(f"Sinyal Excel export tamamlandı: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Sinyal Excel export hatası: {str(e)}")
            raise Exception(f"Sinyal Excel export hatası: {str(e)}")

    def _create_basic_dataframe(self, messages: List[Dict]) -> pd.DataFrame:
        """
        Temel mesaj DataFrame'i oluştur.

        Args:
            messages: Mesaj listesi

        Returns:
            pd.DataFrame: Mesaj verileri
        """
        data = {
            'Timestamp': [],
            'DateTime': [],
            'CAN_ID': [],
            'CAN_ID_Hex': [],
            'DLC': [],
            'Data_Hex': [],
            'Data_Dec': []
        }

        for msg in messages:
            data['Timestamp'].append(msg['timestamp'])
            data['DateTime'].append(msg['datetime'])
            data['CAN_ID'].append(msg['arbitration_id'])
            data['CAN_ID_Hex'].append(f"0x{msg['arbitration_id']:X}")
            data['DLC'].append(msg['dlc'])
            data['Data_Hex'].append(msg['data'].hex().upper())
            data['Data_Dec'].append(' '.join([str(b) for b in msg['data']]))

        return pd.DataFrame(data)

    def _create_decoded_dataframe(self, messages: List[Dict], dbc_parser) -> pd.DataFrame:
        """
        Decode edilmiş mesaj DataFrame'i oluştur.

        Args:
            messages: Mesaj listesi
            dbc_parser: DBCParser instance

        Returns:
            pd.DataFrame: Decode edilmiş mesaj verileri
        """
        data = {
            'Timestamp': [],
            'DateTime': [],
            'CAN_ID_Hex': [],
            'Message_Name': [],
            'DLC': [],
            'Data_Hex': [],
            'Decoded_Signals': []
        }

        for msg in messages:
            decoded = dbc_parser.decode_message(msg['arbitration_id'], msg['data'])

            data['Timestamp'].append(msg['timestamp'])
            data['DateTime'].append(msg['datetime'])
            data['CAN_ID_Hex'].append(f"0x{msg['arbitration_id']:X}")
            data['Message_Name'].append(decoded['message_name'] if decoded else 'Unknown')
            data['DLC'].append(msg['dlc'])
            data['Data_Hex'].append(msg['data'].hex().upper())
            data['Decoded_Signals'].append(str(decoded['signals']) if decoded else '')

        return pd.DataFrame(data)

    def _create_statistics_dataframe(self, messages: List[Dict]) -> pd.DataFrame:
        """
        İstatistik DataFrame'i oluştur.

        Args:
            messages: Mesaj listesi

        Returns:
            pd.DataFrame: İstatistik verileri
        """
        # Unique ID'leri bul
        unique_ids = {}
        for msg in messages:
            can_id = msg['arbitration_id']
            if can_id not in unique_ids:
                unique_ids[can_id] = []
            unique_ids[can_id].append(msg['timestamp'])

        # Her ID için istatistik hesapla
        stats_data = {
            'CAN_ID_Hex': [],
            'CAN_ID_Dec': [],
            'Message_Count': [],
            'First_Time': [],
            'Last_Time': [],
            'Duration_s': [],
            'Avg_Interval_ms': [],
            'Min_Interval_ms': [],
            'Max_Interval_ms': []
        }

        for can_id, timestamps in sorted(unique_ids.items()):
            intervals = [timestamps[i + 1] - timestamps[i]
                        for i in range(len(timestamps) - 1)]

            stats_data['CAN_ID_Hex'].append(f"0x{can_id:X}")
            stats_data['CAN_ID_Dec'].append(can_id)
            stats_data['Message_Count'].append(len(timestamps))
            stats_data['First_Time'].append(timestamps[0])
            stats_data['Last_Time'].append(timestamps[-1])
            stats_data['Duration_s'].append(timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0)
            stats_data['Avg_Interval_ms'].append(
                sum(intervals) / len(intervals) * 1000 if intervals else 0
            )
            stats_data['Min_Interval_ms'].append(
                min(intervals) * 1000 if intervals else 0
            )
            stats_data['Max_Interval_ms'].append(
                max(intervals) * 1000 if intervals else 0
            )

        return pd.DataFrame(stats_data)

    def _create_dbc_info_dataframe(self, dbc_parser) -> pd.DataFrame:
        """
        DBC bilgi DataFrame'i oluştur.

        Args:
            dbc_parser: DBCParser instance

        Returns:
            pd.DataFrame: DBC bilgileri
        """
        messages = dbc_parser.get_all_messages()

        data = {
            'Message_Name': [],
            'CAN_ID_Hex': [],
            'CAN_ID_Dec': [],
            'DLC': [],
            'Signal_Count': [],
            'Comment': []
        }

        for msg in messages:
            data['Message_Name'].append(msg['name'])
            data['CAN_ID_Hex'].append(f"0x{msg['frame_id']:X}")
            data['CAN_ID_Dec'].append(msg['frame_id'])
            data['DLC'].append(msg['length'])
            data['Signal_Count'].append(msg['signal_count'])
            data['Comment'].append(msg['comment'] or '')

        return pd.DataFrame(data)

    def _adjust_column_widths(self, writer):
        """
        Excel sütun genişliklerini otomatik ayarla.

        Args:
            writer: pd.ExcelWriter objesi
        """
        try:
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]

                for i, col in enumerate(worksheet.columns):
                    max_length = 0
                    column = col[0].column_letter

                    for cell in col:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column].width = adjusted_width

        except Exception as e:
            logger.warning(f"Sütun genişliği ayarlama hatası: {str(e)}")

    def export_filtered_signals(self, messages: List[Dict], signal_names: List[str],
                               dbc_parser, output_path: str) -> bool:
        """
        Belirli sinyalleri filtrele ve export et.

        Args:
            messages: Mesaj listesi
            signal_names: Export edilecek sinyal isimleri
            dbc_parser: DBCParser instance
            output_path: Çıktı dosya yolu

        Returns:
            bool: Export başarılı ise True
        """
        try:
            if not dbc_parser.is_loaded:
                raise Exception("DBC dosyası yüklü değil")

            # Sinyal verilerini topla
            signal_data = {'timestamps': []}
            for signal_name in signal_names:
                signal_data[signal_name] = []

            for msg in messages:
                decoded = dbc_parser.decode_message(msg['arbitration_id'], msg['data'])

                if decoded and decoded['signals']:
                    # İstenen sinyaller bu mesajda var mı kontrol et
                    has_signal = any(signal_name in decoded['signals']
                                   for signal_name in signal_names)

                    if has_signal:
                        signal_data['timestamps'].append(msg['timestamp'])

                        for signal_name in signal_names:
                            value = decoded['signals'].get(signal_name, None)
                            signal_data[signal_name].append(value)

            if not signal_data['timestamps']:
                raise ValueError("İstenen sinyaller için veri bulunamadı")

            # Export et
            return self.export_signals_to_excel(signal_data, output_path)

        except Exception as e:
            logger.error(f"Filtrelenmiş sinyal export hatası: {str(e)}")
            raise Exception(f"Filtrelenmiş sinyal export hatası: {str(e)}")
