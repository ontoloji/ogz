# Wealth Tracker - Finansal Birikim Takip Uygulaması

Finansal birikimlerinizi (değerli madenler, döviz, vadeli yatırımlar) takip edebileceğiniz, çapraz platform destekli masaüstü uygulaması.

## Özellikler

✅ **Cross-Platform**: Windows ve macOS'ta çalışır
✅ **Güvenli Giriş**: Şifreli kullanıcı hesapları
✅ **Çoklu Varlık Desteği**: Değerli maden, döviz, vadeli yatırım
✅ **Online Fiyat Güncellemesi**: Gerçek zamanlı değerleme
✅ **Portföy Özeti**: Toplam değer hesaplama
✅ **Kolay Kullanım**: Sezgisel arayüz

## Desteklenen Varlık Tipleri

### 💰 Değerli Madenler
- Altın (gram)
- Gümüş (gram)
- Platin
- Paladyum

### 💵 Dövizler
- Dolar (USD)
- Euro (EUR)
- Pound/Sterlin (GBP)

### 📊 Vadeli Yatırımlar
- Mevduat
- Tahvil
- Bono
- Diğer

## Kurulum

### Gereksinimler
- Python 3.7 veya üzeri
- pip (Python paket yöneticisi)

### Windows'ta Kurulum

1. Python'u yükleyin (eğer yoksa): https://www.python.org/downloads/
2. Komut istemcisini açın ve şu komutları çalıştırın:

```cmd
cd wealth_tracker
pip install -r requirements.txt
python main.py
```

### macOS'ta Kurulum

1. Terminal'i açın
2. Python'un yüklü olduğunu kontrol edin:

```bash
python3 --version
```

3. Uygulamayı çalıştırın:

```bash
cd wealth_tracker
pip3 install -r requirements.txt
python3 main.py
```

## Kullanım

### İlk Kullanım

1. **Uygulamayı Başlatın**: `python main.py` komutu ile
2. **Yeni Kullanıcı Oluşturun**:
   - "Yeni Kullanıcı" butonuna tıklayın
   - Kullanıcı adı ve şifre belirleyin (en az 4 karakter)
   - Kaydedin
3. **Giriş Yapın**: Oluşturduğunuz kullanıcı adı ve şifre ile giriş yapın

### Birikim Ekleme

1. Ana ekranda **"Yeni Birikim Ekle"** butonuna tıklayın
2. Gerekli bilgileri doldurun:
   - **Varlık Tipi**: Değerli Maden, Döviz veya Vadeli Yatırım
   - **Varlık Adı**: Altın, Dolar, vb.
   - **Miktar**: Sahip olduğunuz miktar (örn: 50 gram altın)
   - **Alış Fiyatı**: Birim başına ödediğiniz fiyat (TL)
   - **Alış Tarihi**: Satın alma tarihi
   - **Notlar**: İsteğe bağlı notlar
3. **"Kaydet"** butonuna tıklayın

### Fiyat Güncelleme

- **"Fiyatları Güncelle"** butonuna tıklayarak güncel piyasa fiyatlarını çekin
- Sistem otomatik olarak:
  - Altın ve gümüş fiyatlarını
  - Döviz kurlarını
  - Toplam portföy değerinizi hesaplar

### Kayıt Silme

1. Tablodan silmek istediğiniz kaydı seçin
2. **"Seçili Kaydı Sil"** butonuna tıklayın
3. Onaylayın

## Veri Güvenliği

- 🔒 Şifreler SHA-256 ile hash'lenerek saklanır
- 💾 Tüm veriler yerel SQLite veritabanında tutulur
- 📁 Veritabanı dosyası: `wealth_tracker.db`

## Fiyat Kaynakları

Uygulama aşağıdaki kaynaklardan gerçek zamanlı fiyat bilgisi çeker:

- **Döviz Kurları**: exchangerate-api.com (ücretsiz API)
- **Değerli Madenler**: Yapılandırılabilir API (varsayılan örnek değerler)

> **Not**: Üretim kullanımı için, `price_fetcher.py` dosyasında geçerli bir altın/gümüş API anahtarı yapılandırmanız önerilir (örn: metals-api.com, metalpriceapi.com)

## Proje Yapısı

```
wealth_tracker/
├── main.py              # Ana uygulama ve GUI
├── database.py          # Veritabanı yönetimi
├── price_fetcher.py     # Online fiyat servisi
├── requirements.txt     # Python bağımlılıkları
├── README.md           # Bu dosya
└── wealth_tracker.db   # Veritabanı (otomatik oluşur)
```

## Teknik Detaylar

- **GUI Framework**: tkinter (Python standart kütüphanesi)
- **Veritabanı**: SQLite3
- **HTTP İstekleri**: requests
- **Şifreleme**: hashlib (SHA-256)

## Sorun Giderme

### Windows'ta "python komutu tanınmıyor" hatası
- Python'u PATH'e eklemeyi unutmuş olabilirsiniz
- Python kurulumunu yeniden yapın ve "Add Python to PATH" seçeneğini işaretleyin

### macOS'ta "tkinter bulunamadı" hatası
```bash
brew install python-tk
```

### Internet bağlantısı yoksa
- Uygulama çalışmaya devam eder
- Fiyatlar güncellenemez, son bilinen değerler kullanılır
- Vadeli yatırımlar için alış fiyatınız kullanılır

## Geliştirme Önerileri

### API Anahtarı Yapılandırması
Üretim kullanımı için `price_fetcher.py` dosyasında API anahtarlarınızı güncelleyin:

```python
# Altın/Gümüş için
url = "https://api.metalpriceapi.com/v1/latest"
params = {
    "api_key": "BURAYA_API_ANAHTARINIZ",
    "base": "XAU",
    "currencies": currency
}
```

### Ek Özellikler
- Grafik ve raporlama
- Excel'e aktarma
- Otomatik yedekleme
- Çoklu para birimi desteği
- Mobil uygulama

## Lisans

Bu proje eğitim ve kişisel kullanım içindir.

## Destek

Sorularınız için GitHub Issues kullanabilirsiniz.

---

**Geliştirici**: Wealth Tracker Ekibi
**Versiyon**: 1.0.0
**Son Güncelleme**: 2025
