# 💼 Kişisel Verimlilik ve Zaman Yönetimi Uygulaması

Modern, kullanıcı dostu ve kapsamlı bir verimlilik uygulaması. Zamanınızı etkili bir şekilde yönetin, hedeflerinize ulaşın ve motivasyonunuzu yüksek tutun!

## ✨ Özellikler

### 🍅 Pomodoro Timer
- 25 dakika çalışma, 5 dakika kısa mola, 15 dakika uzun mola
- Özelleştirilebilir süreler
- Görsel ilerleme göstergesi
- Ses ve masaüstü bildirimleri
- Seans takibi

### ✓ Görev Listesi (To-Do)
- Görev ekleme, düzenleme ve silme
- Öncelik seviyeleri (Düşük, Orta, Yüksek)
- Proje bazlı kategorilendirme
- Filtreleme (Tümü, Aktif, Tamamlanan)
- İlerleme takibi

### 📁 Proje Yönetimi
- Proje oluşturma ve düzenleme
- Renk kodlu projeler
- Proje bazlı görev istatistikleri
- Tamamlanma oranı göstergesi
- Görsel ilerleme çubukları

### ⏱️ Zaman Takibi
- Çalışma sürelerini takip edin
- Proje bazlı zaman kaydı
- Detaylı aktivite geçmişi
- Toplam çalışma süresi özeti
- Manuel başlatma/durdurma

### 📊 Raporlar
- Günlük, haftalık ve aylık raporlar
- Proje bazlı zaman dağılımı
- Tamamlanan görev istatistikleri
- Görsel grafikler ve çizelgeler
- Veri görselleştirme (Bar, Pie, Line charts)

### 🎯 Hedef Belirleme ve Takip
- Hedef oluşturma ve yönetimi
- İlerleme takibi
- Son tarih belirleme
- Tamamlanma yüzdesi
- Görsel ilerleme göstergeleri

### 📝 Not Alma
- Hızlı not oluşturma
- Başlık ve içerik destekli notlar
- Not arama özelliği
- Güncelleme tarihi takibi
- Kolay düzenleme ve silme

### 📅 Takvim Entegrasyonu
- Etkinlik oluşturma ve yönetimi
- Tarih ve saat bazlı planlama
- Yaklaşan etkinlik hatırlatıcıları
- Geçmiş etkinlik geçmişi
- "Bugün" ve "Yarın" etiketleri

### 🚫 Dikkat Dağıtıcı Website Engelleyici
- Website engelleme listesi
- Popüler dikkat dağıtıcı siteler
- Hızlı ekleme/çıkarma
- Hatırlatma sistemi

### 💪 Motivasyon Mesajları
- 20+ Türkçe motivasyon sözü
- Rastgele söz gösterimi
- Görsel ve etkileşimli tasarım
- Yeni söz butonu

### 💾 Yedekleme ve Geri Yükleme
- JSON formatında veri dışa aktarma
- Verileri geri yükleme
- Tüm verilerinizi koruma
- Kolay yedek alma

### 📱 Cross-Platform
- **Windows**: Electron ile masaüstü uygulaması
- **Web**: Modern tarayıcılarda çalışır
- **Mobil**: PWA desteği ile mobil cihazlarda kullanılabilir
- Responsive tasarım - tüm ekran boyutlarına uyumlu

## 🚀 Kurulum

### Gereksinimler
- Node.js 14+
- npm veya yarn

### Kurulum Adımları

1. Projeyi klonlayın:
```bash
git clone <repo-url>
cd productivity-app
```

2. Bağımlılıkları yükleyin:
```bash
npm install
```

3. Geliştirme sunucusunu başlatın:
```bash
npm start
```

Uygulama http://localhost:3000 adresinde açılacaktır.

## 🖥️ Electron ile Masaüstü Uygulaması

### Development modunda çalıştırma:
```bash
npm run electron-dev
```

### Production build:
```bash
npm run build
npm run electron
```

### Windows installer oluşturma:
```bash
npm run package
```

## 📱 PWA (Progressive Web App)

Uygulama PWA desteği ile gelir. Mobil cihazlarda:

1. Tarayıcıda uygulamayı açın
2. "Ana ekrana ekle" seçeneğini kullanın
3. Uygulama artık ana ekranınızda!

## 🛠️ Teknolojiler

- **React 18** - Modern UI framework
- **Electron** - Cross-platform desktop app
- **Recharts** - Data visualization
- **LocalForage** - Offline storage
- **date-fns** - Date manipulation
- **CSS3** - Modern styling
- **Service Worker** - PWA support

## 📂 Proje Yapısı

```
productivity-app/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── service-worker.js
├── src/
│   ├── components/
│   │   ├── PomodoroTimer/
│   │   ├── TodoList/
│   │   ├── Projects/
│   │   ├── TimeTracker/
│   │   ├── Reports/
│   │   ├── Goals/
│   │   ├── Notes/
│   │   ├── Calendar/
│   │   ├── WebsiteBlocker/
│   │   └── Motivation/
│   ├── utils/
│   │   ├── storage.js
│   │   ├── motivationalQuotes.js
│   │   └── dateUtils.js
│   ├── styles/
│   │   └── index.css
│   ├── App.js
│   ├── App.css
│   └── index.js
├── electron/
│   └── main.js
└── package.json
```

## 🎨 Özellikler Detayları

### Veri Yönetimi
- Tüm veriler tarayıcıda (IndexedDB) saklanır
- Otomatik kaydetme
- Offline çalışma desteği
- İstediğiniz zaman yedekleme

### Kullanıcı Deneyimi
- Temiz ve modern arayüz
- Koyu mod desteği (gradient tema)
- Animasyonlu geçişler
- Responsive tasarım
- Hızlı ve akıcı performans

### Bildirimler
- Pomodoro tamamlandığında bildirim
- Tarayıcı bildirimleri
- Görsel ve sesli uyarılar

## 🔧 Özelleştirme

### Pomodoro Ayarları
App.js içinde `settings` state'ini düzenleyerek Pomodoro sürelerini özelleştirebilirsiniz:

```javascript
const [settings, setSettings] = useState({
  pomodoroWork: 25,        // Çalışma süresi (dakika)
  pomodoroShortBreak: 5,   // Kısa mola (dakika)
  pomodoroLongBreak: 15,   // Uzun mola (dakika)
  pomodoroSessions: 4      // Uzun mola için seans sayısı
});
```

### Renkler
`src/styles/index.css` dosyasındaki CSS değişkenlerini düzenleyerek renk şemasını özelleştirebilirsiniz.

## 📖 Kullanım Kılavuzu

1. **Başlangıç**: Anasayfada motivasyon sözünüzü görün ve Pomodoro ile çalışmaya başlayın
2. **Görev Ekleme**: Görevler sekmesinden yapılacak işlerinizi ekleyin
3. **Proje Oluşturma**: Görevlerinizi organize etmek için projeler oluşturun
4. **Zaman Takibi**: Ne kadar çalıştığınızı takip edin
5. **Hedef Belirleme**: Ulaşmak istediğiniz hedefleri belirleyin ve takip edin
6. **Raporlar**: İlerlemenizi grafiklerle görün

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.

## 📄 Lisans

MIT

## 👨‍💻 Geliştirici

Bu uygulama modern web teknolojileri kullanılarak geliştirilmiştir.

## 🆘 Destek

Herhangi bir sorunuz veya sorununuz varsa issue açabilirsiniz.

---

**Zamanınızı en iyi şekilde yönetin ve hedeflerinize ulaşın! 🚀**
