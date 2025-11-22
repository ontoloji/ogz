# 📺 World TV Streaming

Windows ve macOS için geliştirilmiş modern, kullanıcı dostu online TV streaming uygulaması.

## ✨ Özellikler

- 🌍 **Dünya Genelinde TV Kanalları** - Türkiye, ABD, Avrupa, Asya ve daha fazlası
- 📱 **Modern Arayüz** - Kolay kullanılabilir, şık tasarım
- ⛶ **Tam Ekran Modu** - Sinema kalitesinde izleme deneyimi
- ⭐ **Favori Kanallar** - Beğendiğiniz kanalları kaydedin
- 🔍 **Akıllı Arama** - Kanalları hızlıca bulun
- 🌐 **Ülke ve Kategori Filtreleri** - İstediğiniz içeriği kolayca bulun
- 🎵 **Çoklu Kategori** - Haber, Spor, Eğlence, Müzik, Belgesel ve daha fazlası
- 💾 **Yerel Kayıt** - Favori listeniz cihazınızda saklanır

## 🖥️ Desteklenen Platformlar

- ✅ Windows 10/11
- ✅ macOS 10.13 (High Sierra) ve üzeri

## 📋 Gereksinimler

- Node.js 18.x veya üzeri
- npm veya yarn paket yöneticisi

## 🚀 Kurulum

### 1. Depoyu Klonlayın

```bash
git clone <repository-url>
cd streaming-tv-app
```

### 2. Bağımlılıkları Yükleyin

```bash
npm install
```

### 3. Uygulamayı Başlatın

```bash
npm start
```

## 📦 Kurulum Dosyası Oluşturma

### Windows için:

```bash
npm run build:win
```

Kurulum dosyası `dist/` klasöründe oluşturulacaktır.

### macOS için:

```bash
npm run build:mac
```

DMG dosyası `dist/` klasöründe oluşturulacaktır.

### Her İki Platform için:

```bash
npm run build
```

## 🎮 Kullanım

### Temel Kullanım

1. **Kanal Seçimi**: Sol taraftaki kanal listesinden izlemek istediğiniz kanalı tıklayın
2. **Arama**: Üst kısımdaki arama kutusuna kanal adı yazarak arama yapın
3. **Filtreleme**:
   - Ülke filtresinden istediğiniz ülkeyi seçin
   - Kategori filtresinden içerik türünü seçin
4. **Favoriler**: Bir kanalı izlerken sağ üstteki yıldız butonuna tıklayarak favorilere ekleyin

### Klavye Kısayolları

- **F veya f**: Tam ekran modunu aç/kapa
- **Boşluk**: Oynat/Duraklat
- **ESC**: Tam ekrandan çık

### Video Kontrolleri

- ▶️ Oynat/Duraklat butonu
- 🔊 Ses seviyesi kontrolü
- ⛶ Tam ekran modu
- ⭐ Favorilere ekle/çıkar

## 📺 Kanal Kategorileri

- 📰 **Haber**: Ulusal ve uluslararası haber kanalları
- ⚽ **Spor**: Spor yayınları ve etkinlikler
- 🎬 **Film**: Film kanalları
- 📺 **Dizi**: Dizi kanalları
- 🎭 **Eğlence**: Genel eğlence kanalları
- 🎵 **Müzik**: Müzik videoları ve konserler
- 👶 **Çocuk**: Çocuk programları
- 📚 **Belgesel**: Belgesel ve eğitim programları
- 📡 **Genel**: Genel içerik kanalları

## 🌍 Desteklenen Ülkeler

- 🇹🇷 Türkiye
- 🇺🇸 Amerika Birleşik Devletleri
- 🇬🇧 İngiltere
- 🇩🇪 Almanya
- 🇫🇷 Fransa
- 🇮🇹 İtalya
- 🇪🇸 İspanya
- 🇷🇺 Rusya
- 🇨🇳 Çin
- 🇯🇵 Japonya
- 🇰🇷 Güney Kore
- 🇸🇦 Suudi Arabistan
- 🇦🇪 Birleşik Arap Emirlikleri
- Ve daha fazlası...

## 🔧 Kanal Ekleme

Kendi kanallarınızı eklemek için `src/channels.json` dosyasını düzenleyin:

```json
{
  "id": "unique-channel-id",
  "name": "Kanal Adı",
  "country": "TR",
  "category": "news",
  "url": "https://stream-url.com/playlist.m3u8",
  "description": "Kanal açıklaması"
}
```

### Desteklenen Stream Formatları

- HLS (HTTP Live Streaming) - `.m3u8`
- MPEG-DASH
- Direkt video akışları

## 🛠️ Teknolojiler

- **Electron**: Cross-platform masaüstü uygulaması
- **HLS.js**: HTTP Live Streaming desteği
- **HTML5 Video**: Modern video oynatıcı
- **Node.js**: Backend runtime
- **JavaScript/ES6**: Uygulama mantığı

## 📂 Proje Yapısı

```
streaming-tv-app/
├── src/
│   ├── main.js          # Electron ana process
│   ├── renderer.js      # Renderer process (uygulama mantığı)
│   ├── index.html       # Ana HTML dosyası
│   ├── styles.css       # CSS stilleri
│   └── channels.json    # Kanal veritabanı
├── assets/              # Uygulama ikonları ve görseller
├── package.json         # Proje bağımlılıkları
└── README.md           # Dokümantasyon
```

## 🐛 Sorun Giderme

### Video Oynatılmıyor

1. İnternet bağlantınızı kontrol edin
2. Başka bir kanal deneyin
3. Uygulamayı yeniden başlatın

### Kanal Bulunamıyor

1. Arama filtrelerini temizleyin
2. "Tüm Kanallar" sekmesine geçin
3. Ülke ve kategori filtrelerini "Tüm" olarak ayarlayın

### Uygulama Açılmıyor

1. Node.js ve npm'in doğru yüklendiğinden emin olun
2. Bağımlılıkları yeniden yükleyin: `npm install`
3. Terminalde hata mesajlarını kontrol edin

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## ⚠️ Yasal Uyarı

Bu uygulama yalnızca halka açık ve yasal olarak yayınlanan TV akışlarını destekler. Kullanıcılar, yayınları izlerken telif hakkı ve yayın haklarına saygı göstermelidir. Geliştiriciler, kullanıcıların yasadışı içerik izlemesinden sorumlu değildir.

## 📞 Destek

Sorularınız veya sorunlarınız için:
- GitHub Issues kullanın
- Dokümantasyonu inceleyin
- Topluluk forumlarına katılın

## 🎉 Teşekkürler

Bu projeyi kullandığınız için teşekkür ederiz! İyi seyirler! 📺✨

---

**Not**: Kanal listesi düzenli olarak güncellenmektedir. Bazı akışlar bölgenize göre erişilemeyebilir.
