# 💪 Fitness Trainer - Kişisel Antrenör Uygulaması

Modern SwiftUI ile geliştirilmiş, kullanıcı dostu iOS fitness uygulaması.

## 🌟 Özellikler

### ✅ Vücut Tipi Bazlı Programlar
- **Ektomorf**: İnce yapılı, hızlı metabolizma için özel program
- **Mezomorf**: Atletik yapı için dengeli program
- **Endomorf**: Güçlü yapı için özel yağ yakma programı

### 🎯 Hedef Odaklı Antrenmanlar
- Kilo Verme
- Kas Yapma
- Güçlenme
- Fit Kalma

### 📊 Detaylı İzleme Sistemi
- **Kilo Takibi**: Grafik ile görselleştirilmiş ilerleme
- **Antrenman Geçmişi**: Tüm antrenmanlarınızın kaydı
- **Set ve Tekrar Kayıtları**: Her egzersiz için detaylı takip
- **İstatistikler**: Haftalık ve genel performans metrikleri

### 🏋️ Kapsamlı Egzersiz Kütüphanesi
25+ egzersiz ile:
- Göğüs
- Sırt
- Omuz
- Biceps
- Triceps
- Bacak
- Karın
- Kardiyo

### 📱 Kullanıcı Dostu Arayüz
- **Modern Tasarım**: SwiftUI ile native iOS deneyimi
- **Görsel Egzersiz Rehberi**: Her egzersiz için adım adım talimatlar
- **Kolay Navigasyon**: Sezgisel tab bar yapısı
- **İpuçları**: Her egzersiz için güvenlik ve form ipuçları

## 🛠 Teknik Detaylar

### Gereksinimler
- iOS 16.0+
- Xcode 15.0+
- Swift 5.9+

### Kullanılan Teknolojiler
- **SwiftUI**: Modern UI framework
- **Charts**: Veri görselleştirme için Swift Charts
- **UserDefaults**: Veri kalıcılığı
- **Combine**: Reaktif programlama

### Proje Yapısı
```
FitnessTrainerApp/
├── Models/
│   ├── UserProfile.swift          # Kullanıcı profil modeli
│   ├── Exercise.swift              # Egzersiz modelleri
│   ├── WorkoutPlan.swift           # Antrenman planı modelleri
│   └── ProgressRecord.swift        # İlerleme kayıtları
├── Views/
│   ├── ContentView.swift           # Ana view
│   ├── ProfileSetupView.swift      # Profil oluşturma
│   ├── HomeView.swift              # Ana sayfa
│   ├── WorkoutPlanView.swift       # Antrenman programı
│   ├── ExerciseDetailView.swift    # Egzersiz detayları
│   ├── WorkoutSessionView.swift    # Aktif antrenman
│   ├── ProgressView.swift          # İlerleme takibi
│   └── SettingsView.swift          # Ayarlar
├── Services/
│   ├── ExerciseLibrary.swift       # Egzersiz kütüphanesi
│   ├── WorkoutPlanGenerator.swift  # Plan oluşturucu
│   └── DataManager.swift           # Veri yönetimi
└── FitnessTrainerApp.swift         # App entry point
```

## 🚀 Kurulum

1. Xcode'da projeyi açın:
```bash
cd FitnessTrainerApp
open FitnessTrainerApp.xcodeproj
```

2. Bir simülatör veya gerçek cihaz seçin

3. Cmd+R ile çalıştırın

## 📖 Kullanım

### İlk Kurulum
1. Uygulamayı açın
2. Adınızı, yaşınızı ve cinsiyetinizi girin
3. Vücut tipinizi seçin
4. Fitness hedefınızı belirleyin
5. Boy, mevcut kilo ve hedef kilonuzu girin
6. "Başla" butonuna tıklayın

### Antrenman Yapma
1. Ana sayfada bugünün antrenmanını görün
2. Antrenman kartına tıklayın
3. Her egzersiz için:
   - Görsel ve talimatları inceleyin
   - Her seti tamamlayın
   - Tekrar ve ağırlık bilgisini kaydedin
4. Tüm egzersizleri tamamlayınca "Bitir" butonuna tıklayın

### Kilo Takibi
1. "İlerleme" sekmesine gidin
2. "Yeni Kilo Kaydı Ekle" butonuna tıklayın
3. Kilonuzu girin
4. İsteğe bağlı not ekleyin
5. Kaydedin

### Program Görüntüleme
1. "Program" sekmesine gidin
2. Haftalık antrenman planınızı görün
3. Gün kartlarına tıklayarak detayları görün
4. Egzersizlere tıklayarak detaylı bilgi alın

## 🎨 Özellikler ve İyileştirmeler

### Mevcut Özellikler
- ✅ Vücut tipi bazlı program oluşturma
- ✅ 6 farklı antrenman programı
- ✅ 25+ egzersiz kütüphanesi
- ✅ Set ve tekrar takibi
- ✅ Kilo grafiği
- ✅ Antrenman geçmişi
- ✅ İstatistikler
- ✅ Profil yönetimi

### Gelecek İyileştirmeler (İsteğe Bağlı)
- [ ] Apple Health entegrasyonu
- [ ] Egzersiz videoları
- [ ] Bildirimler ve hatırlatıcılar
- [ ] Sosyal özellikler (arkadaşlarla yarışma)
- [ ] Özel program oluşturma
- [ ] Beslenme takibi
- [ ] Apple Watch desteği
- [ ] iCloud senkronizasyonu

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 👨‍💻 Geliştirici

Claude AI tarafından geliştirilmiştir.

## 🙏 Teşekkürler

Bu uygulamayı kullandığınız için teşekkürler! Sağlıklı ve fit bir yaşam dilerim! 💪

---

**Not**: Bu uygulama bir sağlık profesyoneli değildir. Herhangi bir egzersiz programına başlamadan önce doktorunuza danışın.
