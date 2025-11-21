"""
İstatistiksel analiz modülü
Test verilerinin istatistiksel analizini yapar
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from scipy import stats


class StatisticsAnalyzer:
    """İstatistiksel analiz sınıfı"""

    def __init__(self, decimal_places: int = 2):
        """
        Args:
            decimal_places: Ondalık basamak sayısı
        """
        self.decimal_places = decimal_places

    def basic_statistics(self, data: pd.Series) -> Dict[str, float]:
        """
        Temel istatistikler hesapla

        Args:
            data: Veri serisi

        Returns:
            Dict: İstatistik sonuçları
        """
        stats_dict = {
            'count': int(len(data)),
            'mean': round(data.mean(), self.decimal_places),
            'median': round(data.median(), self.decimal_places),
            'std': round(data.std(), self.decimal_places),
            'min': round(data.min(), self.decimal_places),
            'max': round(data.max(), self.decimal_places),
            'range': round(data.max() - data.min(), self.decimal_places),
            'q25': round(data.quantile(0.25), self.decimal_places),
            'q75': round(data.quantile(0.75), self.decimal_places),
        }

        # IQR (Interquartile Range)
        stats_dict['iqr'] = round(stats_dict['q75'] - stats_dict['q25'], self.decimal_places)

        # Variation coefficient (CV)
        if stats_dict['mean'] != 0:
            stats_dict['cv'] = round((stats_dict['std'] / stats_dict['mean']) * 100, self.decimal_places)
        else:
            stats_dict['cv'] = 0

        return stats_dict

    def multi_column_statistics(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Birden fazla sütun için istatistik hesapla

        Args:
            df: DataFrame
            columns: Analiz edilecek sütunlar

        Returns:
            DataFrame: İstatistik tablosu
        """
        results = {}
        for col in columns:
            if col in df.columns:
                results[col] = self.basic_statistics(df[col])

        stats_df = pd.DataFrame(results).T
        return stats_df

    def compare_datasets(
        self,
        datasets: Dict[str, pd.DataFrame],
        column: str
    ) -> pd.DataFrame:
        """
        Birden fazla veri setini karşılaştır

        Args:
            datasets: {isim: DataFrame} dictionary
            column: Karşılaştırılacak sütun

        Returns:
            DataFrame: Karşılaştırma tablosu
        """
        results = {}
        for name, df in datasets.items():
            if column in df.columns:
                results[name] = self.basic_statistics(df[column])

        comparison_df = pd.DataFrame(results).T
        return comparison_df

    def confidence_interval(
        self,
        data: pd.Series,
        confidence: float = 0.95
    ) -> tuple[float, float]:
        """
        Güven aralığı hesapla

        Args:
            data: Veri serisi
            confidence: Güven seviyesi (0-1 arası)

        Returns:
            tuple: (alt_sınır, üst_sınır)
        """
        mean = data.mean()
        std_err = stats.sem(data)
        margin = std_err * stats.t.ppf((1 + confidence) / 2, len(data) - 1)

        lower = round(mean - margin, self.decimal_places)
        upper = round(mean + margin, self.decimal_places)

        return (lower, upper)

    def outlier_detection(
        self,
        data: pd.Series,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> pd.Series:
        """
        Aykırı değerleri tespit et

        Args:
            data: Veri serisi
            method: 'iqr' veya 'zscore'
            threshold: Eşik değeri (IQR için 1.5, Z-score için 3.0 önerilir)

        Returns:
            Series: Aykırı değerlerin boolean mask'i
        """
        if method == 'iqr':
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            outliers = (data < lower_bound) | (data > upper_bound)

        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(data))
            outliers = z_scores > threshold

        else:
            raise ValueError(f"Geçersiz method: {method}")

        return outliers

    def test_normality(self, data: pd.Series) -> Dict[str, any]:
        """
        Normallik testi (Shapiro-Wilk)

        Args:
            data: Veri serisi

        Returns:
            Dict: Test sonuçları
        """
        statistic, p_value = stats.shapiro(data)

        return {
            'statistic': round(statistic, 4),
            'p_value': round(p_value, 4),
            'is_normal': p_value > 0.05,  # %5 anlamlılık seviyesi
            'interpretation': 'Normal dağılım' if p_value > 0.05 else 'Normal dağılım değil'
        }

    def correlation_analysis(
        self,
        df: pd.DataFrame,
        columns: List[str],
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """
        Korelasyon analizi

        Args:
            df: DataFrame
            columns: Analiz edilecek sütunlar
            method: 'pearson', 'spearman', veya 'kendall'

        Returns:
            DataFrame: Korelasyon matrisi
        """
        correlation_matrix = df[columns].corr(method=method)
        return correlation_matrix.round(self.decimal_places)

    def moving_average(
        self,
        data: pd.Series,
        window: int = 5
    ) -> pd.Series:
        """
        Hareketli ortalama hesapla

        Args:
            data: Veri serisi
            window: Pencere boyutu

        Returns:
            Series: Hareketli ortalama
        """
        return data.rolling(window=window, center=True).mean()

    def calculate_energy_consumption(
        self,
        energy: pd.Series,
        distance: pd.Series,
        unit: str = 'kWh/100km'
    ) -> float:
        """
        Enerji tüketimi hesapla

        Args:
            energy: Enerji değerleri (Wh veya kWh)
            distance: Mesafe değerleri (m veya km)
            unit: Çıktı birimi

        Returns:
            float: Enerji tüketimi
        """
        total_energy = energy.iloc[-1] - energy.iloc[0]  # Wh
        total_distance = distance.iloc[-1] - distance.iloc[0]  # m

        if total_distance == 0:
            return 0

        if unit == 'kWh/100km':
            # Wh to kWh, m to km, then per 100km
            consumption = (total_energy / 1000) / (total_distance / 1000) * 100
        elif unit == 'Wh/km':
            consumption = total_energy / (total_distance / 1000)
        else:
            raise ValueError(f"Desteklenmeyen birim: {unit}")

        return round(consumption, self.decimal_places)


class RequirementChecker:
    """Gereksinim kontrolü sınıfı"""

    def __init__(self, requirements: Dict[str, Dict[str, float]]):
        """
        Args:
            requirements: Gereksinim kriterleri
                Örnek: {
                    'SORT1': {
                        'max_energy_consumption': 100,
                        'max_duration': 3600,
                        'min_distance': 1000
                    }
                }
        """
        self.requirements = requirements

    def check_requirement(
        self,
        test_type: str,
        parameter: str,
        actual_value: float
    ) -> Dict[str, any]:
        """
        Tek bir gereksinim kontrolü

        Args:
            test_type: Test tipi (ör. 'SORT1')
            parameter: Parametre adı
            actual_value: Gerçekleşen değer

        Returns:
            Dict: Kontrol sonucu
        """
        if test_type not in self.requirements:
            return {
                'test_type': test_type,
                'parameter': parameter,
                'actual': actual_value,
                'requirement': None,
                'status': 'UNKNOWN',
                'message': f'Test tipi bulunamadı: {test_type}'
            }

        test_reqs = self.requirements[test_type]

        if parameter not in test_reqs:
            return {
                'test_type': test_type,
                'parameter': parameter,
                'actual': actual_value,
                'requirement': None,
                'status': 'UNKNOWN',
                'message': f'Parametre bulunamadı: {parameter}'
            }

        req_value = test_reqs[parameter]

        # Max kontrolü
        if parameter.startswith('max_'):
            status = 'PASS' if actual_value <= req_value else 'FAIL'
            comparison = f'{actual_value} <= {req_value}'
        # Min kontrolü
        elif parameter.startswith('min_'):
            status = 'PASS' if actual_value >= req_value else 'FAIL'
            comparison = f'{actual_value} >= {req_value}'
        # Eşitlik kontrolü
        else:
            status = 'PASS' if actual_value == req_value else 'FAIL'
            comparison = f'{actual_value} == {req_value}'

        return {
            'test_type': test_type,
            'parameter': parameter,
            'actual': actual_value,
            'requirement': req_value,
            'status': status,
            'comparison': comparison,
            'message': f'{status}: {comparison}'
        }

    def check_all_requirements(
        self,
        test_type: str,
        actual_values: Dict[str, float]
    ) -> List[Dict[str, any]]:
        """
        Tüm gereksinimleri kontrol et

        Args:
            test_type: Test tipi
            actual_values: Gerçekleşen değerler {parametre: değer}

        Returns:
            List[Dict]: Tüm kontrol sonuçları
        """
        results = []
        for parameter, value in actual_values.items():
            result = self.check_requirement(test_type, parameter, value)
            results.append(result)

        return results

    def generate_summary(self, check_results: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Gereksinim kontrolü özeti

        Args:
            check_results: Kontrol sonuçları

        Returns:
            Dict: Özet bilgiler
        """
        total = len(check_results)
        passed = sum(1 for r in check_results if r['status'] == 'PASS')
        failed = sum(1 for r in check_results if r['status'] == 'FAIL')
        unknown = sum(1 for r in check_results if r['status'] == 'UNKNOWN')

        overall_status = 'PASS' if failed == 0 and unknown == 0 else 'FAIL'

        return {
            'total_checks': total,
            'passed': passed,
            'failed': failed,
            'unknown': unknown,
            'pass_rate': round((passed / total * 100), 2) if total > 0 else 0,
            'overall_status': overall_status
        }
