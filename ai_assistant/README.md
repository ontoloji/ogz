# 🤖 Windows AI Kişisel Asistan

Modern, hafif ve Türkçe destekli yapay zeka kişisel asistan uygulaması.

## ✨ Özellikler

- 🎯 **System Tray Entegrasyonu**: Sistem tepsisinde sessizce çalışır
- ⌨️ **Global Hotkey**: `Ctrl+Shift+A` ile hızlıca erişim
- 🧠 **Doğal Dil Anlama**: Türkçe komutları anlar ve işler
- 📝 **Not Alma**: Hızlıca not alın ve saklayın
- ⏰ **Hatırlatıcı Sistemi**: Zamanlı hatırlatmalar oluşturun
- 🔍 **Dosya Arama**: Bilgisayarınızda hızlı dosya araması
- 🔢 **Hesaplama**: Basit matematiksel hesaplamalar
- 🌐 **Web Araması**: Doğrudan Google araması yapın
- 🚀 **Uygulama Başlatma**: Sık kullandığınız uygulamaları açın
- 🤖 **Otomasyon**: Zamanlanmış görevler ve bildirimler
- 🔒 **Gizlilik**: Tüm veriler lokal olarak saklanır
- 💨 **Hafif**: Düşük sistem kaynağı kullanımı

## 📋 Gereksinimler

- Windows 10/11
- Python 3.8 veya üzeri

## 🚀 Kurulum

1. **Repository'yi klonlayın veya indirin:**
```bash
git clone <repository-url>
cd ai_assistant
```

2. **Gerekli kütüphaneleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı başlatın:**
```bash
python main.py
```

## 🎮 Kullanım

### Temel Komutlar

#### 📝 Not Alma
```
"proje fikirleri diye not al"
"alışveriş listesi not ekle"
"toplantı notları kaydet"
```

#### ⏰ Hatırlatıcı
```
"yarın saat 10'da toplantı hatırlat"
"bugün 15:30'da randevu hatırlat"
"30 dakika sonra çay hatırlat"
"2 saat sonra mola hatırlat"
```

#### 🔢 Hesaplama
```
"15 çarpı 8 kaç"
"100 eksi 25"
"50 artı 30"
"120 böl 4"
```

#### 🔍 Dosya Arama
```
"python dosyalarını ara"
"rapor.pdf dosya ara"
"proje dosyalarını bul"
```

#### 🌐 Web Araması
```
"python nedir ara"
"yapay zeka google'da ara"
"hava durumu ankara search"
```

#### 🚀 Uygulama Açma
```
"chrome aç"
"notepad başlat"
"calculator çalıştır"
"word aç"
```

### Global Hotkey

- `Ctrl+Shift+A`: Asistan penceresini aç/kapat

### System Tray

Sistem tepsisindeki icon'a sağ tıklayarak:
- Asistanı Aç
- Hatırlatıcıları Görüntüle
- Notları Görüntüle
- Çıkış

## 📁 Proje Yapısı

```
ai_assistant/
│
├── main.py              # Ana uygulama dosyası
├── database.py          # SQLite veritabanı yönetimi
├── nlp_processor.py     # Doğal dil işleme ve komut yorumlama
├── automation.py        # Otomasyon ve hatırlatıcı sistemi
├── file_search.py       # Dosya arama modülü
├── requirements.txt     # Gerekli Python kütüphaneleri
└── README.md           # Bu dosya
```

## 🗄️ Veri Depolama

Tüm veriler lokal olarak saklanır:
- Konum: `%USERPROFILE%\.ai_assistant\assistant.db`
- Format: SQLite veritabanı
- İçerik: Notlar, hatırlatıcılar, komut geçmişi, favori uygulamalar

## 🔧 Özelleştirme

### Arama Dizinlerini Değiştirme

`file_search.py` dosyasındaki `search_paths` listesini düzenleyin:

```python
self.search_paths = [
    Path.home() / 'Desktop',
    Path.home() / 'Documents',
    Path.home() / 'Downloads',
    # Kendi dizinlerinizi ekleyin
    Path('D:/Projeler'),
]
```

### Yeni Uygulama Kısayolları Ekleme

`nlp_processor.py` dosyasındaki `common_apps` sözlüğünü düzenleyin:

```python
self.common_apps = {
    'vscode': 'code.exe',
    'spotify': 'spotify.exe',
    # Kendi uygulamalarınızı ekleyin
}
```

### Hotkey'i Değiştirme

`main.py` dosyasındaki `setup_hotkey` fonksiyonunu düzenleyin:

```python
keyboard.add_hotkey('ctrl+alt+a', self.show_assistant_window)  # Yeni hotkey
```

## 🐛 Bilinen Sorunlar ve Çözümler

### Keyboard Modülü Yönetici İzni Gerektiriyor

Bazı durumlarda global hotkey çalışması için uygulamanın yönetici olarak çalıştırılması gerekebilir.

**Çözüm:**
```bash
# PowerShell'i yönetici olarak açın
python main.py
```

### Toast Notifications Çalışmıyor

`win10toast` kütüphanesi opsiyoneldir. Yüklü değilse sadece MessageBox gösterilir.

**Çözüm:**
```bash
pip install win10toast
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/YeniOzellik`)
5. Pull Request oluşturun

## 📝 Geliştirme Notları

### Gelecek Özellikler

- [ ] OpenAI/GPT entegrasyonu (opsiyonel)
- [ ] Outlook takvim entegrasyonu
- [ ] Pomodoro zamanlayıcı
- [ ] Ekran görüntüsü alma ve OCR
- [ ] Sesli komut desteği
- [ ] Tema seçenekleri (koyu/açık mod)
- [ ] Çoklu dil desteği
- [ ] Cloud senkronizasyonu (opsiyonel)

### Performans İpuçları

- Dosya araması ilk çalıştırmada yavaş olabilir
- Derin dizin aramalarını sınırlamak için `max_depth` ayarını düşürün
- Veritabanı düzenli olarak temizlenmeli (eski komut geçmişi)

## 📄 Lisans

Bu proje açık kaynak kodludur ve serbestçe kullanılabilir.

## 🙏 Teşekkürler

Bu proje aşağıdaki harika kütüphaneler sayesinde mümkün oldu:
- [pystray](https://github.com/moses-palmer/pystray) - System tray ikonu için
- [keyboard](https://github.com/boppreh/keyboard) - Global hotkey için
- [Pillow](https://python-pillow.org/) - Görsel işleme için
- [python-dateutil](https://github.com/dateutil/dateutil) - Tarih/saat işlemleri için

## 📧 İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

**Not**: Bu uygulama Windows işletim sistemi için tasarlanmıştır. Linux ve macOS desteği gelecek sürümlerde eklenebilir.
