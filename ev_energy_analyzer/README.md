# ⚡ Elektrikli Araç Enerji Tüketimi Analiz Sistemi

Windows için profesyonel elektrikli araç enerji tüketimi analiz uygulaması.

## 🎯 Özellikler

### Temel Özellikler
- ✅ Windows Excel dosyalarından test verilerini okuma (zaman, hız, akım, voltaj, sıcaklık)
- ✅ UITP SORT test döngüsüne göre enerji tüketimi hesaplama
- ✅ kWh/100km hesaplaması
- ✅ Menzil tahmini (farklı batarya kapasiteleri için)
- ✅ Regeneratif frenleme verimlilik analizi
- ✅ Sıcaklık etkisi analizi
- ✅ Otomatik grafik oluşturma (hız profili, enerji tüketimi, SOC değişimi)
- ✅ PDF rapor çıktısı (şirket logolu, profesyonel görünüm)
- ✅ Karşılaştırma modu (farklı test tarihlerini karşılaştırma)
- ✅ Windows 10/11 uyumlu modern GUI
- ✅ .exe olarak derlenebilir

### UITP SORT Test Döngüleri
- **SORT 1**: Düşük hızlı şehir içi trafiği (maks 25 km/h)
- **SORT 2**: Orta hızlı karışık trafik (maks 40 km/h)
- **SORT 3**: Yüksek hızlı banliyö trafiği (maks 60 km/h)

## 📋 Gereksinimler

### Sistem Gereksinimleri
- Windows 10/11
- Python 3.8 veya üzeri
- 4 GB RAM (önerilen)
- 500 MB disk alanı

### Python Kütüphaneleri
```
pandas>=1.5.0
numpy>=1.23.0
openpyxl>=3.0.10
matplotlib>=3.6.0
reportlab>=3.6.0
pyinstaller>=5.7.0  (opsiyonel, .exe için)
```

## 🚀 Kurulum

### 1. Depoyu klonlayın
```bash
git clone <repository-url>
cd ev_energy_analyzer
```

### 2. Sanal ortam oluşturun (önerilen)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 4. Örnek veri oluşturun
```bash
python create_sample_data.py
```

## 💻 Kullanım

### Python ile çalıştırma
```bash
python main.py
```

### Adımlar
1. **Excel Dosyası Seç**: Test verilerinizi içeren Excel dosyasını seçin
2. **SORT Döngüsü Seç**: Otomatik tespit veya manuel seçim
3. **Batarya Ayarları**: Batarya kapasitesi ve başlangıç SOC değerini girin
4. **Analiz Başlat**: Enerji tüketimi analizini başlatın
5. **Sonuçları İncele**: Detaylı sonuçları ve grafikleri görüntüleyin
6. **PDF Rapor**: Profesyonel PDF rapor oluşturun

### Excel Dosya Formatı
Excel dosyanızda şu sütunlar bulunmalıdır:
- **Zaman** (saniye): Test süresi
- **Hız** (km/h): Araç hızı
- **Akım** (A): Batarya akımı
- **Voltaj** (V): Batarya voltajı
- **Sıcaklık** (°C): Ortam/batarya sıcaklığı (opsiyonel)

## 🔧 .exe Derleme

### PyInstaller ile .exe oluşturma
```bash
python build_exe.py
```

veya manuel olarak:
```bash
pyinstaller --onefile --windowed --name="EVEnergyAnalyzer" --icon=assets/icon.ico main.py
```

Oluşturulan .exe dosyası `dist/` klasöründe bulunur.

## 📊 Analiz Sonuçları

### Enerji Tüketimi
- Toplam enerji tüketimi (kWh)
- kWh/100km değeri
- Faz bazında tüketim (hızlanma, yavaşlama, sabit hız, durma)

### Menzil Tahminleri
- Teorik menzil
- Gerçekçi menzil (%90 verimlilik)
- Minimum menzil (%75 verimlilik)
- Farklı batarya kapasiteleri için tahminler

### Regeneratif Frenleme
- Geri kazanılan enerji miktarı
- Regen verimliliği yüzdesi
- Ortalama ve maksimum regen gücü
- Regen olay sayısı

### Sıcaklık Etkisi
- Ortalama test sıcaklığı
- Sıcaklık etkisi faktörü
- Normalize edilmiş enerji tüketimi
- Sıcaklıktan kaynaklı tüketim artışı

### Grafikler
- Hız profili
- Güç profili
- Enerji tüketimi
- SOC (Şarj Durumu) değişimi
- Sıcaklık etkisi
- Sürüş fazları dağılımı
- Menzil karşılaştırması

## 📁 Proje Yapısı

```
ev_energy_analyzer/
├── src/
│   ├── gui/
│   │   └── main_window.py          # Ana GUI penceresi
│   ├── modules/
│   │   ├── excel_reader.py         # Excel okuma modülü
│   │   ├── sort_calculator.py      # SORT hesaplama modülü
│   │   ├── energy_analyzer.py      # Enerji analiz modülü
│   │   ├── chart_generator.py      # Grafik oluşturma modülü
│   │   ├── pdf_reporter.py         # PDF rapor modülü
│   │   └── comparison.py           # Karşılaştırma modülü
│   └── utils/
│       └── config.py                # Konfigürasyon ayarları
├── assets/
│   └── logo.png                     # Şirket logosu (PDF için)
├── data/
│   └── ornek_test_verisi.xlsx      # Örnek test verisi
├── output/                          # Grafikler ve raporlar
├── main.py                          # Ana çalıştırma dosyası
├── create_sample_data.py           # Örnek veri oluşturucu
├── requirements.txt                 # Python bağımlılıkları
└── README.md                        # Bu dosya
```

## 🔬 Karşılaştırma Modu

Birden fazla testi karşılaştırmak için:

1. "Karşılaştırma Modu" butonuna tıklayın
2. İlk test dosyasını yükleyin ve analiz edin
3. İkinci test dosyasını yükleyin ve analiz edin
4. Sonuçlar otomatik olarak karşılaştırma listesine eklenir
5. Karşılaştırma grafikleri ve raporları otomatik oluşturulur

### Karşılaştırılan Metrikler
- Enerji tüketimi (kWh/100km)
- Regen verimliliği
- Maksimum ve ortalama güç
- Verimlilik skoru
- Hız profilleri

## 🛠️ Teknik Detaylar

### UITP SORT Metodolojisi
Bu uygulama, UITP (International Association of Public Transport) tarafından belirlenen SORT (Standardised On-Road Test) metodolojisini kullanır. SORT, toplu taşıma araçlarının enerji tüketimini standart koşullarda ölçmek için geliştirilmiş uluslararası bir test standardıdır.

### Hesaplama Formülleri

**Enerji Tüketimi:**
```
E (kWh) = ∫ P(t) dt / 3600000
P (W) = V × I
```

**Menzil Tahmini:**
```
Menzil (km) = (Batarya Kapasitesi × Kullanılabilir SOC) / (Tüketim / 100)
```

**Regeneratif Frenleme Verimliliği:**
```
Verimlilik (%) = (Geri Kazanılan Enerji / Toplam Tüketilen Enerji) × 100
```

## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📧 İletişim

Sorularınız veya önerileriniz için lütfen issue açın.

## 🙏 Teşekkürler

- UITP SORT metodolojisi için UITP'ye
- Python topluluğuna
- Tüm katkıda bulunanlara

---

**Not**: Bu yazılım, elektrikli araç test verilerinin analizinde yardımcı olmak için geliştirilmiştir. Gerçek dünya koşulları, test sonuçlarından farklılık gösterebilir.
