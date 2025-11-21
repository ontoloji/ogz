"""
Batarya Test Maliyeti Hesaplama Modülü

Bu modül batarya testlerinin maliyetini hesaplamak için gerekli
tüm formül ve fonksiyonları içerir.

Maliyet Bileşenleri:
1. Personel Maliyeti = Test Süresi × Personel Sayısı × Saat Ücreti
2. Enerji Maliyeti = Test Süresi × Güç Tüketimi × Birim Enerji Fiyatı
3. Ekipman Amortismanı = (Ekipman Maliyeti / Kullanım Ömrü) × Test Süresi
4. Bakım Maliyeti = Ekipman Maliyeti × Yıllık Bakım Oranı × (Test Süresi / Yıllık Çalışma Saati)
5. Tesis Maliyeti = Saatlik Tesis Maliyeti × Test Süresi
6. Kalibrasyon Maliyeti = (Yıllık Kalibrasyon / Yıllık Test Sayısı)
7. Sarf Malzemeleri = Test Başına Sarf Malzeme Maliyeti

Toplam Maliyet = Σ(Tüm Maliyet Bileşenleri)
Birim Başına Maliyet = Toplam Maliyet / Test Edilen Batarya Sayısı
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class RegionalCostData:
    """Bölgesel maliyet parametreleri"""
    region: str
    labor_cost_per_hour: float  # Saat başına işçilik maliyeti
    energy_cost_per_kwh: float  # kWh başına enerji maliyeti
    facility_cost_per_hour: float  # Saat başına tesis maliyeti
    maintenance_rate: float  # Yıllık bakım oranı (%)
    calibration_cost_per_year: float  # Yıllık kalibrasyon maliyeti
    consumables_per_test: float  # Test başına sarf malzeme maliyeti
    currency: str  # Para birimi
    outsource_multiplier: float = 1.5  # Dış kaynak kullanım katsayısı


@dataclass
class TestTypeProfile:
    """Test tipi profili"""
    test_type: str
    typical_duration_hours: float  # Tipik test süresi (saat)
    power_consumption_kw: float  # Güç tüketimi (kW)
    required_personnel: int  # Gerekli personel sayısı
    equipment_cost: float  # Ekipman maliyeti
    equipment_lifetime_hours: int  # Ekipman kullanım ömrü (saat)
    description: str = ""


@dataclass
class CostBreakdown:
    """Maliyet dağılımı"""
    labor_cost: float = 0.0
    energy_cost: float = 0.0
    equipment_depreciation: float = 0.0
    maintenance_cost: float = 0.0
    facility_cost: float = 0.0
    calibration_cost: float = 0.0
    consumables_cost: float = 0.0
    total_cost: float = 0.0
    cost_per_unit: float = 0.0
    currency: str = "USD"

    def to_dict(self) -> Dict:
        """Dictionary'ye dönüştür"""
        return {
            'labor_cost': round(self.labor_cost, 2),
            'energy_cost': round(self.energy_cost, 2),
            'equipment_depreciation': round(self.equipment_depreciation, 2),
            'maintenance_cost': round(self.maintenance_cost, 2),
            'facility_cost': round(self.facility_cost, 2),
            'calibration_cost': round(self.calibration_cost, 2),
            'consumables_cost': round(self.consumables_cost, 2),
            'total_cost': round(self.total_cost, 2),
            'cost_per_unit': round(self.cost_per_unit, 2),
            'currency': self.currency
        }


class BatteryTestCostCalculator:
    """Batarya test maliyeti hesaplayıcı"""

    # Test profilleri
    TEST_PROFILES = {
        'lifecycle': TestTypeProfile(
            test_type='Ömür Döngüsü Testi',
            typical_duration_hours=1000.0,  # ~42 gün
            power_consumption_kw=2.5,
            required_personnel=1,
            equipment_cost=150000.0,  # USD
            equipment_lifetime_hours=50000,
            description='Bataryanın tam şarj-deşarj döngülerini test eder'
        ),
        'safety': TestTypeProfile(
            test_type='Güvenlik Testi',
            typical_duration_hours=48.0,
            power_consumption_kw=3.0,
            required_personnel=2,
            equipment_cost=200000.0,
            equipment_lifetime_hours=30000,
            description='Kısa devre, aşırı şarj, termal kaçak testleri'
        ),
        'performance': TestTypeProfile(
            test_type='Performans Testi',
            typical_duration_hours=168.0,  # 1 hafta
            power_consumption_kw=4.0,
            required_personnel=1,
            equipment_cost=120000.0,
            equipment_lifetime_hours=40000,
            description='Güç yoğunluğu, verimlilik, hız testleri'
        ),
        'thermal': TestTypeProfile(
            test_type='Termal Test',
            typical_duration_hours=120.0,
            power_consumption_kw=5.0,
            required_personnel=1,
            equipment_cost=180000.0,
            equipment_lifetime_hours=35000,
            description='Farklı sıcaklık koşullarında performans testi'
        ),
        'environmental': TestTypeProfile(
            test_type='Çevresel Test',
            typical_duration_hours=240.0,
            power_consumption_kw=3.5,
            required_personnel=1,
            equipment_cost=160000.0,
            equipment_lifetime_hours=40000,
            description='Nem, titreşim, darbe testleri'
        )
    }

    # Bölgesel maliyet verileri
    REGIONAL_DATA = {
        'turkey': RegionalCostData(
            region='Türkiye',
            labor_cost_per_hour=25.0,  # USD/saat
            energy_cost_per_kwh=0.12,  # USD/kWh
            facility_cost_per_hour=15.0,
            maintenance_rate=0.08,  # %8
            calibration_cost_per_year=5000.0,
            consumables_per_test=200.0,
            currency='TRY',
            outsource_multiplier=1.6
        ),
        'europe': RegionalCostData(
            region='Avrupa',
            labor_cost_per_hour=65.0,
            energy_cost_per_kwh=0.25,
            facility_cost_per_hour=40.0,
            maintenance_rate=0.10,
            calibration_cost_per_year=12000.0,
            consumables_per_test=350.0,
            currency='EUR',
            outsource_multiplier=1.4
        ),
        'china': RegionalCostData(
            region='Çin',
            labor_cost_per_hour=15.0,
            energy_cost_per_kwh=0.08,
            facility_cost_per_hour=10.0,
            maintenance_rate=0.06,
            calibration_cost_per_year=3000.0,
            consumables_per_test=150.0,
            currency='USD',
            outsource_multiplier=1.3
        ),
        'india': RegionalCostData(
            region='Hindistan',
            labor_cost_per_hour=12.0,
            energy_cost_per_kwh=0.10,
            facility_cost_per_hour=8.0,
            maintenance_rate=0.07,
            calibration_cost_per_year=2500.0,
            consumables_per_test=120.0,
            currency='USD',
            outsource_multiplier=1.5
        )
    }

    # Para birimi çevrim oranları (USD bazında)
    CURRENCY_RATES = {
        'USD': 1.0,
        'EUR': 0.92,
        'TRY': 34.5,
        'CNY': 7.24,
        'INR': 83.12
    }

    def __init__(self):
        """Hesaplayıcıyı başlat"""
        self.annual_working_hours = 8760  # Yılda 365 gün × 24 saat
        self.annual_test_count = 100  # Yıllık ortalama test sayısı

    def calculate_cost(
        self,
        test_type: str,
        region: str,
        test_duration_hours: float = None,
        power_consumption_kw: float = None,
        personnel_count: int = None,
        battery_count: int = 1,
        is_outsource: bool = False,
        target_currency: str = 'USD',
        custom_equipment_cost: float = None
    ) -> CostBreakdown:
        """
        Test maliyetini hesapla

        Args:
            test_type: Test tipi ('lifecycle', 'safety', 'performance', vb.)
            region: Bölge ('turkey', 'europe', 'china', 'india')
            test_duration_hours: Test süresi (saat), None ise varsayılan kullanılır
            power_consumption_kw: Güç tüketimi (kW), None ise varsayılan kullanılır
            personnel_count: Personel sayısı, None ise varsayılan kullanılır
            battery_count: Test edilen batarya sayısı
            is_outsource: Dış kaynak kullanımı
            target_currency: Hedef para birimi
            custom_equipment_cost: Özel ekipman maliyeti

        Returns:
            CostBreakdown: Maliyet dağılımı
        """
        # Profilleri al
        test_profile = self.TEST_PROFILES.get(test_type)
        if not test_profile:
            raise ValueError(f"Geçersiz test tipi: {test_type}")

        regional_data = self.REGIONAL_DATA.get(region)
        if not regional_data:
            raise ValueError(f"Geçersiz bölge: {region}")

        # Parametreleri belirle (custom veya default)
        duration = test_duration_hours if test_duration_hours is not None else test_profile.typical_duration_hours
        power = power_consumption_kw if power_consumption_kw is not None else test_profile.power_consumption_kw
        personnel = personnel_count if personnel_count is not None else test_profile.required_personnel
        equipment_cost = custom_equipment_cost if custom_equipment_cost is not None else test_profile.equipment_cost

        # Maliyet bileşenlerini hesapla
        breakdown = CostBreakdown(currency='USD')  # Önce USD'de hesapla

        # 1. Personel maliyeti
        breakdown.labor_cost = duration * personnel * regional_data.labor_cost_per_hour

        # 2. Enerji maliyeti
        breakdown.energy_cost = duration * power * regional_data.energy_cost_per_kwh

        # 3. Ekipman amortismanı
        breakdown.equipment_depreciation = (equipment_cost / test_profile.equipment_lifetime_hours) * duration

        # 4. Bakım maliyeti
        breakdown.maintenance_cost = (
            equipment_cost * regional_data.maintenance_rate *
            (duration / self.annual_working_hours)
        )

        # 5. Tesis maliyeti
        breakdown.facility_cost = regional_data.facility_cost_per_hour * duration

        # 6. Kalibrasyon maliyeti
        breakdown.calibration_cost = regional_data.calibration_cost_per_year / self.annual_test_count

        # 7. Sarf malzemeleri
        breakdown.consumables_cost = regional_data.consumables_per_test

        # Toplam maliyet
        breakdown.total_cost = (
            breakdown.labor_cost +
            breakdown.energy_cost +
            breakdown.equipment_depreciation +
            breakdown.maintenance_cost +
            breakdown.facility_cost +
            breakdown.calibration_cost +
            breakdown.consumables_cost
        )

        # Dış kaynak kullanımı
        if is_outsource:
            breakdown.total_cost *= regional_data.outsource_multiplier
            # Dış kaynak kullanımında bazı maliyetler olmaz
            breakdown.equipment_depreciation = 0
            breakdown.maintenance_cost = 0
            breakdown.facility_cost *= 0.3  # Kısmi tesis maliyeti

        # Birim başına maliyet
        breakdown.cost_per_unit = breakdown.total_cost / battery_count if battery_count > 0 else 0

        # Para birimi dönüşümü
        if target_currency != 'USD':
            rate = self.CURRENCY_RATES.get(target_currency, 1.0)
            breakdown.labor_cost *= rate
            breakdown.energy_cost *= rate
            breakdown.equipment_depreciation *= rate
            breakdown.maintenance_cost *= rate
            breakdown.facility_cost *= rate
            breakdown.calibration_cost *= rate
            breakdown.consumables_cost *= rate
            breakdown.total_cost *= rate
            breakdown.cost_per_unit *= rate
            breakdown.currency = target_currency

        return breakdown

    def compare_regions(
        self,
        test_type: str,
        test_duration_hours: float = None,
        battery_count: int = 1,
        target_currency: str = 'USD'
    ) -> Dict[str, CostBreakdown]:
        """
        Tüm bölgeleri karşılaştır

        Args:
            test_type: Test tipi
            test_duration_hours: Test süresi
            battery_count: Batarya sayısı
            target_currency: Hedef para birimi

        Returns:
            Dict: Bölge başına maliyet dağılımı
        """
        results = {}
        for region in self.REGIONAL_DATA.keys():
            results[region] = self.calculate_cost(
                test_type=test_type,
                region=region,
                test_duration_hours=test_duration_hours,
                battery_count=battery_count,
                target_currency=target_currency
            )
        return results

    def compare_scenarios(
        self,
        test_type: str,
        region: str,
        test_duration_hours: float = None,
        battery_count: int = 1,
        target_currency: str = 'USD'
    ) -> Dict[str, CostBreakdown]:
        """
        Kendi test vs dış kaynak senaryolarını karşılaştır

        Args:
            test_type: Test tipi
            region: Bölge
            test_duration_hours: Test süresi
            battery_count: Batarya sayısı
            target_currency: Hedef para birimi

        Returns:
            Dict: Senaryo başına maliyet dağılımı
        """
        in_house = self.calculate_cost(
            test_type=test_type,
            region=region,
            test_duration_hours=test_duration_hours,
            battery_count=battery_count,
            is_outsource=False,
            target_currency=target_currency
        )

        outsource = self.calculate_cost(
            test_type=test_type,
            region=region,
            test_duration_hours=test_duration_hours,
            battery_count=battery_count,
            is_outsource=True,
            target_currency=target_currency
        )

        return {
            'in_house': in_house,
            'outsource': outsource
        }

    def get_cost_timeline(
        self,
        test_type: str,
        region: str,
        battery_count: int = 1,
        target_currency: str = 'USD',
        time_points: int = 10
    ) -> Tuple[List[float], List[float]]:
        """
        Zaman-maliyet grafiği için veri oluştur

        Args:
            test_type: Test tipi
            region: Bölge
            battery_count: Batarya sayısı
            target_currency: Hedef para birimi
            time_points: Zaman noktası sayısı

        Returns:
            Tuple: (zaman_listesi, maliyet_listesi)
        """
        test_profile = self.TEST_PROFILES.get(test_type)
        if not test_profile:
            raise ValueError(f"Geçersiz test tipi: {test_type}")

        total_duration = test_profile.typical_duration_hours
        time_step = total_duration / time_points

        times = []
        costs = []

        for i in range(time_points + 1):
            current_time = i * time_step
            times.append(current_time)

            if current_time == 0:
                costs.append(0)
            else:
                breakdown = self.calculate_cost(
                    test_type=test_type,
                    region=region,
                    test_duration_hours=current_time,
                    battery_count=battery_count,
                    target_currency=target_currency
                )
                costs.append(breakdown.total_cost)

        return times, costs

    def export_to_dict(self, breakdown: CostBreakdown, test_info: Dict = None) -> Dict:
        """
        Maliyet bilgilerini dict'e aktar

        Args:
            breakdown: Maliyet dağılımı
            test_info: Ek test bilgileri

        Returns:
            Dict: Tüm bilgileri içeren dictionary
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'cost_breakdown': breakdown.to_dict()
        }

        if test_info:
            result['test_info'] = test_info

        return result


# Test kodu
if __name__ == "__main__":
    calculator = BatteryTestCostCalculator()

    # Örnek hesaplama
    print("=" * 80)
    print("BATARYA TEST MALİYETİ HESAPLAMA ARACI")
    print("=" * 80)
    print()

    # Ömür döngüsü testi - Türkiye
    print("Test: Ömür Döngüsü Testi - Türkiye")
    print("-" * 80)
    cost = calculator.calculate_cost(
        test_type='lifecycle',
        region='turkey',
        battery_count=10,
        target_currency='TRY'
    )
    print(f"Toplam Maliyet: {cost.total_cost:,.2f} {cost.currency}")
    print(f"Birim Başına Maliyet: {cost.cost_per_unit:,.2f} {cost.currency}")
    print(f"  - İşçilik: {cost.labor_cost:,.2f} {cost.currency}")
    print(f"  - Enerji: {cost.energy_cost:,.2f} {cost.currency}")
    print(f"  - Ekipman Amortismanı: {cost.equipment_depreciation:,.2f} {cost.currency}")
    print(f"  - Bakım: {cost.maintenance_cost:,.2f} {cost.currency}")
    print(f"  - Tesis: {cost.facility_cost:,.2f} {cost.currency}")
    print(f"  - Kalibrasyon: {cost.calibration_cost:,.2f} {cost.currency}")
    print(f"  - Sarf Malzeme: {cost.consumables_cost:,.2f} {cost.currency}")
    print()

    # Bölge karşılaştırması
    print("Bölgesel Karşılaştırma (Güvenlik Testi)")
    print("-" * 80)
    comparisons = calculator.compare_regions('safety', battery_count=5, target_currency='USD')
    for region, cost in comparisons.items():
        print(f"{calculator.REGIONAL_DATA[region].region:12s}: {cost.total_cost:12,.2f} USD (Birim: {cost.cost_per_unit:,.2f} USD)")
    print()

    # Senaryo karşılaştırması
    print("Senaryo Karşılaştırması (Performans Testi - Avrupa)")
    print("-" * 80)
    scenarios = calculator.compare_scenarios('performance', 'europe', battery_count=8, target_currency='EUR')
    print(f"Kendi Test : {scenarios['in_house'].total_cost:12,.2f} EUR")
    print(f"Dış Kaynak : {scenarios['outsource'].total_cost:12,.2f} EUR")
    savings = scenarios['in_house'].total_cost - scenarios['outsource'].total_cost
    print(f"Fark       : {savings:12,.2f} EUR ({'Tasarruf' if savings > 0 else 'Ek Maliyet'})")
