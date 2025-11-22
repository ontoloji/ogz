# Araç Kalifikasyon Takip Sistemi

Windows ortamında çalışan, araç modellerinin kalifikasyon proje takibini yapan Python tabanlı masaüstü uygulaması.

## Özellikler

- ✅ **Araç Kaydı**: Araçları resim ve teknik özelliklerle birlikte kaydedin
- ✅ **Günlük Girdiler**: Her araç için günlük test ve çalışma kayıtları
- ✅ **Görsel Dashboard**: Araçların resimleri, isimleri ve günlük girdileri ana sayfada
- ✅ **Araç Listesi**: Tüm araçları liste halinde görüntüleme ve düzenleme
- ✅ **Haftalık Raporlar**: Otomatik haftalık özet raporlar
- ✅ **Excel Export**: Raporları Excel formatında dışa aktarma
- ✅ **Arama ve Filtreleme**: Hızlı araç arama

## Sistem Gereksinimleri

### Yazılım
- **Windows** 10 veya üzeri
- **Python** 3.10 veya üzeri
- **PyQt6** (GUI için)
- **pandas** (Veri işleme için)
- **openpyxl** (Excel export için)

### Donanım
- Minimum 4 GB RAM
- 100 MB boş disk alanı
- 1280x720 veya daha yüksek ekran çözünürlüğü

## Kurulum

### 1. Python Kurulumu

Windows için Python'u [python.org](https://www.python.org/downloads/) adresinden indirin ve kurun.

**Önemli**: Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin!

### 2. Bağımlılıkları Yükle

Komut satırını (CMD) açın ve proje klasörüne gidin:

```cmd
cd C:\path\to\ogz
```

Gerekli paketleri yükleyin:

```cmd
pip install PyQt6 pandas openpyxl
```

Veya requirements.txt kullanarak:

```cmd
pip install -r requirements.txt
```

## Kullanım

### Hızlı Başlatma (Windows)

Proje klasöründe `start_vehicle_qualification.bat` dosyasına çift tıklayın.

### Manuel Başlatma

Komut satırından:

```cmd
python vehicle_qualification_gui.py
```

## Kullanım Kılavuzu

### 1. İlk Başlatma

Program ilk kez çalıştırıldığında otomatik olarak:
- `vehicle_qualification.db` veritabanı dosyası oluşturulur
- `vehicle_images/` klasörü oluşturulur (araç resimleri için)

### 2. Yeni Araç Ekleme

1. Ana pencerede **"Yeni Araç Ekle"** butonuna tıklayın
2. Araç bilgilerini doldurun:
   - **Araç Adı** (zorunlu)
   - Model, Üretici, Yıl
   - Araç Tipi (Elektrikli, Dizel, vb.)
3. **"Resim Seç"** ile araç fotoğrafı ekleyin
4. **Teknik Özellikler** bölümüne JSON formatında özellikler girin:
   ```json
   {
     "motor_gucu": "150 kW",
     "batarya": "75 kWh",
     "menzil": "400 km",
     "tork": "310 Nm"
   }
   ```
5. İsterseniz notlar ekleyin
6. **"Save"** butonuna tıklayın

### 3. Günlük Girdi Ekleme

#### Yöntem 1: Dashboard'dan
1. **Ana Sayfa** sekmesinde araç kartını bulun
2. **"Günlük Girdi Ekle"** butonuna tıklayın

#### Yöntem 2: Araç Listesinden
1. **Araç Listesi** sekmesine geçin
2. Aracı seçin ve **"Detayları Gör"** butonuna tıklayın
3. Günlük girdi dialogunu açın

#### Girdi Bilgileri
- **Tarih**: Test/çalışma tarihi
- **Test Tipi**: SORT 1/2/3, Performans, vb.
- **Test Sonucu**: Başarılı, Başarısız, vb.
- **Mesafe (km)**: Katedilen mesafe
- **Süre (saat)**: Test süresi
- **Yakıt Tüketimi (L)**: Yakıt sarfiyatı
- **Enerji Tüketimi (kWh)**: Elektrik tüketimi
- **Durum**: Tamamlandı, Devam Ediyor, vb.
- **Operatör**: Test operatörü adı
- **Sıcaklık (°C)**: Ortam sıcaklığı
- **Hava Durumu**: Güneşli, Yağmurlu, vb.
- **Sorunlar**: Karşılaşılan problemler
- **Notlar**: Ek notlar

### 4. Ana Sayfa (Dashboard)

Ana sayfa özellikleri:
- **Araç Kartları**: Her araç için görsel kart
  - Araç resmi
  - Araç adı, model, üretici
  - Son 5 günlük girdi
- **Arama**: Üstteki arama çubuğuyla araç ara
- **Hızlı İşlemler**:
  - "Günlük Girdi Ekle" - Doğrudan girdi ekle
  - "Detaylar" - Araç detaylarını görüntüle

### 5. Araç Listesi

Liste görünümü özellikleri:
- Tüm araçları tablo halinde görüntüleme
- Sütunlar: ID, Araç Adı, Model, Üretici, Yıl, Tip, Durum
- **Çift tıklama** ile detayları görüntüleme
- **Düzenle**: Araç bilgilerini güncelle
- **Sil**: Aracı sil (soft delete)

### 6. Haftalık Raporlar

1. **Raporlar** sekmesine geçin
2. **Araç seçin** (veya "Tüm Araçlar")
3. **Hafta seçin**:
   - Bu Hafta
   - Geçen Hafta
   - 2/3/4 Hafta Önce
4. **"Haftalık Rapor Oluştur"** butonuna tıklayın

Rapor içeriği:
- Tarih aralığı
- Toplam girdi sayısı
- Toplam mesafe, süre
- Toplam yakıt/enerji tüketimi
- Günlük detaylar tablosu

### 7. Excel'e Aktarma

1. Rapor oluşturduktan sonra
2. **"Excel'e Aktar"** butonuna tıklayın
3. Dosya adı ve konum seçin
4. Excel dosyası oluşturulur:
   - **Sayfa 1**: Günlük Girdiler (detay)
   - **Sayfa 2**: Özet istatistikler

## Dosya Yapısı

```
ogz/
├── vehicle_qualification_gui.py    # Ana GUI programı
├── vehicle_database.py              # Veritabanı modülü
├── start_vehicle_qualification.bat  # Windows başlatıcı
├── VEHICLE_QUALIFICATION_README.md  # Bu dosya
├── vehicle_qualification.db         # SQLite veritabanı (otomatik oluşur)
├── vehicle_images/                  # Araç resimleri (otomatik oluşur)
│   ├── Arac_A1_20241122_143022.jpg
│   └── ...
└── requirements.txt                 # Python bağımlılıkları
```

## Veritabanı Yapısı

### Tablolar

#### vehicles
- `id`: Benzersiz araç ID
- `name`: Araç adı
- `model`: Model
- `manufacturer`: Üretici
- `year`: Yıl
- `vehicle_type`: Araç tipi
- `image_path`: Resim dosya yolu
- `specifications`: Teknik özellikler (JSON)
- `notes`: Notlar
- `created_date`: Oluşturma tarihi
- `updated_date`: Güncelleme tarihi
- `status`: Durum (active/inactive/deleted)

#### daily_entries
- `id`: Benzersiz girdi ID
- `vehicle_id`: Araç ID (foreign key)
- `entry_date`: Girdi tarihi
- `entry_time`: Girdi saati
- `test_type`: Test tipi
- `test_result`: Test sonucu
- `distance_km`: Mesafe (km)
- `duration_hours`: Süre (saat)
- `fuel_consumption`: Yakıt tüketimi (L)
- `energy_consumption`: Enerji tüketimi (kWh)
- `status`: Durum
- `issues`: Sorunlar
- `notes`: Notlar
- `operator`: Operatör
- `temperature`: Sıcaklık (°C)
- `weather`: Hava durumu
- `created_at`: Oluşturma zamanı

## İpuçları ve En İyi Uygulamalar

### Araç Resimleri
- **Desteklenen formatlar**: PNG, JPG, JPEG, BMP, GIF
- **Önerilen boyut**: 800x600 piksel
- **Dosya boyutu**: Maksimum 5 MB
- Resimler otomatik olarak `vehicle_images/` klasörüne kopyalanır

### Teknik Özellikler
- **JSON formatı** kullanın
- Türkçe karakter kullanabilirsiniz
- Örnek format:
  ```json
  {
    "motor_gucu": "150 kW",
    "batarya_kapasitesi": "75 kWh",
    "maksimum_hiz": "180 km/h",
    "menzil": "400 km",
    "sarj_suresi": "8 saat",
    "tork": "310 Nm"
  }
  ```

### Günlük Girdiler
- **Düzenli kayıt**: Her test sonrası hemen kaydedin
- **Detaylı notlar**: Sorunları ve gözlemleri detaylı yazın
- **Operatör bilgisi**: Kim test ettiyse ismini yazın
- **Çevre koşulları**: Sıcaklık ve hava durumu önemli!

### Raporlama
- **Haftalık kontrol**: Her hafta sonu rapor alın
- **Excel saklama**: Raporları düzenli olarak Excel'e aktarıp saklayın
- **Karşılaştırma**: Farklı haftaları karşılaştırın

## Sorun Giderme

### Program Açılmıyor
```
HATA: Python bulunamadı!
```
**Çözüm**: Python'u PATH'e ekleyin veya yeniden kurun

### PyQt6 Hatası
```
ModuleNotFoundError: No module named 'PyQt6'
```
**Çözüm**:
```cmd
pip install PyQt6
```

### Veritabanı Hatası
```
database is locked
```
**Çözüm**: Programın sadece bir örneğini çalıştırın

### Resim Gösterilmiyor
- Resim dosyasının var olduğundan emin olun
- Desteklenen formatta olduğunu kontrol edin
- `vehicle_images/` klasörüne erişim izniniz olduğunu kontrol edin

### Excel Export Hatası
```
ModuleNotFoundError: No module named 'openpyxl'
```
**Çözüm**:
```cmd
pip install openpyxl pandas
```

## Yedekleme

### Manuel Yedekleme
Düzenli olarak şu dosyaları yedekleyin:
- `vehicle_qualification.db` (veritabanı)
- `vehicle_images/` klasörü (araç resimleri)

### Otomatik Yedekleme
Windows Task Scheduler ile otomatik yedekleme ayarlayabilirsiniz:

```cmd
xcopy vehicle_qualification.db "D:\Yedek\" /Y
xcopy vehicle_images "D:\Yedek\vehicle_images\" /E /I /Y
```

## Sık Sorulan Sorular (SSS)

**S: Kaç araç ekleyebilirim?**
C: Sınır yok. Veritabanı binlerce aracı destekler.

**S: Günlük girdiyi düzenleyebilir miyim?**
C: Evet, ancak şu anda GUI'de düzenleme özelliği yok. Veritabanı düzeyinde mümkün.

**S: Eski haftaların raporlarını alabilir miyim?**
C: Evet, Raporlar sekmesinde hafta seçebilirsiniz (son 4 hafta).

**S: Birden fazla bilgisayarda kullanabilir miyim?**
C: Evet, veritabanı ve resim klasörünü kopyalayın.

**S: SORT test sistemi ile entegre mi?**
C: Hayır, bu bağımsız bir sistem. İsterseniz entegre edilebilir.

## Gelecek Özellikler (Planlanan)

- [ ] Girdi düzenleme özelliği
- [ ] Grafik ve istatistik gösterimleri
- [ ] Özel tarih aralığı raporları
- [ ] PDF export
- [ ] Araç karşılaştırma
- [ ] E-posta rapor gönderimi
- [ ] Otomatik yedekleme
- [ ] Kullanıcı yetkilendirme

## Destek

Sorularınız için:
- **GitHub Issues**: Proje repository'sinde issue açın
- **E-posta**: support@example.com

## Lisans

Bu proje özel bir proje olup, tüm hakları saklıdır.

## Sürüm Geçmişi

### v1.0.0 (2024-11-22)
- ✅ İlk sürüm
- ✅ Araç kaydı (resim + özellikler)
- ✅ Günlük girdiler
- ✅ Görsel dashboard
- ✅ Araç listesi
- ✅ Haftalık raporlar
- ✅ Excel export

---

**Not**: Bu sistem, mevcut SORT Test Otomasyon Sistemi'nden bağımsız olarak çalışır. İsterseniz iki sistemi birlikte kullanabilirsiniz.
