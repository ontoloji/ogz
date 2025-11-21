# 📖 Kullanım Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. İlk Kurulum

#### Adım 1: Python Kurulumu
- Python 3.8 veya üzerini [python.org](https://www.python.org/downloads/) adresinden indirin
- Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

#### Adım 2: Projeyi İndirin
```bash
# Git ile
git clone <repository-url>
cd ev_energy_analyzer

# veya ZIP olarak indirip açın
```

#### Adım 3: Bağımlılıkları Kurun
```bash
# Windows Command Prompt veya PowerShell'de
pip install -r requirements.txt
```

#### Adım 4: Örnek Veri Oluşturun
```bash
python create_sample_data.py
```

### 2. Uygulamayı Başlatma

#### Python ile
```bash
python main.py
```

#### veya Windows'ta çift tıklama
`start.bat` dosyasını çift tıklayın

### 3. İlk Analiz

1. **Excel Dosyası Seçin**
   - "📁 Excel Dosyası Seç" butonuna tıklayın
   - Test verilerinizi içeren .xlsx dosyasını seçin
   - Örnek: `data/ornek_test_verisi.xlsx`

2. **SORT Döngüsü Seçin**
   - **Otomatik Tespit**: Program otomatik olarak uygun döngüyü belirler (önerilen)
   - **SORT 1**: Şehir içi düşük hızlı trafik
   - **SORT 2**: Karışık orta hızlı trafik
   - **SORT 3**: Banliyö yüksek hızlı trafik

3. **Batarya Ayarları**
   - **Batarya Kapasitesi**: Aracınızın batarya kapasitesini seçin (kWh)
   - **Başlangıç SOC**: Test başlangıcındaki şarj durumunu girin (%)

4. **Analiz Başlat**
   - "🔍 Analiz Başlat" butonuna tıklayın
   - İşlem günlüğünü takip edin
   - Sonuçlar "📊 Sonuçlar" sekmesinde görüntülenir

5. **PDF Rapor**
   - "📄 PDF Rapor Oluştur" butonuna tıklayın
   - Rapor `output/` klasörüne kaydedilir
   - Otomatik olarak açılır

## 📊 Excel Dosya Formatı

### Gerekli Sütunlar

Excel dosyanızda şu sütunlar **mutlaka** bulunmalıdır:

| Sütun Adı | Birim | Açıklama | Örnek |
|-----------|-------|----------|-------|
| Zaman | saniye | Test başlangıcından itibaren geçen süre | 0, 1, 2, 3... |
| Hız | km/h | Anlık araç hızı | 0, 15.5, 40.2... |
| Akım | Amper (A) | Batarya akımı (+ tüketim, - regen) | 50, -20, 100... |
| Voltaj | Volt (V) | Batarya voltajı | 400, 395, 410... |
| Sıcaklık | °C | Ortam/batarya sıcaklığı (opsiyonel) | 25, 26.5, 28... |

### Alternatif Sütun İsimleri

Program aşağıdaki isimleri de tanır:
- **Zaman**: Time, Süre, Duration, T
- **Hız**: Speed, Velocity, V
- **Akım**: Current, I, A
- **Voltaj**: Voltage, U, V
- **Sıcaklık**: Temperature, Temp, T

### Örnek Veri Yapısı

```
Zaman   Hız    Akım   Voltaj  Sıcaklık
0       0      0      400     25.0
1       0      0      400     25.1
2       5.2    45     398     25.2
3       10.5   80     395     25.3
4       15.0   95     393     25.4
...
```

## 🔍 Analiz Sonuçları

### 1. Test Bilgileri
- Dosya adı ve yolu
- Toplam veri sayısı
- Test süresi
- Toplam mesafe
- Maksimum ve ortalama hız
- Toplam enerji tüketimi

### 2. SORT Analizi
- Tespit edilen döngü tipi
- Standart vs gerçek değerler
- Uyumluluk yüzdeleri
- Enerji tüketimi (kWh/100km)

### 3. Enerji Analizi
- **Tüketim Metrikleri**
  - Toplam enerji (kWh)
  - kWh/100km
  - Faz bazında tüketim

- **Regeneratif Frenleme**
  - Geri kazanılan enerji
  - Verimlilik yüzdesi
  - Ortalama/maksimum regen gücü

- **Sıcaklık Etkisi**
  - Sıcaklık etkisi faktörü
  - Normalize edilmiş tüketim
  - Tüketim artış yüzdesi

### 4. Menzil Tahminleri
Her batarya kapasitesi için:
- **Teorik Menzil**: İdeal koşullarda maksimum menzil
- **Gerçekçi Menzil**: Normal kullanımda beklenen menzil (%90 verimlilik)
- **Minimum Menzil**: Zorlu koşullarda minimum menzil (%75 verimlilik)

### 5. Grafikler
- **Hız Profili**: Zaman-hız grafiği, faz göstergeleri
- **Güç Profili**: Motor ve regen gücü
- **Enerji Tüketimi**: Kümülatif enerji grafiği
- **SOC Değişimi**: Batarya şarj durumu
- **Sıcaklık Etkisi**: Sıcaklık ve güç ilişkisi
- **Faz Dağılımı**: Sürüş fazlarının oranları
- **Menzil Karşılaştırması**: Farklı batarya kapasiteleri

## 📈 Karşılaştırma Modu

### Birden Fazla Testi Karşılaştırma

1. **Modu Etkinleştir**
   - "📊 Karşılaştırma Modu" butonuna tıklayın
   - Mod aktif olduğunda bildirim alırsınız

2. **Test Ekle**
   - İlk test dosyasını seçin ve analiz edin
   - İkinci test dosyasını seçin ve analiz edin
   - Her analiz otomatik olarak karşılaştırma listesine eklenir

3. **Sonuçları Görüntüle**
   - Karşılaştırma grafikleri otomatik oluşturulur
   - Tüketim, performans ve hız profilleri karşılaştırılır

4. **Modu Kapat**
   - Tekrar "📊 Karşılaştırma Modu" butonuna tıklayın
   - Liste temizlenir

### Karşılaştırılan Metrikler
- ✅ Enerji tüketimi (kWh/100km)
- ✅ Regeneratif frenleme verimliliği
- ✅ Maksimum ve ortalama güç
- ✅ Maksimum hız
- ✅ Verimlilik skoru
- ✅ Hız profilleri (çakıştırmalı grafik)

## 📄 PDF Rapor İçeriği

### Rapor Bölümleri

1. **Başlık Sayfası**
   - Şirket logosu (varsa)
   - Rapor başlığı
   - Tarih ve saat

2. **Test Bilgileri Tablosu**
   - Dosya adı
   - Test süresi ve mesafesi
   - Hız ve güç metrikleri

3. **SORT Analizi**
   - Döngü tipi ve açıklama
   - Standart karşılaştırması
   - Uyumluluk tablosu

4. **Enerji Analizi**
   - Tüketim metrikleri
   - Regeneratif frenleme detayları
   - Sıcaklık etkisi analizi

5. **Menzil Tahminleri Tablosu**
   - Tüm batarya kapasiteleri
   - Teorik, gerçekçi ve minimum menziller

6. **Grafikler**
   - Yüksek çözünürlüklü (300 DPI)
   - Renkli ve profesyonel görünüm
   - Türkçe etiketler

### Logo Ekleme

PDF raporuna şirket logosu eklemek için:
1. Logo dosyanızı `assets/logo.png` olarak kaydedin
2. PNG formatı, önerilen boyut: 400x200 piksel
3. Şeffaf arkaplan desteklenir

## 🛠️ .exe Derleme

### Windows Çalıştırılabilir Oluşturma

1. **PyInstaller'ı kurun** (henüz kurulu değilse)
   ```bash
   pip install pyinstaller
   ```

2. **Build script'ini çalıştırın**
   ```bash
   python build_exe.py
   ```

3. **Alternatif: Manuel derleme**
   ```bash
   pyinstaller --onefile --windowed --name=EVEnergyAnalyzer main.py
   ```

4. **Sonuç**
   - .exe dosyası `dist/` klasöründe oluşturulur
   - Boyut: ~80-120 MB
   - Tek dosya, Python gerektirmez

### Dağıtım

.exe dosyasını dağıtırken:
- ✅ Tek başına çalışır (Python gerekmez)
- ✅ `data/` klasörünü de ekleyin (örnek veri için)
- ✅ `assets/` klasörünü ekleyin (logo için)
- ⚠️ Windows Defender taraması gerekebilir

## ❓ Sık Sorulan Sorular

### Q: Excel dosyam okunamıyor?
**A:** Kontrol edin:
- Dosya .xlsx formatında mı?
- Gerekli sütunlar var mı?
- Sütun isimleri doğru mu?
- Veri sayısal mı? (metin içermemeli)

### Q: Grafikler oluşturulmuyor?
**A:**
- matplotlib kurulu mu? (`pip install matplotlib`)
- `output/` klasörü var mı?
- Yazma izni var mı?

### Q: PDF oluşturulamıyor?
**A:**
- reportlab kurulu mu? (`pip install reportlab`)
- `output/` klasöründe yer var mı?
- Varolan PDF açık değil mi? (kapatın)

### Q: Sıcaklık verisi yok ne olur?
**A:** Sıcaklık opsiyoneldir. Olmadığında:
- Sıcaklık analizi atlanır
- Diğer analizler normal çalışır
- Sıcaklık grafikleri oluşturulmaz

### Q: Karşılaştırma modunda kaç test ekleyebilirim?
**A:** Teorik olarak sınırsız, ancak:
- Okunabilirlik için 4-6 test önerilir
- Çok fazla test grafikleri karmaşıklaştırır
- RAM kullanımı artar

### Q: Hangi SORT döngüsünü seçmeliyim?
**A:**
- **Otomatik**: Program en uygununu seçer (önerilen)
- **Manuel**: Test koşullarınıza göre
  - Şehir içi → SORT 1
  - Karışık → SORT 2
  - Banliyö → SORT 3

## 📞 Destek

### Sorun Bildirme
1. GitHub Issues kullanın
2. Şunları ekleyin:
   - Hata mesajı
   - Excel dosya formatı
   - Python versiyonu
   - İşletim sistemi

### Log Dosyaları
İşlem günlüğü:
- GUI'de "📝 İşlem Günlüğü" sekmesinde
- Hataları buradan kopyalayın

## 🎓 İleri Düzey Kullanım

### Python API'si

Modülleri Python scriptlerinizde kullanabilirsiniz:

```python
from modules.excel_reader import load_excel_data
from modules.energy_analyzer import EnergyAnalyzer

# Veriyi yükle
df, metadata, info, warnings = load_excel_data("test.xlsx")

# Analiz yap
analyzer = EnergyAnalyzer(df)
results = analyzer.full_analysis()

# Sonuçları kullan
print(f"Tüketim: {results['consumption']['consumption_per_100km']:.2f} kWh/100km")
```

### Özel Grafik Oluşturma

```python
from modules.chart_generator import ChartGenerator

gen = ChartGenerator(df, title_prefix="Özel Test - ")
gen.plot_speed_profile(output_path="ozel_grafik.png")
```

### Toplu İşlem

```python
import glob

for file in glob.glob("data/*.xlsx"):
    # Her dosyayı işle
    df, _, _, _ = load_excel_data(file)
    # ... analiz yap
```

## 📚 Ek Kaynaklar

- [UITP SORT Metodolojisi](https://www.uitp.org/)
- [Pandas Dokümantasyonu](https://pandas.pydata.org/)
- [Matplotlib Kılavuzu](https://matplotlib.org/)
- [ReportLab PDF](https://www.reportlab.com/)

---

**Son Güncelleme**: 2024
**Versiyon**: 1.0
