# Personal Assistant - iOS Kişisel Asistan Uygulaması

<div align="center">
    <h3>📱 Kapsamlı iOS Kişisel Asistan ve Görev Yönetimi Uygulaması</h3>
    <p>SwiftUI • Core Data • EventKit • CloudKit • WidgetKit</p>
</div>

---

## 📋 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Özellikler](#-özellikler)
- [Teknik Detaylar](#-teknik-detaylar)
- [Mimari](#-mimari)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Gereksinimler](#-gereksinimler)

---

## 🎯 Genel Bakış

**Personal Assistant**, iOS platformu için geliştirilmiş, modern ve kapsamlı bir kişisel asistan uygulamasıdır. Notlarınızı, görevlerinizi ve takvim etkinliklerinizi tek bir yerde toplayarak hayatınızı organize etmenize yardımcı olur.

### Neden Personal Assistant?

- ✅ **Tek Platformda Her Şey**: Notlar, görevler, takvim ve analitik tek uygulamada
- ✅ **Akıllı Hatırlatmalar**: Zamana ve konuma dayalı otomatik hatırlatmalar
- ✅ **İOS Entegrasyonu**: EventKit, CloudKit, Siri Shortcuts tam entegrasyonu
- ✅ **Modern Tasarım**: SwiftUI ile native iOS tasarımı ve Dark Mode desteği
- ✅ **Verimlilik Odaklı**: Pomodoro Timer ve detaylı analitiklerle verimliliğinizi artırın

---

## ✨ Özellikler

### 🗒️ Not Yönetimi
- **Gelişmiş Not Sistemi**: Zengin metin, fotoğraf ve ses notu desteği
- **Kategori Bazlı Organizasyon**: Özelleştirilebilir kategoriler ve renkler
- **Öncelik Seviyeleri**: Düşük, normal, yüksek öncelik seviyeleri
- **Pin Özelliği**: Önemli notları sabitleyerek üstte tutun
- **Arşiv Sistemi**: Eski notları arşivleyerek düzen sağlayın
- **Güçlü Arama**: Başlık ve içerikte anlık arama
- **Ses Notları**: Mikrofonla hızlıca ses notu kaydedin

### ✅ Görev Yönetimi
- **Gelişmiş Görev Sistemi**: Alt görevler ve bağımlılıklar
- **Proje Bazlı Organizasyon**: Görevleri projelerde gruplayın
- **Son Tarih Takibi**: Gecikmiş görevler için otomatik uyarılar
- **Zaman Takibi**: Görevlerde geçirilen süreyi kaydedin
- **Pomodoro Timer**: 25/5 dakikalık odaklanma oturumları
- **Tamamlanma Yüzdesi**: Alt görevlerle ilerleme takibi
- **Kanban Görünümü**: Görevleri sürükle-bırak ile yönet

### 📅 Takvim Entegrasyonu
- **EventKit Entegrasyonu**: iOS Takvim ile tam senkronizasyon
- **Çoklu Takvim Desteği**: iCloud, Google, Exchange takvimleri
- **Etkinlik Yönetimi**: Toplantı oluşturma, düzenleme ve silme
- **Akıllı Bildirimler**: 24 saat ve 1 saat öncesi hatırlatmalar
- **Katılımcı Takibi**: Toplantı katılımcılarını görüntüleme
- **Konum Bilgisi**: Etkinlik konumu ve harita entegrasyonu

### 🔔 Hatırlatma Sistemi
- **Zamana Dayalı Hatırlatmalar**: Belirli tarih ve saatte hatırlatma
- **Konum Bazlı Hatırlatmalar**: Belirli bir yere gelince veya çıkınca hatırlatma
- **Tekrarlayan Hatırlatmalar**: Günlük, haftalık, aylık tekrar seçenekleri
- **Kritik Uyarılar**: Çok önemli hatırlatmalar için özel mod
- **Sessiz Saatler**: Belirli saatlerde bildirimleri sustur
- **Özelleştirilebilir Sesler**: Farklı hatırlatma sesleri

### 📊 Analitik ve Raporlama
- **Verimlilik Metrikleri**: Günlük, haftalık, aylık istatistikler
- **Görev Tamamlama Oranı**: Grafik ve yüzdelik gösterim
- **Zaman Analizi**: Kategorilere göre zaman dağılımı
- **Odaklanma Oturumları**: Pomodoro istatistikleri
- **İlerleme Grafikleri**: Görsel veri sunumu
- **Hedef Takibi**: Kişisel hedefler ve başarı oranları

### 🔒 Güvenlik ve Gizlilik
- **Face ID / Touch ID**: Biyometrik kilitleme
- **Güvenli Notlar**: Özel notlar için ekstra koruma
- **iCloud Senkronizasyon**: Şifreli bulut yedekleme
- **Yerel Veri Saklama**: Core Data ile güvenli yerel depolama
- **Gizlilik Odaklı**: Tüm veriler cihazınızda kalır

### 🎨 Kullanıcı Deneyimi
- **Modern SwiftUI Tasarımı**: Native iOS görünümü
- **Dark Mode**: Tam karanlık mod desteği
- **Dynamic Type**: Erişilebilirlik font boyutları
- **Haptic Feedback**: Dokunmatik geri bildirim
- **SF Symbols**: Tutarlı ikon seti
- **Adaptive Layout**: iPhone ve iPad desteği
- **Swipe Actions**: Hızlı işlemler için kaydırma jestleri

### 📲 İleri Seviye Özellikler
- **Widget Desteği**: Home Screen ve Lock Screen widget'ları
- **Live Activities**: Dinamik bildirimler (iOS 16+)
- **Siri Shortcuts**: "Hey Siri" komut desteği
- **App Intents**: iOS 16 App Intents API
- **Handoff**: iPad/Mac ile sorunsuz geçiş
- **Share Extension**: Safari, Fotoğraflar vb. uygulamalardan paylaşım
- **Quick Actions**: 3D Touch / Haptic Touch hızlı menü
- **Spotlight Search**: Sistem çapında arama entegrasyonu

---

## 🛠 Teknik Detaylar

### Teknoloji Yığını

#### **Temel Teknolojiler**
- **SwiftUI**: Modern, deklaratif UI framework
- **Swift**: Hızlı ve güvenli programlama dili
- **Combine**: Reaktif programlama ve veri akışı
- **iOS 16.0+**: En yeni iOS özellikleri

#### **Veri Katmanı**
- **Core Data**: Yerel veri saklama ve yönetim
- **CloudKit**: iCloud senkronizasyon
- **NSPersistentCloudKitContainer**: Otomatik bulut sync
- **Codable**: JSON serialization

#### **iOS Frameworks**
- **EventKit**: Takvim ve hatırlatma entegrasyonu
- **UserNotifications**: Local ve remote bildirimler
- **CoreLocation**: Konum tabanlı özellikler
- **LocalAuthentication**: Face ID / Touch ID
- **WidgetKit**: Home ve Lock Screen widget'ları
- **AppIntents**: Siri ve Shortcuts entegrasyonu
- **BackgroundTasks**: Arka plan işlemleri

### Veri Modeli

```swift
// Core Entities
- Note
  - id, title, content
  - category, tags
  - priority, isPinned, isArchived
  - reminders, location
  - images, audioURL

- Task
  - id, title, description
  - dueDate, completedAt
  - priority, isCompleted
  - category, project, tags
  - subtasks, dependencies
  - timeEntries, estimatedDuration

- Category
  - id, name, colorHex, iconName
  - notes, tasks

- Project
  - id, name, description
  - deadline, progress
  - tasks, isArchived

- Reminder
  - id, date, repeatInterval
  - isEnabled, notificationID

- LocationReminder
  - id, latitude, longitude
  - radius, placeName
  - triggerOnEntry, triggerOnExit

- FocusSession
  - id, startTime, endTime
  - duration, sessionType
  - isCompleted, taskTitle
```

---

## 🏗 Mimari

### MVVM (Model-View-ViewModel) Pattern

```
PersonalAssistant/
├── App/
│   ├── PersonalAssistantApp.swift     # Ana uygulama
│   ├── ContentView.swift              # Root view
│   └── AppState.swift                 # Global state
│
├── Models/
│   ├── CoreDataModel.xcdatamodeld     # Core Data schema
│   ├── Note+Extensions.swift          # Note entity extensions
│   ├── Task+Extensions.swift          # Task entity extensions
│   ├── Category+Extensions.swift      # Category extensions
│   └── Project+Extensions.swift       # Project extensions
│
├── ViewModels/
│   ├── NotesViewModel.swift           # Not yönetimi logic
│   ├── TasksViewModel.swift           # Görev yönetimi logic
│   └── AnalyticsViewModel.swift       # Analitik hesaplamaları
│
├── Views/
│   ├── Home/
│   │   └── HomeView.swift             # Ana dashboard
│   ├── Notes/
│   │   ├── NotesListView.swift        # Not listesi
│   │   ├── NoteDetailView.swift       # Not detay
│   │   └── AddNoteView.swift          # Not ekleme
│   ├── Tasks/
│   │   ├── TasksView.swift            # Görev listesi
│   │   └── PomodoroTimerView.swift    # Pomodoro timer
│   ├── Calendar/
│   │   └── CalendarView.swift         # Takvim görünümü
│   ├── Analytics/
│   │   └── AnalyticsView.swift        # Analitik dashboard
│   ├── Settings/
│   │   └── SettingsView.swift         # Ayarlar
│   └── Shared/
│       ├── NoteCardView.swift         # Paylaşılan componentler
│       ├── TaskRowView.swift
│       └── EventCardView.swift
│
├── Services/
│   ├── DataService/
│   │   └── PersistenceController.swift    # Core Data yönetimi
│   ├── NotificationService/
│   │   └── NotificationManager.swift      # Bildirim yönetimi
│   ├── CalendarService/
│   │   └── CalendarManager.swift          # EventKit yönetimi
│   ├── LocationService/
│   │   └── LocationManager.swift          # Konum servisi
│   ├── BiometricService/
│   │   └── BiometricAuthManager.swift     # Face ID/Touch ID
│   └── CloudService/
│       └── CloudKitManager.swift          # iCloud sync
│
├── Utilities/
│   ├── ThemeManager.swift             # Tema yönetimi
│   ├── HapticManager.swift            # Haptic feedback
│   └── BackgroundTaskManager.swift    # Arka plan görevleri
│
└── Resources/
    ├── Assets.xcassets                # Görseller ve renkler
    ├── Info.plist                     # Uygulama konfigürasyonu
    └── PersonalAssistant.entitlements # İzinler ve capabilities

PersonalAssistantWidget/
└── PersonalAssistantWidget.swift      # Widget extension

PersonalAssistantIntents/
└── AppIntents.swift                   # Siri Shortcuts
```

### Veri Akışı

```
User Action → View → ViewModel → Service Layer → Core Data/CloudKit
                ↑                                         ↓
                └─────────── ObservableObject ←──────────┘
```

### Dependency Injection

```swift
@StateObject private var persistenceController = PersistenceController.shared
@StateObject private var notificationManager = NotificationManager.shared
@StateObject private var calendarManager = CalendarManager.shared
@StateObject private var locationManager = LocationManager.shared
@StateObject private var biometricManager = BiometricAuthManager.shared
```

---

## 🚀 Kurulum

### Gereksinimler

- **macOS**: 13.0 (Ventura) veya üzeri
- **Xcode**: 14.0 veya üzeri
- **iOS Deployment Target**: 16.0+
- **Swift**: 5.7+
- **Apple Developer Account**: Widget ve Siri için gerekli

### Adım Adım Kurulum

1. **Repository'yi Klonlayın**
```bash
git clone https://github.com/yourusername/personal-assistant-ios.git
cd personal-assistant-ios/PersonalAssistant
```

2. **Xcode ile Açın**
```bash
open PersonalAssistant.xcodeproj
```

3. **Signing & Capabilities Ayarları**
   - Xcode'da projeyi seçin
   - "Signing & Capabilities" sekmesine gidin
   - Team'inizi seçin
   - Bundle Identifier'ı değiştirin (örn: `com.yourname.personalassistant`)

4. **iCloud Container Ayarları**
   - "Signing & Capabilities" → "+" → "iCloud"
   - CloudKit container oluşturun
   - `PersonalAssistant.entitlements` dosyasındaki container ID'yi güncelleyin

5. **App Group Ayarları**
   - "Signing & Capabilities" → "+" → "App Groups"
   - Yeni app group oluşturun: `group.com.yourname.personalassistant`
   - Widget ve Intent extension'ları için aynı grup'u ekleyin

6. **Build ve Run**
   - Simulator veya gerçek cihaz seçin
   - Cmd + R ile çalıştırın

### Opsiyonel Konfigürasyon

#### Push Notifications
```bash
# APNs için sertifika oluşturun
# Apple Developer Portal → Certificates, Identifiers & Profiles
```

#### Siri Shortcuts
```bash
# Info.plist'e NSAppShortcuts ekleyin
# Siri iznini test edin
```

---

## 📱 Kullanım

### İlk Başlatma

1. **Onboarding**: Uygulamayı ilk açtığınızda hoş geldin ekranları gösterilir
2. **İzinler**: Takvim, bildirim, konum izinlerini verin
3. **Kategoriler**: Varsayılan kategoriler otomatik oluşturulur
4. **İlk Not**: "+" butonuna basarak ilk notunuzu ekleyin

### Temel İşlemler

#### Not Ekleme
```swift
1. "Notlar" sekmesine gidin
2. Sağ üstteki "+" butonuna dokunun
3. Başlık ve içerik girin
4. Kategori ve öncelik seçin
5. İsteğe bağlı hatırlatma ekleyin
6. "Kaydet" butonuna basın
```

#### Görev Oluşturma
```swift
1. "Görevler" sekmesine gidin
2. "+" butonuna dokunun
3. Görev başlığı girin
4. Son tarih ve öncelik belirleyin
5. Alt görevler ekleyin (opsiyonel)
6. "Kaydet"
```

#### Pomodoro Kullanımı
```swift
1. "Görevler" → Timer ikonu
2. Odaklanma/mola modunu seçin
3. "Başlat" butonuna dokunun
4. Timer otomatik olarak çalışır
5. Tamamlandığında bildirim alırsınız
```

### Siri Komutları

```
"Hey Siri, Personal Assistant ile not ekle"
"Hey Siri, bugünkü görevleri göster"
"Hey Siri, Pomodoro başlat"
"Hey Siri, yeni görev oluştur"
```

### Widget Kullanımı

1. **Home Screen**
   - Ana ekranda boş alana uzun basın
   - "+" butonuna dokunun
   - "Personal Assistant" widget'ını seçin
   - Boyut seçin (küçük/orta/büyük)

2. **Lock Screen** (iOS 16+)
   - Kilit ekranında uzun basın
   - "Özelleştir"
   - Widget ekle
   - Personal Assistant widget'larını seçin

---

## 📸 Ekran Görüntüleri

```
[Ana Ekran]  [Notlar]  [Görevler]  [Takvim]  [Analitik]
```

---

## 📋 Gereksinimler

### Minimum Gereksinimler
- iPhone: iPhone 8 ve üzeri
- iOS: 16.0 veya üzeri
- Depolama: 50 MB boş alan
- İnternet: iCloud sync için gerekli

### Önerilen
- iPhone: iPhone 12 ve üzeri
- iOS: iOS 17.0
- Face ID / Touch ID: Güvenlik özellikleri için
- iCloud: Çoklu cihaz senkronizasyonu

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👤 Geliştirici

**Claude Code**
- GitHub: [@claude-code](https://github.com/claude-code)

---

## 🙏 Teşekkürler

- SwiftUI framework için Apple'a
- Open source kütüphane geliştiricilerine
- Tasarım inspirasyonu için iOS topluluğuna

---

## 📞 İletişim

Sorularınız veya önerileriniz için:
- Email: support@personalassistant.app
- GitHub Issues: [Issues](https://github.com/yourusername/personal-assistant-ios/issues)

---

<div align="center">
    <p>⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐</p>
    <p>Made with ❤️ using SwiftUI</p>
</div>
