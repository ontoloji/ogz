"""
Test verisi okuma modülü
Excel, CSV ve JSON formatlarından test verilerini okur
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime


class DataReader:
    """Test verisi okuma sınıfı"""

    def __init__(self):
        """DataReader başlatıcı"""
        self.data = None
        self.metadata = None
        self.file_path = None

    def read_csv(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> pd.DataFrame:
        """
        CSV dosyasını oku

        Args:
            file_path: CSV dosya yolu
            encoding: Dosya kodlaması

        Returns:
            DataFrame: Okunan veri
        """
        self.file_path = Path(file_path)
        try:
            self.data = pd.read_csv(file_path, encoding=encoding)
            print(f"✓ CSV dosyası okundu: {file_path}")
            print(f"  - Satır sayısı: {len(self.data)}")
            print(f"  - Sütun sayısı: {len(self.data.columns)}")
            return self.data
        except Exception as e:
            raise Exception(f"CSV okuma hatası: {str(e)}")

    def read_excel(
        self,
        file_path: Union[str, Path],
        sheet_name: Union[str, int] = 0
    ) -> pd.DataFrame:
        """
        Excel dosyasını oku

        Args:
            file_path: Excel dosya yolu
            sheet_name: Sayfa adı veya index

        Returns:
            DataFrame: Okunan veri
        """
        self.file_path = Path(file_path)
        try:
            self.data = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"✓ Excel dosyası okundu: {file_path}")
            print(f"  - Sayfa: {sheet_name}")
            print(f"  - Satır sayısı: {len(self.data)}")
            print(f"  - Sütun sayısı: {len(self.data.columns)}")
            return self.data
        except Exception as e:
            raise Exception(f"Excel okuma hatası: {str(e)}")

    def read_json(self, file_path: Union[str, Path]) -> Dict:
        """
        JSON dosyasını oku (metadata için)

        Args:
            file_path: JSON dosya yolu

        Returns:
            Dict: Okunan metadata
        """
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"✓ JSON metadata okundu: {file_path}")
            return self.metadata
        except Exception as e:
            raise Exception(f"JSON okuma hatası: {str(e)}")

    def read_multiple_files(
        self,
        file_paths: List[Union[str, Path]],
        file_type: str = 'csv'
    ) -> List[pd.DataFrame]:
        """
        Birden fazla dosyayı oku

        Args:
            file_paths: Dosya yolu listesi
            file_type: Dosya tipi ('csv' veya 'excel')

        Returns:
            List[DataFrame]: Okunan veriler listesi
        """
        data_list = []
        for path in file_paths:
            if file_type == 'csv':
                df = self.read_csv(path)
            elif file_type == 'excel':
                df = self.read_excel(path)
            else:
                raise ValueError(f"Desteklenmeyen dosya tipi: {file_type}")
            data_list.append(df)

        print(f"\n✓ Toplam {len(data_list)} dosya okundu")
        return data_list

    def read_test_data_with_metadata(
        self,
        data_file: Union[str, Path],
        metadata_file: Optional[Union[str, Path]] = None
    ) -> tuple[pd.DataFrame, Optional[Dict]]:
        """
        Test verisini metadata ile birlikte oku

        Args:
            data_file: Test verisi dosyası (CSV)
            metadata_file: Metadata dosyası (JSON), None ise otomatik arar

        Returns:
            tuple: (DataFrame, metadata dict)
        """
        # Veriyi oku
        data = self.read_csv(data_file)

        # Metadata'yı oku
        metadata = None
        if metadata_file is None:
            # Otomatik metadata dosyası ara (.meta.json uzantılı)
            data_path = Path(data_file)
            potential_metadata = data_path.parent / f"{data_path.stem}.meta.json"
            if potential_metadata.exists():
                metadata_file = potential_metadata

        if metadata_file and Path(metadata_file).exists():
            metadata = self.read_json(metadata_file)

        return data, metadata

    def validate_columns(self, required_columns: List[str]) -> bool:
        """
        Gerekli sütunların varlığını kontrol et

        Args:
            required_columns: Gerekli sütun isimleri

        Returns:
            bool: Tüm sütunlar mevcutsa True

        Raises:
            ValueError: Eksik sütun varsa
        """
        if self.data is None:
            raise ValueError("Veri henüz okunmadı")

        missing_columns = [col for col in required_columns if col not in self.data.columns]

        if missing_columns:
            raise ValueError(
                f"Eksik sütunlar: {missing_columns}\n"
                f"Mevcut sütunlar: {list(self.data.columns)}"
            )

        print(f"✓ Tüm gerekli sütunlar mevcut")
        return True

    def get_column_info(self) -> pd.DataFrame:
        """
        Sütun bilgilerini döndür

        Returns:
            DataFrame: Sütun isimleri ve tipleri
        """
        if self.data is None:
            raise ValueError("Veri henüz okunmadı")

        info_df = pd.DataFrame({
            'Column': self.data.columns,
            'Type': self.data.dtypes.values,
            'Non-Null Count': self.data.count().values,
            'Null Count': self.data.isnull().sum().values
        })

        return info_df

    def filter_data(
        self,
        filters: Dict[str, any]
    ) -> pd.DataFrame:
        """
        Veriyi filtrele

        Args:
            filters: Filtre kriterleri {column: value}

        Returns:
            DataFrame: Filtrelenmiş veri
        """
        if self.data is None:
            raise ValueError("Veri henüz okunmadı")

        filtered_data = self.data.copy()
        for column, value in filters.items():
            if column in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[column] == value]

        print(f"✓ Veri filtrelendi: {len(filtered_data)} / {len(self.data)} satır kaldı")
        return filtered_data

    def get_time_range(self, time_column: str = 'Time') -> tuple:
        """
        Zaman aralığını döndür

        Args:
            time_column: Zaman sütunu adı

        Returns:
            tuple: (başlangıç, bitiş) zamanları
        """
        if self.data is None:
            raise ValueError("Veri henüz okunmadı")

        if time_column not in self.data.columns:
            raise ValueError(f"Sütun bulunamadı: {time_column}")

        return (self.data[time_column].min(), self.data[time_column].max())

    def export_summary(self, output_file: Union[str, Path]):
        """
        Veri özetini Excel'e aktar

        Args:
            output_file: Çıktı dosya yolu
        """
        if self.data is None:
            raise ValueError("Veri henüz okunmadı")

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Veri özeti
            self.data.describe().to_excel(writer, sheet_name='Summary')

            # Sütun bilgileri
            self.get_column_info().to_excel(writer, sheet_name='Column Info', index=False)

            # Ham veri (ilk 1000 satır)
            self.data.head(1000).to_excel(writer, sheet_name='Data Preview', index=False)

        print(f"✓ Veri özeti kaydedildi: {output_file}")


class TestDataReader(DataReader):
    """SORT test verileri için özelleştirilmiş veri okuyucu"""

    # SORT test verisi için beklenen sütunlar
    EXPECTED_COLUMNS = [
        'Time',
        'Speed',
        'Distance',
        'Throttle',
        'Energy'
    ]

    def __init__(self):
        super().__init__()
        self.test_type = None
        self.test_metadata = {}

    def read_sort_test(
        self,
        data_file: Union[str, Path],
        validate: bool = True
    ) -> pd.DataFrame:
        """
        SORT test verisini oku ve doğrula

        Args:
            data_file: Test verisi dosyası
            validate: Veriyi doğrula

        Returns:
            DataFrame: Test verisi
        """
        # Veri ve metadata'yı oku
        data, metadata = self.read_test_data_with_metadata(data_file)

        # Metadata'dan test tipini al
        if metadata:
            self.test_metadata = metadata
            self.test_type = metadata.get('test_type', 'Unknown')
            print(f"  - Test tipi: {self.test_type}")

        # Doğrulama
        if validate:
            self.validate_columns(self.EXPECTED_COLUMNS)

        return data

    def get_test_info(self) -> Dict:
        """
        Test bilgilerini döndür

        Returns:
            Dict: Test bilgileri
        """
        info = {
            'test_type': self.test_type,
            'duration': self.get_time_range()[1] if self.data is not None else None,
            'total_distance': self.data['Distance'].max() if self.data is not None and 'Distance' in self.data.columns else None,
            'metadata': self.test_metadata
        }
        return info
