# 🔋 Batarya Test Maliyeti Hesaplama Aracı

Batarya test süreçlerinin maliyetini hesaplamak, karşılaştırmak ve analiz etmek için profesyonel bir Python GUI uygulaması.

## 📋 İçindekiler

- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Maliyet Hesaplama Formülleri](#maliyet-hesaplama-formülleri)
- [Test Tipleri](#test-tipleri)
- [Bölgesel Maliyet Verileri](#bölgesel-maliyet-verileri)
- [Export Seçenekleri](#export-seçenekleri)
- [Ekran Görüntüleri](#ekran-görüntüleri)

## ✨ Özellikler

### 🧮 Maliyet Hesaplama
- **Detaylı Maliyet Analizi**: 7 farklı maliyet bileşenini hesaplar
  - İşçilik maliyeti
  - Enerji maliyeti
  - Ekipman amortismanı
  - Bakım maliyeti
  - Tesis maliyeti
  - Kalibrasyon maliyeti
  - Sarf malzemeleri

### 🔬 Test Tipleri
5 farklı batarya test tipi desteği:
- **Ömür Döngüsü Testi**: Tam şarj-deşarj döngüleri (~1000 saat)
- **Güvenlik Testi**: Kısa devre, aşırı şarj, termal kaçak testleri (48 saat)
- **Performans Testi**: Güç yoğunluğu, verimlilik, hız testleri (168 saat)
- **Termal Test**: Farklı sıcaklık koşullarında performans (120 saat)
- **Çevresel Test**: Nem, titreşim, darbe testleri (240 saat)

### 🌍 Bölgesel Karşılaştırma
4 farklı bölge için maliyet analizi:
- **Türkiye**: TRY cinsinden hesaplama
- **Avrupa**: EUR cinsinden hesaplama
- **Çin**: USD cinsinden hesaplama
- **Hindistan**: USD cinsinden hesaplama

Her bölge için özelleştirilmiş:
- İşçilik maliyetleri
- Enerji fiyatları
- Tesis maliyetleri
- Bakım oranları
- Dış kaynak kullanım katsayıları

### 📊 Analiz ve Karşılaştırma
- **Senaryo Karşılaştırma**: Kendi test vs Dış kaynak kullanımı
- **Zaman-Maliyet Grafiği**: Test süresine bağlı maliyet gelişimi
- **Bölgesel Karşılaştırma**: Tüm bölgeler için yan yana analiz
- **Grafik Gösterimler**: Matplotlib ile interaktif grafikler

### 💰 Para Birimi Desteği
- USD (Amerikan Doları)
- EUR (Euro)
- TRY (Türk Lirası)
- CNY (Çin Yuanı)
- INR (Hint Rupisi)

Otomatik dönüşüm oranları ile tüm hesaplamalar

### 📤 Export Özellikleri
- **Excel Export**: Detaylı tablolar ve grafikler
- **JSON Export**: Ham veri formatında
- **PDF Rapor**: Profesyonel rapor formatı (yakında)

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- tkinter (Python ile birlikte gelir)
- matplotlib
- openpyxl (Excel export için)

### Adım 1: Projeyi İndirin
```bash
git clone <repository-url>
cd ogz
```

### Adım 2: Gerekli Kütüphaneleri Kurun
```bash
pip install -r requirements.txt
```

### Adım 3: Uygulamayı Başlatın
```bash
python battery_test_cost_gui.py
```

## 📖 Kullanım

### 1. Tekli Maliyet Hesaplama

**"Maliyet Hesaplama"** sekmesinden:

1. **Test tipini** seçin (Ömür döngüsü, Güvenlik, vb.)
2. **Bölgeyi** seçin (Türkiye, Avrupa, Çin, Hindistan)
3. **Para birimini** seçin
4. **Parametreleri** girin (veya varsayılan değerleri kullanın):
   - Test süresi (saat)
   - Güç tüketimi (kW)
   - Personel sayısı
   - Batarya sayısı
   - Ekipman maliyeti
5. **Dış kaynak** kullanımı varsa işaretleyin
6. **"Hesapla"** butonuna tıklayın

Sonuçlar sağ panelde detaylı olarak görüntülenir.

### 2. Bölgesel Karşılaştırma

**"Bölge Karşılaştırma"** sekmesinden:

1. Test tipi ve para birimini seçin
2. Batarya sayısını girin
3. **"Karşılaştır"** butonuna tıklayın

Tüm bölgeler için:
- Karşılaştırma tablosu
- Bar grafikleri
- Maliyet bileşenleri dağılımı

otomatik olarak oluşturulur.

### 3. Senaryo Analizi

**"Senaryo Karşılaştırma"** sekmesinden:

1. Test tipi, bölge ve para birimini seçin
2. **"Karşılaştır"** butonuna tıklayın

**Kendi test** vs **Dış kaynak** senaryolarını:
- Detaylı maliyet dağılımları
- Toplam maliyet karşılaştırması
- Tasarruf/Ek maliyet analizi
- Grafik gösterimler

ile karşılaştırın.

### 4. Zaman-Maliyet Analizi

**"Zaman-Maliyet Grafiği"** sekmesinden:

1. Test tipi, bölge ve para birimini seçin
2. **"Grafik Oluştur"** butonuna tıklayın

Test süresine bağlı maliyet gelişimini gösteren interaktif grafik oluşturulur.

### 5. Export İşlemleri

**"Export & Rapor"** sekmesinden:

Herhangi bir hesaplama yaptıktan sonra:
- **Excel'e Aktar**: Detaylı Excel raporu
- **JSON'a Aktar**: Ham veri formatında export

## 📐 Maliyet Hesaplama Formülleri

### 1. İşçilik Maliyeti
```
İşçilik Maliyeti = Test Süresi (saat) × Personel Sayısı × Saat Ücreti
```

**Örnek**:
- Test süresi: 48 saat
- Personel: 2 kişi
- Saat ücreti: 65 USD/saat (Avrupa)
- **Toplam**: 48 × 2 × 65 = **6,240 USD**

### 2. Enerji Maliyeti
```
Enerji Maliyeti = Test Süresi (saat) × Güç Tüketimi (kW) × Birim Enerji Fiyatı (USD/kWh)
```

**Örnek**:
- Test süresi: 48 saat
- Güç: 3 kW
- Enerji fiyatı: 0.25 USD/kWh (Avrupa)
- **Toplam**: 48 × 3 × 0.25 = **36 USD**

### 3. Ekipman Amortismanı
```
Ekipman Amortismanı = (Ekipman Maliyeti / Kullanım Ömrü) × Test Süresi
```

**Örnek**:
- Ekipman maliyeti: 200,000 USD
- Kullanım ömrü: 30,000 saat
- Test süresi: 48 saat
- **Toplam**: (200,000 / 30,000) × 48 = **320 USD**

### 4. Bakım Maliyeti
```
Bakım Maliyeti = Ekipman Maliyeti × Yıllık Bakım Oranı × (Test Süresi / Yıllık Çalışma Saati)
```

**Örnek**:
- Ekipman maliyeti: 200,000 USD
- Bakım oranı: %10
- Test süresi: 48 saat
- Yıllık çalışma: 8,760 saat
- **Toplam**: 200,000 × 0.10 × (48 / 8,760) = **109.59 USD**

### 5. Tesis Maliyeti
```
Tesis Maliyeti = Saatlik Tesis Maliyeti × Test Süresi
```

**Örnek**:
- Tesis maliyeti: 40 USD/saat (Avrupa)
- Test süresi: 48 saat
- **Toplam**: 40 × 48 = **1,920 USD**

### 6. Kalibrasyon Maliyeti
```
Kalibrasyon Maliyeti = Yıllık Kalibrasyon Maliyeti / Yıllık Test Sayısı
```

**Örnek**:
- Yıllık kalibrasyon: 12,000 USD
- Yıllık test: 100 adet
- **Test başına**: 12,000 / 100 = **120 USD**

### 7. Sarf Malzemeleri
```
Sarf Malzemeleri = Sabit Test Başına Maliyet
```

**Örnek**:
- Avrupa: **350 USD** per test

### Toplam Maliyet
```
Toplam Maliyet = İşçilik + Enerji + Ekipman + Bakım + Tesis + Kalibrasyon + Sarf
```

**Güvenlik Testi Örneği (Avrupa)**:
- İşçilik: 6,240 USD
- Enerji: 36 USD
- Ekipman: 320 USD
- Bakım: 109.59 USD
- Tesis: 1,920 USD
- Kalibrasyon: 120 USD
- Sarf: 350 USD
- **TOPLAM: 9,095.59 USD**

### Birim Başına Maliyet
```
Birim Başına Maliyet = Toplam Maliyet / Test Edilen Batarya Sayısı
```

**Örnek**:
- Toplam: 9,095.59 USD
- Batarya sayısı: 5 adet
- **Birim başına**: 9,095.59 / 5 = **1,819.12 USD**

### Dış Kaynak Kullanımı
```
Dış Kaynak Maliyeti = Toplam Maliyet × Dış Kaynak Katsayısı
```

**Özel Düzenlemeler**:
- Ekipman amortismanı: 0 (ekipman sağlayıcıya ait)
- Bakım maliyeti: 0 (sağlayıcının sorumluluğu)
- Tesis maliyeti: %30 (kısmi tesis kullanımı)

**Örnek** (Avrupa, katsayı 1.4):
- Kendi test: 9,095.59 USD
- **Dış kaynak**: ~**11,500 USD**

## 🧪 Test Tipleri

### 1. Ömür Döngüsü Testi (Lifecycle Test)
**Süre**: ~1000 saat (42 gün)
**Güç**: 2.5 kW
**Personel**: 1 kişi
**Açıklama**: Bataryanın tam şarj-deşarj döngülerini test eder

**Tipik Kullanım**:
- Batarya kapasitesi düşüşünü ölçme
- Döngü ömrü belirleme
- SOH (State of Health) analizi

### 2. Güvenlik Testi (Safety Test)
**Süre**: 48 saat
**Güç**: 3.0 kW
**Personel**: 2 kişi
**Açıklama**: Kısa devre, aşırı şarj, termal kaçak testleri

**Testler**:
- Kısa devre testi
- Aşırı şarj testi
- Aşırı deşarj testi
- Termal kaçak (thermal runaway)
- Mekanik darbeye dayanıklılık
- Yangın testi

### 3. Performans Testi (Performance Test)
**Süre**: 168 saat (1 hafta)
**Güç**: 4.0 kW
**Personel**: 1 kişi
**Açıklama**: Güç yoğunluğu, verimlilik, hız testleri

**Ölçümler**:
- Maksimum güç çıkışı
- Enerji verimi
- Şarj/deşarj hızları
- Sıcaklık yönetimi
- Voltaj stabilitesi

### 4. Termal Test (Thermal Test)
**Süre**: 120 saat
**Güç**: 5.0 kW
**Personel**: 1 kişi
**Açıklama**: Farklı sıcaklık koşullarında performans testi

**Sıcaklık Aralıkları**:
- Düşük sıcaklık: -20°C to -40°C
- Oda sıcaklığı: 20°C to 25°C
- Yüksek sıcaklık: 40°C to 60°C

### 5. Çevresel Test (Environmental Test)
**Süre**: 240 saat
**Güç**: 3.5 kW
**Personel**: 1 kişi
**Açıklama**: Nem, titreşim, darbe testleri

**Test Koşulları**:
- Nem testi: %10 - %95 RH
- Titreşim testi: 10-200 Hz
- Darbe testi: 50-150g
- Tuz püskürtme
- Toz geçirmezlik

## 🌍 Bölgesel Maliyet Verileri

### Türkiye
| Parametre | Değer | Birim |
|-----------|-------|-------|
| İşçilik | 25.0 | USD/saat |
| Enerji | 0.12 | USD/kWh |
| Tesis | 15.0 | USD/saat |
| Bakım Oranı | %8 | yıllık |
| Kalibrasyon | 5,000 | USD/yıl |
| Sarf Malzeme | 200 | USD/test |
| Dış Kaynak Katsayısı | 1.6 | - |

### Avrupa
| Parametre | Değer | Birim |
|-----------|-------|-------|
| İşçilik | 65.0 | USD/saat |
| Enerji | 0.25 | USD/kWh |
| Tesis | 40.0 | USD/saat |
| Bakım Oranı | %10 | yıllık |
| Kalibrasyon | 12,000 | USD/yıl |
| Sarf Malzeme | 350 | USD/test |
| Dış Kaynak Katsayısı | 1.4 | - |

### Çin
| Parametre | Değer | Birim |
|-----------|-------|-------|
| İşçilik | 15.0 | USD/saat |
| Enerji | 0.08 | USD/kWh |
| Tesis | 10.0 | USD/saat |
| Bakım Oranı | %6 | yıllık |
| Kalibrasyon | 3,000 | USD/yıl |
| Sarf Malzeme | 150 | USD/test |
| Dış Kaynak Katsayısı | 1.3 | - |

### Hindistan
| Parametre | Değer | Birim |
|-----------|-------|-------|
| İşçilik | 12.0 | USD/saat |
| Enerji | 0.10 | USD/kWh |
| Tesis | 8.0 | USD/saat |
| Bakım Oranı | %7 | yıllık |
| Kalibrasyon | 2,500 | USD/yıl |
| Sarf Malzeme | 120 | USD/test |
| Dış Kaynak Katsayısı | 1.5 | - |

## 💾 Export Seçenekleri

### Excel Export
**Dosya formatı**: `.xlsx`

**İçerik**:
- Başlık ve tarih bilgisi
- Detaylı maliyet tablosu
- Maliyet bileşenleri (tutar ve yüzde)
- Formatlı hücreler ve renkler
- Otomatik sütun genişliği

**Örnek kullanım**:
1. Bir hesaplama yapın
2. "Export & Rapor" sekmesine gidin
3. "Excel'e Aktar" butonuna tıklayın
4. Dosya adı ve konum seçin
5. Dosya otomatik olarak oluşturulur

### JSON Export
**Dosya formatı**: `.json`

**İçerik**:
- ISO 8601 formatında timestamp
- Hesaplama tipi (single, comparison, scenario, timeline)
- Ham veri formatında tüm hesaplamalar
- UTF-8 encoding
- Girintili (indented) format

**Örnek JSON yapısı**:
```json
{
  "timestamp": "2024-11-21T19:30:00",
  "calculation_type": "single",
  "data": {
    "test_type": "safety",
    "region": "Avrupa",
    "battery_count": 5,
    "cost_breakdown": {
      "labor_cost": 6240.00,
      "energy_cost": 36.00,
      "equipment_depreciation": 320.00,
      "maintenance_cost": 109.59,
      "facility_cost": 1920.00,
      "calibration_cost": 120.00,
      "consumables_cost": 350.00,
      "total_cost": 9095.59,
      "cost_per_unit": 1819.12,
      "currency": "EUR"
    }
  }
}
```

### PDF Rapor (Yakında)
Profesyonel rapor formatında:
- Şirket logosu
- Detaylı maliyet analizi
- Grafikler ve tablolar
- Sayfa numaraları
- Başlık ve alt bilgi

## 🎨 Ekran Görüntüleri

### Ana Ekran - Maliyet Hesaplama
```
┌────────────────────────────────────────────────────────────────┐
│  🔋 Batarya Test Maliyeti Hesaplama Aracı                     │
├────────────────────────────────────────────────────────────────┤
│ Parametreler              │  Maliyet Analizi                   │
│                           │                                     │
│ Test Tipi: [Güvenlik]     │  ═══════════════════════════════   │
│ Bölge: [Avrupa]           │  BATARYA TEST MALİYETİ RAPORU      │
│ Para Birimi: [EUR]        │  ═══════════════════════════════   │
│                           │                                     │
│ Test Süresi: 48.0         │  Test Tipi: Güvenlik Testi         │
│ Güç Tüketimi: 3.0         │  Bölge: Avrupa                     │
│ Personel Sayısı: 2        │  Para Birimi: EUR                  │
│ Batarya Sayısı: 5         │                                     │
│                           │  MALİYET DAĞILIMI                  │
│ [✓] Dış Kaynak Kullan     │  ───────────────────────────────   │
│                           │  İşçilik: 6,240.00 EUR (68.6%)     │
│     [Hesapla]             │  Enerji: 36.00 EUR (0.4%)          │
│   [Varsayılana Dön]       │  Ekipman: 320.00 EUR (3.5%)        │
└───────────────────────────┴────────────────────────────────────┘
```

## 🔧 Özelleştirme

### Bölgesel Verileri Güncelleme

`cost_calculator.py` dosyasında `REGIONAL_DATA` dictionary'sini düzenleyin:

```python
REGIONAL_DATA = {
    'turkey': RegionalCostData(
        region='Türkiye',
        labor_cost_per_hour=25.0,  # Güncel değer
        energy_cost_per_kwh=0.12,
        # ... diğer parametreler
    ),
    # Yeni bölge ekleyin
    'usa': RegionalCostData(
        region='ABD',
        labor_cost_per_hour=70.0,
        energy_cost_per_kwh=0.15,
        # ...
    )
}
```

### Yeni Test Tipi Ekleme

`cost_calculator.py` dosyasında `TEST_PROFILES` dictionary'sini genişletin:

```python
TEST_PROFILES = {
    # ... mevcut profiller
    'custom_test': TestTypeProfile(
        test_type='Özel Test',
        typical_duration_hours=100.0,
        power_consumption_kw=2.0,
        required_personnel=1,
        equipment_cost=100000.0,
        equipment_lifetime_hours=40000,
        description='Özel test açıklaması'
    )
}
```

### Para Birimi Dönüşüm Oranlarını Güncelleme

`cost_calculator.py` dosyasında `CURRENCY_RATES`:

```python
CURRENCY_RATES = {
    'USD': 1.0,
    'EUR': 0.92,  # Güncel oran
    'TRY': 34.5,  # Güncel oran
    # ...
}
```

## 📊 Örnek Kullanım Senaryoları

### Senaryo 1: Güvenlik Testi Maliyeti (Türkiye)
```python
from cost_calculator import BatteryTestCostCalculator

calculator = BatteryTestCostCalculator()

cost = calculator.calculate_cost(
    test_type='safety',
    region='turkey',
    battery_count=10,
    target_currency='TRY'
)

print(f"Toplam: {cost.total_cost:,.2f} TRY")
print(f"Birim: {cost.cost_per_unit:,.2f} TRY")
```

### Senaryo 2: Bölgeleri Karşılaştır
```python
results = calculator.compare_regions(
    test_type='lifecycle',
    battery_count=5,
    target_currency='USD'
)

for region, cost in results.items():
    print(f"{region}: {cost.total_cost:,.2f} USD")
```

### Senaryo 3: Kendi Test vs Dış Kaynak
```python
scenarios = calculator.compare_scenarios(
    test_type='performance',
    region='europe',
    target_currency='EUR'
)

in_house = scenarios['in_house'].total_cost
outsource = scenarios['outsource'].total_cost
savings = in_house - outsource

print(f"Tasarruf: {savings:,.2f} EUR")
```

## 🐛 Sorun Giderme

### Grafik Görünmüyor
**Çözüm**: matplotlib backend ayarlarını kontrol edin:
```python
import matplotlib
matplotlib.use('TkAgg')
```

### Excel Export Çalışmıyor
**Çözüm**: openpyxl kütüphanesini kurun:
```bash
pip install openpyxl
```

### Pencere Boyutu Sorunları
**Çözüm**: Kod içinde `root.geometry()` değerini ayarlayın:
```python
root.geometry("1600x1000")  # Daha büyük pencere
```

### Türkçe Karakter Sorunları
**Çözüm**: UTF-8 encoding kullanıldığından emin olun:
```python
# -*- coding: utf-8 -*-
```

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

## 🔄 Güncellemeler

### v1.0.0 (2024-11-21)
- ✨ İlk sürüm yayınlandı
- ✅ 5 test tipi desteği
- ✅ 4 bölge karşılaştırması
- ✅ Excel ve JSON export
- ✅ Grafik gösterimleri
- ✅ Para birimi dönüşümü

## 🎯 Gelecek Özellikler

- [ ] PDF rapor oluşturma
- [ ] Veritabanı entegrasyonu
- [ ] Geçmiş hesaplama kayıtları
- [ ] Özel test profilleri oluşturma
- [ ] API entegrasyonu
- [ ] Çoklu dil desteği
- [ ] Dark mode tema
- [ ] Bulut senkronizasyonu

---

**Not**: Bu araç batarya test maliyetlerinin tahmini hesaplamasını sağlar. Gerçek maliyetler kullanılan ekipman, bölgesel koşullar ve diğer faktörlere bağlı olarak değişebilir.
