# 🏠 Windows 11 Kişisel Asistan Uygulaması

Modern ve kapsamlı bir kişisel asistan masaüstü uygulaması. Not alma, hatırlatmalar, görev yönetimi, Pomodoro timer ve Outlook takvim entegrasyonu özellikleri sunar.

![Windows 11](https://img.shields.io/badge/Windows-11-0078D4?style=flat&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt-41CD52?style=flat&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Özellikler

### 📝 Not Alma ve Hatırlatma Sistemi
- **Kapsamlı Not Yönetimi**: Başlık, içerik, kategori ve öncelik seviyesi ile notlar
- **Akıllı Hatırlatmalar**: Her not için özel tarih ve saat ayarlama
- **Tekrarlayan Hatırlatmalar**: Günlük, haftalık, aylık periyotlar
- **Kategori Sistemi**: İş, Kişisel, Alışveriş, Sağlık, Eğitim, Genel
- **Öncelik Seviyeleri**: Düşük (🔵), Orta (⚪), Yüksek (🟡), Acil (🔴)
- **Güçlü Arama**: Not başlığı ve içeriğinde tam metin arama
- **Filtreleme**: Kategoriye göre notları filtrele

### ✅ Görev Yönetimi (To-Do List)
- **Görev Takibi**: Detaylı görev oluşturma ve düzenleme
- **Durum Yönetimi**: Beklemede, Devam Ediyor, Tamamlandı, İptal Edildi
- **Termin Tarihleri**: Her görev için son tarih belirleme
- **Süre Tahmini**: Görevler için tahmini çalışma süresi
- **İlerleme Takibi**: Görsel progress bar ile tamamlanma oranı
- **İstatistikler**: Günlük, haftalık ve aylık görev istatistikleri

### 🍅 Pomodoro Timer
- **Özelleştirilebilir Süreler**: Çalışma, kısa mola ve uzun mola süreleri
- **Otomatik Geçişler**: Çalışma oturumları arasında otomatik mola
- **Oturum Takibi**: Günlük tamamlanan oturum sayısı
- **Duraklat/Devam**: Esnek timer kontrolü
- **Bildirimler**: Her oturum sonunda sesli/görsel bildirim
- **İstatistikler**: Günlük ve haftalık verimlilik raporları

### 📅 Outlook Takvim Entegrasyonu
- **Microsoft Graph API**: Modern OAuth 2.0 kimlik doğrulama
- **Otomatik Senkronizasyon**: Ayarlanabilir senkronizasyon aralığı
- **Yaklaşan Etkinlikler**: 24 saat önceden otomatik bildirimler
- **Detaylı Bilgiler**: Konu, katılımcılar, yer, süre
- **Çevrimdışı Destek**: Yerel önbellekleme
- **Birden Fazla Takvim**: Tüm Outlook takvimlerini destekler

### 🎨 Modern UI/UX
- **Fluent Design**: Windows 11 tasarım diline uygun
- **Tema Desteği**: Açık ve koyu tema seçenekleri
- **Sistem Tepsisi**: Arka planda çalışma ve hızlı erişim
- **Klavye Kısayolları**: Hızlı işlemler için kısayollar
- **Responsive Tasarım**: Esnek ve yeniden boyutlandırılabilir arayüz
- **Görsel Geri Bildirimler**: Renkli ikonlar ve durum göstergeleri

### 💾 Veri Yönetimi
- **SQLite Veritabanı**: Hızlı ve güvenilir yerel depolama
- **Yedekleme**: JSON formatında veri dışa aktarma
- **Geri Yükleme**: Yedekten tam veri geri yükleme
- **Veri Temizleme**: Güvenli toplu veri silme

## 🚀 Kurulum

### Gereksinimler

- **Python 3.8 veya üzeri**
- **Windows 10/11** (Windows bildirimleri için)
- **Outlook hesabı** (takvim entegrasyonu için, opsiyonel)

### Adım 1: Depoyu Klonlayın

```bash
git clone <repository-url>
cd windows-assistant
```

### Adım 2: Sanal Ortam Oluşturun (Önerilen)

```bash
python -m venv venv
venv\Scripts\activate
```

### Adım 3: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### Adım 4: Uygulamayı Çalıştırın

```bash
python src/main.py
```

## 📖 Kullanım Kılavuzu

### İlk Kurulum

1. **Uygulamayı Başlatın**: `python src/main.py` komutu ile uygulamayı başlatın
2. **İlk Not**: Notlar sekmesinden ilk notunuzu oluşturun
3. **Hatırlatma Ekleyin**: Nota hatırlatma ekleyerek bildirimleri test edin
4. **Ayarları Düzenleyin**: Tema, bildirim ve Pomodoro ayarlarını özelleştirin

### Not Ekleme

1. **Notlar** sekmesine gidin
2. **➕ Yeni Not** butonuna tıklayın
3. Başlık, içerik, kategori ve öncelik bilgilerini girin
4. **Hatırlatma eklemek için**:
   - "Hatırlatma Ekle" seçeneğini "Evet" yapın
   - Tarih ve saat seçin
   - İsterseniz tekrar ayarları yapın
5. **💾 Kaydet** butonuna tıklayın

### Görev Oluşturma

1. **Görevler** sekmesine gidin
2. **➕ Yeni Görev** butonuna tıklayın
3. Görev detaylarını doldurun:
   - Başlık ve açıklama
   - Kategori ve öncelik
   - Termin tarihi (opsiyonel)
   - Tahmini süre (opsiyonel)
4. **💾 Kaydet** butonuna tıklayın

### Pomodoro Kullanımı

1. **Pomodoro** sekmesine gidin
2. Ayarlar sekmesinden süreleri özelleştirin (opsiyonel)
3. **🍅 Çalışma Başlat** butonuna tıklayın
4. Odaklanın ve çalışın!
5. Süre dolunca otomatik bildirim alacaksınız
6. **☕ Kısa Mola** veya **🎉 Uzun Mola** başlatın
7. İstatistiklerinizi takip edin

### Outlook Entegrasyonu

#### Azure AD Uygulama Kaydı

Outlook entegrasyonu için Microsoft Graph API kullanılır. Şu adımları izleyin:

1. **Azure Portal'a gidin**: https://portal.azure.com
2. **Azure Active Directory** > **App registrations** > **New registration**
3. **Uygulama Bilgileri**:
   - Name: "Personal Assistant"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:8000/auth/callback` (Web)
4. **Client ID'yi kaydedin**
5. **Certificates & secrets** > **New client secret** > Secret'i kaydedin
6. **API permissions** > **Add a permission**:
   - Microsoft Graph > Delegated permissions
   - `Calendars.Read`
   - `Calendars.Read.Shared`
   - `User.Read`
7. **Grant admin consent** (eğer kurumsal hesap kullanıyorsanız)

#### Uygulamada Kullanım

1. **Takvim** sekmesine gidin
2. **🔗 Outlook'a Bağlan** butonuna tıklayın
3. Microsoft hesabınızla giriş yapın
4. İzinleri onaylayın
5. **🔄 Senkronize Et** ile takvim etkinliklerini çekin

**Not**: Şu anda demo modunda çalışmaktadır. Gerçek entegrasyon için yukarıdaki Azure AD adımlarını tamamlayın ve `src/services/outlook_service.py` dosyasındaki OAuth implementasyonunu etkinleştirin.

### Sistem Tepsisi

- **Minimize**: Pencereyi kapatınca sistem tepsisinde arka planda çalışmaya devam eder
- **Çift Tıklama**: Sistem tepsisi ikonuna çift tıklayarak pencereyi açın
- **Sağ Tık Menüsü**:
  - 🏠 Pencereyi Göster
  - 📝 Hızlı Not
  - 🚪 Çıkış

### Veri Yedekleme

#### Dışa Aktarma

1. **Ayarlar** sekmesine gidin
2. **📤 Verileri Dışa Aktar** butonuna tıklayın
3. Dosya konumunu seçin
4. Tüm notlar, görevler ve ayarlar JSON dosyasına kaydedilir

#### İçe Aktarma

1. **Ayarlar** sekmesine gidin
2. **📥 Verileri İçe Aktar** butonuna tıklayın
3. Yedek JSON dosyasını seçin
4. Onaylayın (mevcut veriler silinecektir!)

## 🗂️ Proje Yapısı

```
windows-assistant/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Ana uygulama giriş noktası
│   ├── models/                 # Veritabanı modelleri
│   │   ├── __init__.py
│   │   └── database.py         # SQLite şeması ve modeller
│   ├── services/               # İş mantığı servisleri
│   │   ├── __init__.py
│   │   ├── reminder_service.py # Hatırlatma servisi
│   │   ├── notification_service.py # Bildirim servisi
│   │   ├── outlook_service.py  # Outlook entegrasyonu
│   │   └── pomodoro_service.py # Pomodoro timer servisi
│   ├── ui/                     # Kullanıcı arayüzü
│   │   ├── __init__.py
│   │   ├── main_window.py      # Ana pencere
│   │   ├── notes_tab.py        # Notlar sekmesi
│   │   ├── tasks_tab.py        # Görevler sekmesi
│   │   ├── pomodoro_tab.py     # Pomodoro sekmesi
│   │   ├── calendar_tab.py     # Takvim sekmesi
│   │   ├── settings_tab.py     # Ayarlar sekmesi
│   │   └── system_tray.py      # Sistem tepsisi
│   └── utils/                  # Yardımcı fonksiyonlar
│       └── __init__.py
├── data/                       # Veritabanı dosyaları (otomatik oluşur)
│   └── assistant.db
├── resources/                  # Kaynaklar
│   ├── icons/                  # İkonlar
│   └── themes/                 # Temalar
├── docs/                       # Dokümantasyon
├── tests/                      # Testler
├── requirements.txt            # Python bağımlılıkları
└── README.md                   # Bu dosya
```

## 🗄️ Veritabanı Şeması

### Notes (Notlar)
- `id`: Benzersiz kimlik
- `title`: Not başlığı
- `content`: Not içeriği
- `category`: Kategori
- `priority`: Öncelik (1-4)
- `created_at`: Oluşturulma tarihi
- `updated_at`: Güncellenme tarihi
- `is_deleted`: Silindi mi (soft delete)
- `tags`: Etiketler (JSON)

### Reminders (Hatırlatmalar)
- `id`: Benzersiz kimlik
- `note_id`: İlişkili not
- `reminder_time`: Hatırlatma zamanı
- `is_completed`: Tamamlandı mı
- `is_snoozed`: Ertelendi mi
- `snooze_until`: Erteleme zamanı
- `recurrence_type`: Tekrar tipi (daily, weekly, monthly)
- `recurrence_interval`: Tekrar aralığı
- `last_triggered`: Son tetiklenme

### Tasks (Görevler)
- `id`: Benzersiz kimlik
- `title`: Görev başlığı
- `description`: Açıklama
- `category`: Kategori
- `priority`: Öncelik (1-4)
- `status`: Durum (pending, in_progress, completed, cancelled)
- `due_date`: Termin tarihi
- `completed_at`: Tamamlanma tarihi
- `estimated_minutes`: Tahmini süre
- `actual_minutes`: Gerçek süre

### Calendar Events (Takvim Etkinlikleri)
- `id`: Benzersiz kimlik
- `event_id`: Outlook event ID
- `subject`: Konu
- `start_time`: Başlangıç
- `end_time`: Bitiş
- `location`: Yer
- `attendees`: Katılımcılar
- `notification_sent`: Bildirim gönderildi mi

### Pomodoro Sessions
- `id`: Benzersiz kimlik
- `task_id`: İlişkili görev
- `start_time`: Başlangıç
- `end_time`: Bitiş
- `duration_minutes`: Süre
- `is_completed`: Tamamlandı mı
- `session_type`: Oturum tipi (work, short_break, long_break)

## ⚙️ Ayarlar

### Görünüm
- **Tema**: Açık / Koyu

### Bildirimler
- **Bildirimleri Etkinleştir**: Tüm bildirimleri aç/kapat
- **Bildirim Sesi**: Sesli bildirimler

### Outlook
- **Otomatik Senkronizasyon**: Arka planda otomatik senkronizasyon
- **Senkronizasyon Aralığı**: 5-120 dakika arası

### Pomodoro
- **Çalışma Süresi**: 1-60 dakika (varsayılan: 25)
- **Kısa Mola**: 1-30 dakika (varsayılan: 5)
- **Uzun Mola**: 5-60 dakika (varsayılan: 15)
- **Uzun Molaya Kadar**: 2-10 oturum (varsayılan: 4)

### Başlangıç
- **Windows ile Başlat**: Sistem başlangıcında otomatik çalıştır
- **Sistem Tepsisine Küçült**: Kapatınca arka planda çalış

## 🔧 Geliştirme

### Test Çalıştırma

```bash
# Test paketlerini yükleyin
pip install pytest pytest-qt

# Testleri çalıştırın
pytest tests/
```

### Kod Formatı

```bash
# Black ile format
pip install black
black src/

# Flake8 ile lint
pip install flake8
flake8 src/
```

## 🐛 Bilinen Sorunlar ve Çözümler

### Windows Bildirimleri Çalışmıyor

**Sorun**: Bildirimler görünmüyor
**Çözüm**:
1. Windows Ayarlar > Sistem > Bildirimler ve eylemler
2. "Uygulama ve diğer gönderenlerden bildirim al" açık olmalı
3. Python'un bildirim izni olmalı

### Outlook Bağlantı Hatası

**Sorun**: Outlook'a bağlanılamıyor
**Çözüm**:
1. Azure AD uygulama kaydının doğru yapıldığından emin olun
2. Client ID ve Secret'ın doğru olduğunu kontrol edin
3. Redirect URI'ın eşleştiğinden emin olun
4. İnternet bağlantınızı kontrol edin

### Veritabanı Kilitleme Hatası

**Sorun**: "Database is locked" hatası
**Çözüm**:
1. Uygulamadan tamamen çıkın
2. `data/assistant.db-journal` dosyasını silin (varsa)
3. Uygulamayı yeniden başlatın

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 👥 İletişim

Sorularınız, önerileriniz veya geri bildirimleriniz için:
- Issue açın: [GitHub Issues](https://github.com/yourusername/windows-assistant/issues)
- E-posta: your.email@example.com

## 🙏 Teşekkürler

- **PySide6/Qt**: Muhteşem GUI framework'ü için
- **Microsoft Graph API**: Outlook entegrasyonu için
- **Python Community**: Harika kütüphaneler ve araçlar için

## 📚 Ek Kaynaklar

- [PySide6 Dokümantasyonu](https://doc.qt.io/qtforpython/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
- [SQLite Dokümantasyonu](https://www.sqlite.org/docs.html)
- [Windows Toast Notifications](https://docs.microsoft.com/en-us/windows/apps/design/shell/tiles-and-notifications/)

---

**⭐ Beğendiyseniz yıldız vermeyi unutmayın!**

Keyifli kullanımlar! 🚀
