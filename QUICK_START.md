# 🚀 Batarya Test Maliyeti Hesaplama - Hızlı Başlangıç

## ⚡ 5 Dakikada Başlayın

### 1. Kurulum

```bash
# Gereksinimleri yükleyin
pip install matplotlib openpyxl

# Not: tkinter Python ile birlikte gelir, ayrıca kurulum gerekmez
```

### 2. Uygulamayı Başlatın

```bash
python battery_test_cost_gui.py
```

### 3. İlk Hesaplamanızı Yapın

1. **"Maliyet Hesaplama"** sekmesinde:
   - Test Tipi: `safety` (Güvenlik Testi)
   - Bölge: `Türkiye`
   - Para Birimi: `TRY`
   - **"Hesapla"** butonuna tıklayın

2. Sonuçları sağ panelde görün!

## 📊 Örnek Kullanımlar

### Terminal'den Hızlı Hesaplama

```python
from cost_calculator import BatteryTestCostCalculator

calculator = BatteryTestCostCalculator()

# Ömür döngüsü testi - Türkiye
cost = calculator.calculate_cost(
    test_type='lifecycle',
    region='turkey',
    battery_count=10,
    target_currency='TRY'
)

print(f"Toplam: {cost.total_cost:,.2f} TRY")
# Çıktı: Toplam: 1,549,735.27 TRY
```

### Excel Şablonu Oluşturma

```bash
python create_excel_template.py
```

Otomatik olarak `batarya_test_maliyet_sablonu.xlsx` dosyası oluşturulur.

## 🎯 Test Tipleri

| Test | Süre | Kullanım |
|------|------|----------|
| `lifecycle` | 1000 saat | Ömür döngüsü |
| `safety` | 48 saat | Güvenlik testleri |
| `performance` | 168 saat | Performans analizi |
| `thermal` | 120 saat | Termal testler |
| `environmental` | 240 saat | Çevresel testler |

## 🌍 Bölgeler

| Kod | Bölge | Para Birimi |
|-----|-------|-------------|
| `turkey` | Türkiye | TRY |
| `europe` | Avrupa | EUR |
| `china` | Çin | USD |
| `india` | Hindistan | USD |

## 💡 İpuçları

### Varsayılan Değerleri Kullanın
- Test tipini seçtiğinizde otomatik olarak varsayılan değerler gelir
- **"Varsayılana Dön"** butonu ile her zaman varsayılana dönebilirsiniz

### Karşılaştırmalar Yapın
- **"Bölge Karşılaştırma"** sekmesi: Hangi bölge daha ekonomik?
- **"Senaryo Karşılaştırma"** sekmesi: Kendi test mi, dış kaynak mı?

### Export Edin
- Herhangi bir hesaplama yaptıktan sonra
- **"Export & Rapor"** sekmesinden Excel veya JSON'a aktarın

## 🔧 Sorun Giderme

### GUI Açılmıyor
```bash
# tkinter yüklü mü kontrol edin
python -c "import tkinter"

# Linux için:
sudo apt-get install python3-tk
```

### Grafik Görünmüyor
```bash
pip install --upgrade matplotlib
```

### Excel Export Çalışmıyor
```bash
pip install openpyxl
```

## 📖 Daha Fazla Bilgi

Detaylı dokümantasyon için:
- `BATTERY_COST_CALCULATOR_README.md` dosyasını okuyun
- Tüm formüller ve açıklamalar orada!

## 🎥 Örnek Çıktı

```
================================================================================
BATARYA TEST MALİYETİ HESAPLAMA RAPORU
================================================================================

Test Tipi      : Güvenlik Testi
Bölge          : Türkiye
Senaryo        : Kendi Test
Para Birimi    : TRY

------------------------------------------------------------------------------
MALİYET DAĞILIMI
------------------------------------------------------------------------------

İşçilik Maliyeti         :    41,400.00 TRY (31.7%)
Enerji Maliyeti          :       414.00 TRY ( 0.3%)
Ekipman Amortismanı      :    11,040.00 TRY ( 8.5%)
Bakım Maliyeti           :     6,575.34 TRY ( 5.0%)
Tesis Maliyeti           :    24,840.00 TRY (19.0%)
Kalibrasyon Maliyeti     :     1,725.00 TRY ( 1.3%)
Sarf Malzemeleri         :     6,900.00 TRY ( 5.3%)

================================================================================
TOPLAM MALİYET           :   130,894.34 TRY
BİRİM BAŞINA MALİYET     :    26,178.87 TRY
================================================================================
```

## 🚀 Hadi Başlayalım!

```bash
python battery_test_cost_gui.py
```

**Başarılar!** 🎉
