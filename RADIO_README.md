# 🎵 Internet Radyo Çalar

Windows tabanlı, modern ve kullanıcı dostu internet radyo çalar uygulaması. URL girerek dünyanın her yerinden radyo istasyonlarını dinleyebilirsiniz.

## ✨ Özellikler

- **🌐 Internet Radyo Desteği**: HTTP/HTTPS akış protokolleri
- **🎚️ 10 Bantlı Equalizer**: Profesyonel ses ayarlama
- **⭐ Favoriler Sistemi**: En sevdiğiniz istasyonları kaydedin
- **🎛️ Ses Kontrolü**: Hassas ses seviyesi ayarı
- **💻 Modern Arayüz**: PyQt5 tabanlı şık ve kullanışlı tasarım
- **📻 VLC Backend**: Güçlü ve güvenilir medya oynatma

## 📋 Sistem Gereksinimleri

### Yazılım Gereksinimleri
- **Windows 10/11** (64-bit önerilir)
- **Python 3.8+**
- **VLC Media Player** (Zorunlu)

### Python Paketleri
- PyQt5 >= 5.15.0
- python-vlc >= 3.0.0

## 🚀 Kurulum

### 1. VLC Media Player Kurulumu (Zorunlu)

VLC, uygulamanın çalışması için gereklidir:

1. [VLC İndirme Sayfası](https://www.videolan.org/vlc/)
2. Windows için en son sürümü indirin
3. Kurulum sihirbazını takip edin
4. Varsayılan ayarlarla kurun

### 2. Python Bağımlılıklarını Yükleyin

```bash
pip install -r radio_requirements.txt
```

Veya manuel olarak:

```bash
pip install PyQt5>=5.15.0 python-vlc>=3.0.0
```

## 🎮 Kullanım

### Uygulamayı Başlatma

```bash
python internet_radio_player.py
```

### Radyo Dinleme Adımları

1. **URL Girişi**
   - Üst kısımdaki metin kutusuna radyo istasyonu URL'sini yapıştırın
   - Örnek: `http://stream.example.com:8000/radio`

2. **Çal Butonu**
   - "▶ Çal" butonuna tıklayın
   - Radyo yayını başlayacaktır

3. **Ses Ayarı**
   - Ses seviyesi kaydırıcısıyla ses seviyesini ayarlayın (0-100%)

4. **Equalizer Kullanımı**
   - 10 bantlı equalizer ile ses kalitesini ayarlayın
   - Her bant -20 dB ile +20 dB arasında ayarlanabilir
   - "Sıfırla" butonu ile tüm bantları 0'a getirebilirsiniz

5. **Durdurma**
   - "⏹ Durdur" butonu ile yayını durdurun

### Favoriler Yönetimi

#### Favori Ekleme
1. URL kutusuna istasyon adresini girin
2. Sağ paneldeki "➕ Ekle" butonuna tıklayın
3. İstasyon için bir isim girin
4. "OK" ile kaydedin

#### Favori Çalma
- Favoriler listesinden bir istasyona çift tıklayın
- Otomatik olarak URL alanına yüklenecek ve çalmaya başlayacaktır

#### Favori Silme
1. Silmek istediğiniz favoriyi seçin
2. "🗑 Sil" butonuna tıklayın
3. Onaylayın

## 🎚️ Equalizer Bantları

Equalizer 10 banttan oluşur:

| Bant | Frekans | Açıklama |
|------|---------|----------|
| 1    | 60 Hz   | Derin bas |
| 2    | 170 Hz  | Bas |
| 3    | 310 Hz  | Alt orta |
| 4    | 600 Hz  | Orta |
| 5    | 1 kHz   | Orta |
| 6    | 3 kHz   | Üst orta |
| 7    | 6 kHz   | Tiz |
| 8    | 12 kHz  | Yüksek tiz |
| 9    | 14 kHz  | Çok yüksek tiz |
| 10   | 16 kHz  | Ultra tiz |

### Equalizer Ayar Önerileri

**Pop Müzik**
```
60Hz: +3, 170Hz: +2, 310Hz: 0, 600Hz: -1, 1kHz: 0, 3kHz: +2, 6kHz: +3, 12kHz: +2, 14kHz: +1, 16kHz: 0
```

**Rock Müzik**
```
60Hz: +4, 170Hz: +3, 310Hz: 0, 600Hz: -2, 1kHz: -1, 3kHz: +1, 6kHz: +3, 12kHz: +4, 14kHz: +3, 16kHz: +2
```

**Klasik Müzik**
```
60Hz: +2, 170Hz: +1, 310Hz: 0, 600Hz: +1, 1kHz: +2, 3kHz: +2, 6kHz: +1, 12kHz: 0, 14kHz: -1, 16kHz: 0
```

**Jazz**
```
60Hz: +3, 170Hz: +2, 310Hz: +1, 600Hz: 0, 1kHz: +1, 3kHz: +2, 6kHz: +1, 12kHz: 0, 14kHz: -1, 16kHz: -1
```

**Konuşma/Podcast**
```
60Hz: -2, 170Hz: -1, 310Hz: +2, 600Hz: +3, 1kHz: +4, 3kHz: +3, 6kHz: +1, 12kHz: -1, 14kHz: -2, 16kHz: -2
```

## 📻 Radyo İstasyonu URL'leri Nasıl Bulunur?

### Yöntem 1: İstasyon Web Siteleri
Çoğu radyo istasyonu kendi web sitesinde akış URL'sini paylaşır. "Listen Live" veya "Canlı Dinle" bölümlerinde bulabilirsiniz.

### Yöntem 2: İnternet Radyo Dizinleri
- [Radio Browser](https://www.radio-browser.info/)
- [TuneIn](https://tunein.com/)
- [Internet Radio](https://www.internet-radio.com/)
- [SHOUTcast Directory](https://directory.shoutcast.com/)

### Yöntem 3: M3U/PLS Dosyaları
Bazı istasyonlar .m3u veya .pls dosyaları sunar. Bu dosyaları metin editörü ile açarak gerçek akış URL'sini bulabilirsiniz.

### Örnek Türk Radyo İstasyonları

**Not**: Aşağıdaki URL'ler örnek amaçlıdır. Güncel URL'leri istasyonların web sitelerinden kontrol edin.

```
Metro FM: http://17773.live.streamtheworld.com/METRO_FM.mp3
PowerTürk FM: http://powerturk.radyolarburada.com:8080/powerturk
Radyo 7: http://radyo7.radyotvonline.com/stream
```

## 🔧 Sorun Giderme

### VLC Bulunamadı Hatası
**Sorun**: `libvlc.dll not found` hatası

**Çözüm**:
1. VLC Media Player'ın kurulu olduğundan emin olun
2. VLC'yi Program Files'dan kaldırıp yeniden kurun
3. 64-bit Python kullanıyorsanız, 64-bit VLC kurun
4. Sistem PATH değişkenine VLC dizinini ekleyin

### Radyo Çalmıyor
**Sorun**: URL'yi girdim ama ses gelmiyor

**Çözüm**:
1. URL'nin doğru olduğunu kontrol edin (http:// veya https://)
2. İnternet bağlantınızı kontrol edin
3. URL'yi web tarayıcısında test edin
4. Firewall/antivirüs ayarlarını kontrol edin
5. Durum bilgisinde "Hata" gösteriyorsa, farklı bir URL deneyin

### Ses Kesilmeleri
**Sorun**: Ses kesilip duruyor

**Çözüm**:
1. İnternet bağlantı hızınızı kontrol edin
2. Diğer bandwidth kullanan uygulamaları kapatın
3. Daha düşük kaliteli bir akış URL'si deneyin
4. VLC cache ayarlarını artırın

### Equalizer Çalışmıyor
**Sorun**: Equalizer kaydırıcıları sesi değiştirmiyor

**Çözüm**:
1. VLC'nin en son sürümünü kullandığınızdan emin olun
2. Uygulamayı yeniden başlatın
3. Önce radyoyu çalıştırın, sonra equalizer'ı ayarlayın

## 📂 Dosya Yapısı

```
project/
├── internet_radio_player.py    # Ana uygulama
├── radio_requirements.txt      # Python bağımlılıkları
├── RADIO_README.md            # Bu dosya
└── radio_favorites.json       # Favoriler (otomatik oluşur)
```

### radio_favorites.json Formatı

```json
[
  {
    "name": "Metro FM",
    "url": "http://17773.live.streamtheworld.com/METRO_FM.mp3"
  },
  {
    "name": "My Favorite Station",
    "url": "http://stream.example.com:8000/radio"
  }
]
```

## 🎯 Klavye Kısayolları

*(Gelecek sürümde eklenecek)*

- `Space`: Çal/Durdur
- `Up/Down`: Ses seviyesi
- `R`: Equalizer sıfırla
- `F`: Favorilere ekle

## 🔄 Güncellemeler ve Geliştirmeler

### Mevcut Sürüm: v1.0
- İlk sürüm
- Temel çalma/durdurma özellikleri
- 10 bantlı equalizer
- Favoriler sistemi
- Modern PyQt5 arayüzü

### Planlanan Özellikler
- [ ] Ses kaydetme özelliği
- [ ] Sleep timer (otomatik kapanma)
- [ ] Şarkı bilgisi gösterimi (metadata)
- [ ] Tema değiştirme
- [ ] Sistem tray ikonu
- [ ] Klavye kısayolları
- [ ] Preset equalizer ayarları
- [ ] Çoklu dil desteği

## 📝 Lisans

Bu proje özel bir proje olup, tüm hakları saklıdır.

## 🤝 Katkıda Bulunma

Önerileriniz ve hata raporlarınız için:
- GitHub Issues
- Email: support@example.com

## ⚠️ Yasal Uyarı

Bu uygulama sadece yasal ve kamuya açık internet radyo akışlarını dinlemek içindir. Telif hakkı ihlali içeren içerikleri dinlemek veya kaydetmek yasaktır. Kullanıcılar dinledikleri içeriklerden sorumludur.

## 📞 Destek

Herhangi bir sorunla karşılaşırsanız:
1. Bu README dosyasını dikkatlice okuyun
2. Sorun Giderme bölümünü kontrol edin
3. VLC kurulumunu doğrulayın
4. Python bağımlılıklarını yeniden yükleyin

## 🙏 Teşekkürler

- **VLC Media Player** - Güçlü medya backend
- **PyQt5** - Modern GUI framework
- **Python Community** - Harika kütüphaneler

---

**Keyifli dinlemeler! 🎵**
