# Test Ekipmanı Rezervasyon ve Takip Sistemi

Modern, web tabanlı test ekipmanı rezervasyon ve yönetim sistemi. Flask framework kullanılarak geliştirilmiştir.

## Özellikler

### ✨ Ana Özellikler

- **Ekipman Yönetimi**
  - Detaylı ekipman bilgileri (isim, tip, model, seri no, lokasyon)
  - Ekipman durumu takibi (müsait, kullanımda, bakımda, arızalı)
  - Ekipman kategorileri (Kvaser, Osiloskop, Güç Kaynağı, vb.)
  - Ekipman arama ve filtreleme

- **Rezervasyon Sistemi**
  - Kolay rezervasyon oluşturma
  - Otomatik çakışma kontrolü
  - Rezervasyon durumu takibi (beklemede, onaylandı, tamamlandı, iptal edildi)
  - Rezervasyon geçmişi

- **Takvim Görünümü**
  - Interaktif FullCalendar entegrasyonu
  - Ay, hafta ve gün görünümleri
  - Renkli rezervasyon gösterimi
  - Detaylı rezervasyon bilgileri

- **Bakım ve Kalibrasyon Takibi**
  - Bakım geçmişi kayıtları
  - Kalibrasyon tarihleri
  - Otomatik kalibrasyon hatırlatıcıları
  - Bakım maliyeti takibi

- **E-posta Bildirimleri**
  - Rezervasyon onay bildirimleri
  - Rezervasyon iptal bildirimleri
  - Kalibrasyon hatırlatıcıları
  - HTML formatında profesyonel e-postalar

- **İstatistikler ve Raporlama**
  - Ekipman durumu grafikleri
  - Kullanım istatistikleri
  - En çok kullanılan ekipmanlar
  - Toplam bakım maliyetleri

- **Kullanıcı Yönetimi**
  - Çoklu kullanıcı desteği
  - Rol tabanlı yetkilendirme (Admin, Yönetici, Kullanıcı)
  - Güvenli kimlik doğrulama
  - Kullanıcı profil yönetimi

- **Mobil Uyumlu Arayüz**
  - Bootstrap 5 responsive tasarım
  - Tüm cihazlarda sorunsuz çalışma
  - Modern ve kullanıcı dostu arayüz

## Teknolojiler

- **Backend:** Flask 3.0
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** Bootstrap 5, jQuery
- **Takvim:** FullCalendar
- **Grafikler:** Chart.js
- **Kimlik Doğrulama:** Flask-Login
- **E-posta:** Flask-Mail

## Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adım 1: Bağımlılıkları Yükleyin

```bash
cd equipment_reservation
pip install -r requirements.txt
```

### Adım 2: Çevre Değişkenlerini Yapılandırın

`.env.example` dosyasını `.env` olarak kopyalayın ve düzenleyin:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///equipment_reservation.db

# E-posta ayarları (opsiyonel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Adım 3: Veritabanını Başlatın

```bash
flask init-db
```

### Adım 4: Örnek Verileri Yükleyin (Opsiyonel)

```bash
flask seed-db
```

Bu komut şu örnek kullanıcıları oluşturur:
- **Admin:** Kullanıcı adı: `admin`, Şifre: `admin123`
- **Kullanıcı:** Kullanıcı adı: `user`, Şifre: `user123`

### Adım 5: Uygulamayı Başlatın

```bash
python app.py
```

veya

```bash
flask run
```

Uygulama `http://localhost:5000` adresinde çalışmaya başlayacaktır.

## Kullanım

### İlk Giriş

1. Tarayıcınızda `http://localhost:5000` adresine gidin
2. Örnek verilerle giriş yapın:
   - Admin: `admin` / `admin123`
   - Kullanıcı: `user` / `user123`
3. Veya yeni bir hesap oluşturun

### Temel İşlemler

#### Ekipman Ekleme (Yönetici/Admin)

1. "Yönetim" menüsünden "Ekipman Ekle"yi seçin
2. Ekipman bilgilerini girin
3. "Ekle" butonuna tıklayın

#### Rezervasyon Yapma

1. "Ekipmanlar" sayfasından istediğiniz ekipmanı seçin
2. "Rezervasyon Yap" butonuna tıklayın
3. Tarih, saat ve kullanım amacını girin
4. "Rezervasyon Oluştur" butonuna tıklayın

#### Bakım Kaydı Ekleme (Yönetici/Admin)

1. Ekipman detay sayfasından "Bakım Ekle"yi seçin
2. Bakım bilgilerini girin
3. "Kaydet" butonuna tıklayın

#### İstatistikleri Görüntüleme (Yönetici/Admin)

1. "Yönetim" menüsünden "İstatistikler"i seçin
2. Grafikleri ve raporları inceleyin

## Proje Yapısı

```
equipment_reservation/
├── app.py                      # Ana uygulama dosyası
├── config.py                   # Konfigürasyon ayarları
├── email_utils.py             # E-posta yardımcı fonksiyonları
├── requirements.txt           # Python bağımlılıkları
├── .env.example              # Örnek çevre değişkenleri
├── models/
│   └── __init__.py           # Veritabanı modelleri
├── templates/                 # HTML şablonları
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── equipment_list.html
│   ├── equipment_detail.html
│   ├── equipment_form.html
│   ├── reserve_equipment.html
│   ├── reservation_list.html
│   ├── calendar.html
│   ├── maintenance_form.html
│   ├── statistics.html
│   ├── user_list.html
│   └── user_form.html
└── static/                    # Statik dosyalar
    ├── css/
    │   └── style.css
    └── js/
```

## Veritabanı Modelleri

### User (Kullanıcı)
- Kullanıcı bilgileri ve kimlik doğrulama
- Roller: user, manager, admin

### Equipment (Ekipman)
- Ekipman bilgileri
- Durum takibi
- Kalibrasyon bilgileri

### Reservation (Rezervasyon)
- Rezervasyon detayları
- Çakışma kontrolü
- Durum takibi

### MaintenanceRecord (Bakım Kaydı)
- Bakım geçmişi
- Maliyet takibi
- Kalibrasyon kayıtları

### Notification (Bildirim)
- E-posta bildirimleri
- Sistem bildirimleri

## Güvenlik

- Şifre hashleme (Werkzeug)
- CSRF koruması (Flask-WTF)
- Session yönetimi (Flask-Login)
- SQL injection koruması (SQLAlchemy ORM)

## Özelleştirme

### E-posta Şablonları

E-posta şablonlarını `email_utils.py` dosyasında özelleştirebilirsiniz.

### Tema ve Stil

CSS stillerini `static/css/style.css` dosyasında değiştirebilirsiniz.

### Ekipman Kategorileri

Yeni ekipman kategorileri `equipment_form.html` dosyasındaki datalist'e eklenebilir.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Destek

Sorularınız veya önerileriniz için issue açabilirsiniz.

## Geliştirme Planı

- [ ] PDF rapor oluşturma
- [ ] Excel export
- [ ] QR kod etiketleme
- [ ] Mobil uygulama
- [ ] REST API
- [ ] Çoklu dil desteği
- [ ] Advanced arama ve filtreleme
- [ ] Otomatik yedekleme

## Ekran Görüntüleri

### Ana Sayfa
- Dashboard görünümü
- Hızlı istatistikler
- Son rezervasyonlar

### Ekipman Listesi
- Filtreleme seçenekleri
- Durum göstergeleri
- Hızlı rezervasyon

### Takvim Görünümü
- İnteraktif takvim
- Renkli gösterimler
- Detaylı bilgiler

### İstatistikler
- Grafikler
- Raporlar
- Kalibrasyon uyarıları
