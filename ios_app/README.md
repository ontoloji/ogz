# Müzik Çalar - iOS CarPlay App

iOS uygulaması - CarPlay desteği ile

## Özellikler

### CarPlay Entegrasyonu
- ✅ Şarkı çalma kontrolleri
- ✅ Playlist navigasyonu
- ✅ Now Playing ekranı
- ✅ Arama özellikleri
- ✅ Siri entegrasyonu

### iOS Özellikleri
- SwiftUI modern UI
- AVFoundation audio
- Background playback
- AirPlay desteği
- Handoff desteği

## Kurulum

### Gereksinimler
- Xcode 14+
- iOS 14+ deployment target
- Apple Developer hesabı
- CarPlay entitlement

### Adımlar

1. **Xcode Projesi Oluşturma:**
```bash
cd ios_app
open MusicPlayer.xcodeproj
```

2. **CarPlay Entitlement Ekleme:**
- Project Navigator > Signing & Capabilities
- "+ Capability" > CarPlay
- Audio types: Music, Podcast

3. **Info.plist Ayarları:**
```xml
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```

4. **Build & Run:**
- iPhone/iPad simulator veya gerçek cihaz
- CarPlay simulator için: I/O > External Displays > CarPlay

## Proje Yapısı

```
ios_app/
├── MusicPlayer/
│   ├── App/
│   │   ├── MusicPlayerApp.swift        # Ana app
│   │   └── AppDelegate.swift           # App lifecycle
│   │
│   ├── CarPlaySupport/
│   │   ├── CarPlaySceneDelegate.swift  # CarPlay scene
│   │   ├── CarPlayTemplates.swift      # Template builders
│   │   └── NowPlayingManager.swift     # Now playing info
│   │
│   ├── Views/
│   │   ├── HomeView.swift              # Ana ekran
│   │   ├── PlayerView.swift            # Oynatıcı
│   │   ├── PlaylistView.swift          # Playlist'ler
│   │   ├── SearchView.swift            # Arama
│   │   └── SettingsView.swift          # Ayarlar
│   │
│   ├── Audio/
│   │   ├── AudioPlayer.swift           # AVAudioPlayer wrapper
│   │   ├── AudioSession.swift          # Audio session manager
│   │   └── RemoteCommandManager.swift  # Medya kontrolleri
│   │
│   ├── Networking/
│   │   ├── SpotifyClient.swift         # Spotify API
│   │   ├── YouTubeMusicClient.swift    # YouTube Music
│   │   └── APIManager.swift            # Network layer
│   │
│   ├── Models/
│   │   ├── Track.swift                 # Track model
│   │   ├── Playlist.swift              # Playlist model
│   │   └── RadioStation.swift          # Radio station
│   │
│   └── Resources/
│       ├── Assets.xcassets             # Images, icons
│       └── Info.plist                  # App configuration
│
└── MusicPlayer.xcodeproj
```

## CarPlay Geliştirme

### Scene Delegate

```swift
import CarPlay

class CarPlaySceneDelegate: UIResponder, CPTemplateApplicationSceneDelegate {
    var interfaceController: CPInterfaceController?

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didConnect interfaceController: CPInterfaceController
    ) {
        self.interfaceController = interfaceController

        // Root template
        let tabBarTemplate = createTabBarTemplate()
        interfaceController.setRootTemplate(tabBarTemplate, animated: true)
    }

    func createTabBarTemplate() -> CPTabBarTemplate {
        let templates = [
            createNowPlayingTemplate(),
            createPlaylistsTemplate(),
            createRadioTemplate()
        ]

        return CPTabBarTemplate(templates: templates)
    }
}
```

### Now Playing

```swift
func updateNowPlayingInfo(track: Track) {
    var nowPlayingInfo = [String: Any]()

    nowPlayingInfo[MPMediaItemPropertyTitle] = track.title
    nowPlayingInfo[MPMediaItemPropertyArtist] = track.artist
    nowPlayingInfo[MPMediaItemPropertyAlbumTitle] = track.album
    nowPlayingInfo[MPMediaItemPropertyPlaybackDuration] = track.duration
    nowPlayingInfo[MPNowPlayingInfoPropertyElapsedPlaybackTime] = currentTime

    // Artwork
    if let artworkImage = loadArtwork(url: track.thumbnailURL) {
        let artwork = MPMediaItemArtwork(boundsSize: artworkImage.size) { _ in
            return artworkImage
        }
        nowPlayingInfo[MPMediaItemPropertyArtwork] = artwork
    }

    MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo
}
```

### Remote Commands

```swift
func setupRemoteCommands() {
    let commandCenter = MPRemoteCommandCenter.shared()

    // Play
    commandCenter.playCommand.addTarget { _ in
        self.audioPlayer.play()
        return .success
    }

    // Pause
    commandCenter.pauseCommand.addTarget { _ in
        self.audioPlayer.pause()
        return .success
    }

    // Next
    commandCenter.nextTrackCommand.addTarget { _ in
        self.playNext()
        return .success
    }

    // Previous
    commandCenter.previousTrackCommand.addTarget { _ in
        self.playPrevious()
        return .success
    }
}
```

## Apple CarPlay Guidelines

### Güvenlik
- ⚠️ Sürüş sırasında minimum etkileşim
- ⚠️ Büyük, dokunması kolay butonlar
- ⚠️ Yüksek kontrast, okunabilir yazılar
- ⚠️ Ses geri bildirimi (Siri)

### UI Şablonları
- `CPListTemplate` - Playlist, arama sonuçları
- `CPNowPlayingTemplate` - Now playing ekranı
- `CPTabBarTemplate` - Tab navigation
- `CPSearchTemplate` - Arama interface

### Sınırlamalar
- Maksimum 12 item per list
- Video playback yasak
- Custom UI sınırlı
- Keyboard kullanımı minimal

## Test

### CarPlay Simulator
1. Xcode > Run
2. I/O > External Displays > CarPlay
3. 800x480 CarPlay penceresi açılır

### Gerçek Cihaz
1. iPhone'u USB ile araç sistemine bağlayın
2. CarPlay otomatik başlar
3. Debug için Xcode wireless debugging

## Yayınlama

### App Store Connect
1. Apple Developer Portal > Identifiers
2. CarPlay entitlement isteyin
3. App Store Connect'te app oluşturun
4. CarPlay screenshots ekleyin

### Review Notları
- CarPlay özellikleri açıkça belirtin
- Sürüş güvenliği vurgulayın
- Test senaryoları sağlayın

## Siri Integration

```swift
import Intents

// Play music intent
INPlayMediaIntent()

// Voice commands:
// "Play [song name]"
// "Play music by [artist]"
// "Play my playlist"
```

## Background Audio

```swift
// Audio session
let audioSession = AVAudioSession.sharedInstance()
try? audioSession.setCategory(.playback, mode: .default)
try? audioSession.setActive(true)

// Background modes in Info.plist
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```

## Notlar

- Desktop uygulama ile API paylaşımı için backend gerekli
- iCloud sync için CloudKit kullanılabilir
- Offline playback için local caching
- CarPlay için ses kalitesi optimize edilmeli

---

**iOS + CarPlay** - Yolda müzik keyfini çıkarın 🚗🎵
