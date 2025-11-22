# 📱 Fitness Trainer App - Xcode Kurulum Talimatları

Bu dosya, uygulamayı Xcode'da çalıştırmak için gerekli adımları içerir.

## ⚠️ Önemli Not

Bu proje dosyaları SwiftUI kaynak kodlarını içerir. Xcode'da çalıştırmak için bir Xcode projesi oluşturmanız gerekir.

## 🛠 Xcode'da Proje Oluşturma

### Adım 1: Yeni Proje Oluşturun

1. Xcode'u açın
2. "Create a new Xcode project" seçin
3. **iOS** > **App** seçin ve "Next" tıklayın
4. Proje ayarlarını yapın:
   - **Product Name**: `FitnessTrainerApp`
   - **Team**: Geliştirici hesabınızı seçin (veya None)
   - **Organization Identifier**: `com.yourname` (kendi bilginizi girin)
   - **Interface**: **SwiftUI** seçin
   - **Language**: **Swift** seçin
   - **Storage**: **None** seçin (UserDefaults kullanıyoruz)
5. Proje konumunu seçin ve "Create" tıklayın

### Adım 2: Dosyaları Projeye Ekleyin

1. Xcode'da sol tarafta Project Navigator'da projenizi görüyorsunuz
2. Oluşturduğum dosyaları aşağıdaki yapıda organize edin:

#### Models klasörü oluşturun:
- Sağ tıklayın > New Group > "Models" adını verin
- Bu klasöre şu dosyaları ekleyin:
  - `UserProfile.swift`
  - `Exercise.swift`
  - `WorkoutPlan.swift`
  - `ProgressRecord.swift`

#### Views klasörü oluşturun:
- Sağ tıklayın > New Group > "Views" adını verin
- Bu klasöre şu dosyaları ekleyin:
  - `ContentView.swift`
  - `ProfileSetupView.swift`
  - `HomeView.swift`
  - `WorkoutPlanView.swift`
  - `ExerciseDetailView.swift`
  - `WorkoutSessionView.swift`
  - `ProgressView.swift`
  - `SettingsView.swift`

#### Services klasörü oluşturun:
- Sağ tıklayın > New Group > "Services" adını verin
- Bu klasöre şu dosyaları ekleyin:
  - `ExerciseLibrary.swift`
  - `WorkoutPlanGenerator.swift`
  - `DataManager.swift`

#### Ana dosyayı ekleyin:
- `FitnessTrainerApp.swift` dosyasını ana klasöre ekleyin

### Adım 3: Dosyaları Kopyalama

Dosyaları Xcode'a eklemenin iki yolu var:

**Yöntem 1: Drag & Drop**
1. Finder'da FitnessTrainerApp klasörünü açın
2. Dosyaları sürükleyip Xcode'un ilgili klasörüne bırakın
3. "Copy items if needed" seçeneğini işaretleyin

**Yöntem 2: Manuel Kopyalama**
1. Her dosya için: File > New > File
2. Dosya içeriğini kopyalayıp yapıştırın
3. Dosyayı doğru klasöre kaydedin

### Adım 4: iOS Minimum Sürümünü Ayarlayın

1. Project Navigator'da projeyi seçin
2. **TARGETS** > **FitnessTrainerApp** seçin
3. **General** sekmesinde:
   - **Minimum Deployments** > **iOS 16.0** olarak ayarlayın

### Adım 5: Info.plist Ayarları (İsteğe Bağlı)

Info.plist dosyası otomatik oluşturulur, ekstra ayar gerekmez.

## ▶️ Uygulamayı Çalıştırma

### Simülatörde Çalıştırma:

1. Xcode'un üst kısmında cihaz seçiciyi kullanın
2. **iPhone 14 Pro** veya **iPhone 15 Pro** gibi bir simülatör seçin
3. **Cmd + R** tuşlarına basın veya ▶️ Play butonuna tıklayın
4. Simülatör açılacak ve uygulama çalışacak

### Gerçek Cihazda Çalıştırma:

1. iPhone'unuzu Mac'e bağlayın
2. Cihazınızı seçin (cihaz seçicide görünecek)
3. **Signing & Capabilities** sekmesinde:
   - **Team**: Apple Developer hesabınızı seçin
   - Gerekirse "Automatically manage signing" seçeneğini işaretleyin
4. **Cmd + R** ile çalıştırın

## 🐛 Olası Hatalar ve Çözümleri

### Hata: "No such module 'Charts'"
**Çözüm**: iOS 16.0 veya üzeri kullandığınızdan emin olun. Charts, iOS 16+ ile birlikte gelir.

### Hata: "Cannot find 'X' in scope"
**Çözüm**: Tüm dosyaların doğru şekilde projeye eklendiğinden emin olun. File Inspector'da "Target Membership" işaretli olmalı.

### Hata: Build başarısız oluyor
**Çözüm**:
1. **Product** > **Clean Build Folder** (Cmd + Shift + K)
2. Xcode'u kapatıp tekrar açın
3. Derived Data'yı silin: `~/Library/Developer/Xcode/DerivedData`

### Hata: Simülatör açılmıyor
**Çözüm**:
1. **Xcode** > **Preferences** > **Locations**
2. Command Line Tools'un doğru şekilde seçildiğinden emin olun
3. Simülatörü yeniden başlatın

## 📦 Gerekli Swift Paketleri

Bu uygulama harici paket gerektirmez. Tüm özellikler Apple'ın yerleşik framework'leri ile geliştirilmiştir:
- SwiftUI (UI)
- Charts (Grafikler)
- Foundation (Temel işlevler)
- Combine (Reaktif programlama)

## 🎯 Hızlı Başlangıç Özeti

```bash
# 1. Xcode'da yeni proje oluştur: iOS > App > SwiftUI
# 2. Minimum iOS: 16.0
# 3. Tüm .swift dosyalarını projeye ekle
# 4. Cmd + R ile çalıştır
```

## 💡 İpuçları

1. **Preview Kullanın**: Her view dosyasının altında `#Preview` bloğu var. Xcode'un sağ panelinde "Canvas" aktif edilerek preview görülebilir.

2. **Hot Reload**: Xcode preview'lar otomatik güncellenir, hızlı geliştirme için idealdir.

3. **Debug**: Console'da hataları görmek için `Cmd + Shift + Y` kullanın.

4. **Build Hızlandırma**:
   - File > Workspace Settings > Build System: New Build System
   - Derived Data Location: Default

## 📞 Destek

Sorun yaşarsanız:
1. Build loglarını kontrol edin (Cmd + 9)
2. Issue Navigator'ı açın (Cmd + 5)
3. Clean build yapın (Cmd + Shift + K)

## ✅ Tamamlandı!

Artık uygulamanız çalışmaya hazır! 🎉

Başarıyla çalıştırıldıktan sonra:
- İlk açılışta profil oluşturma ekranını göreceksiniz
- Bilgilerinizi girin ve antrenman programınız otomatik oluşturulacak
- Ana sayfadan bugünün antrenmanını başlatabilirsiniz

İyi antrenmanlar! 💪
