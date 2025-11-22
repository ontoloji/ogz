# Müzik Çalar Uygulama Planı

## Proje Özeti
Cross-platform müzik çalar uygulaması - Desktop (Windows/Mac) ve iOS (CarPlay destekli)

## Teknoloji Stack'i

### Desktop Uygulaması (Windows/Mac)
- **Framework:** PyQt6 (GUI)
- **Audio Engine:** python-vlc (playback), sounddevice + scipy (equalizer)
- **Streaming:**
  - Spotify: spotipy (Web API)
  - YouTube Music: yt-dlp + ytmusicapi
- **Database:** SQLite (playlists, favorites, history)

### iOS Uygulaması (CarPlay)
- **Language:** Swift 5+
- **UI:** SwiftUI
- **CarPlay:** CarPlay Framework
- **Audio:** AVFoundation
- **Streaming:** Native API clients

### Ortak Backend
- **API Server:** Flask (Python) - Streaming koordinasyonu
- **Cache:** Local file caching for offline
- **Config:** JSON based configuration

## Özellikler ve Modüller

### 1. Streaming Entegrasyonu
**Dosya:** `music_player/streaming/`
- `spotify_client.py` - Spotify Web API integration
- `youtube_music_client.py` - YouTube Music integration
- `stream_manager.py` - Unified streaming interface
- **Ad-blocking:** Custom request filtering, YouTube ad skip

### 2. Playlist Yönetimi
**Dosya:** `music_player/playlist/`
- `playlist_manager.py` - CRUD operations
- `import_export.py` - M3U, JSON, Spotify playlist import/export
- `favorites.py` - Liked songs management
- **Dosya Formatları:** .m3u, .json, .xspf

### 3. Arama Motoru
**Dosya:** `music_player/search/`
- `search_engine.py` - Multi-source search (Spotify, YouTube, local)
- `search_filters.py` - Genre, artist, album filters
- **Cache:** Recent searches

### 4. Ekolayzır (10-Band Equalizer)
**Dosya:** `music_player/audio/`
- `equalizer.py` - 10-band equalizer (31Hz - 16kHz)
- `audio_processor.py` - Real-time DSP
- `presets.py` - Rock, Pop, Jazz, Classical, etc.
- **Teknoloji:** scipy.signal for band-pass filters

### 5. GUI - Ana Oynatıcı
**Dosya:** `music_player/gui/`
- `main_window.py` - Ana pencere
- `player_controls.py` - Play/pause/skip controls
- `playlist_view.py` - Playlist görünümü
- `search_view.py` - Arama arayüzü
- `equalizer_view.py` - Equalizer UI
- `settings_view.py` - Ayarlar

### 6. Mini Player (Windows)
**Dosya:** `music_player/gui/mini_player.py`
- Always-on-top compact player
- Album art + basic controls
- Hotkey support
- System tray integration

### 7. Online Radyo
**Dosya:** `music_player/radio/`
- `radio_browser.py` - Radio Browser API integration
- `radio_player.py` - Live stream playback
- **Kategoriler:** Genre, country, language based
- **Favoriler:** Save favorite radio stations

### 8. CarPlay (iOS)
**Dosya:** `ios_app/CarPlaySupport/`
- CarPlay scene delegate
- Now playing integration
- Voice control support
- Safe driving UI

## Proje Yapısı

```
ogz/
├── music_player/                 # Desktop application
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── config.py                 # Configuration management
│   │
│   ├── streaming/                # Music streaming
│   │   ├── __init__.py
│   │   ├── spotify_client.py
│   │   ├── youtube_music_client.py
│   │   ├── stream_manager.py
│   │   └── ad_blocker.py
│   │
│   ├── audio/                    # Audio processing
│   │   ├── __init__.py
│   │   ├── player.py             # VLC backend
│   │   ├── equalizer.py          # 10-band EQ
│   │   ├── audio_processor.py
│   │   └── presets.py
│   │
│   ├── playlist/                 # Playlist management
│   │   ├── __init__.py
│   │   ├── playlist_manager.py
│   │   ├── import_export.py      # M3U, JSON, XSPF
│   │   └── favorites.py
│   │
│   ├── search/                   # Search engine
│   │   ├── __init__.py
│   │   ├── search_engine.py
│   │   └── search_filters.py
│   │
│   ├── radio/                    # Online radio
│   │   ├── __init__.py
│   │   ├── radio_browser.py
│   │   └── radio_player.py
│   │
│   ├── gui/                      # PyQt6 GUI
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── mini_player.py        # Windows mini mode
│   │   ├── player_controls.py
│   │   ├── playlist_view.py
│   │   ├── search_view.py
│   │   ├── equalizer_view.py
│   │   ├── radio_view.py
│   │   └── settings_view.py
│   │
│   ├── database/                 # SQLite database
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── db_manager.py
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── logger.py
│       └── cache.py
│
├── ios_app/                      # iOS + CarPlay
│   ├── MusicPlayer/
│   │   ├── App/
│   │   ├── Views/
│   │   ├── CarPlaySupport/       # CarPlay integration
│   │   ├── Audio/
│   │   └── Networking/
│   └── MusicPlayer.xcodeproj
│
├── shared/                       # Shared resources
│   ├── api_keys.json.example
│   └── presets.json
│
├── requirements.txt              # Python dependencies
├── README_MUSIC_PLAYER.md        # Music player documentation
└── MUSIC_PLAYER_PLAN.md          # This file
```

## Veritabanı Şeması (SQLite)

```sql
-- Playlists
CREATE TABLE playlists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tracks
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT,
    album TEXT,
    duration INTEGER,
    source TEXT,  -- 'spotify', 'youtube', 'local', 'radio'
    source_id TEXT,
    thumbnail_url TEXT,
    is_favorite BOOLEAN DEFAULT 0
);

-- Playlist tracks (many-to-many)
CREATE TABLE playlist_tracks (
    playlist_id INTEGER,
    track_id INTEGER,
    position INTEGER,
    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);

-- Radio stations
CREATE TABLE radio_stations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    stream_url TEXT NOT NULL,
    genre TEXT,
    country TEXT,
    is_favorite BOOLEAN DEFAULT 0
);

-- Equalizer presets
CREATE TABLE eq_presets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    band_31hz REAL,
    band_62hz REAL,
    band_125hz REAL,
    band_250hz REAL,
    band_500hz REAL,
    band_1khz REAL,
    band_2khz REAL,
    band_4khz REAL,
    band_8khz REAL,
    band_16khz REAL
);
```

## API Entegrasyonları

### Spotify
- **Library:** spotipy
- **Auth:** OAuth 2.0
- **Features:** Search, playlists, playback
- **Rate Limit:** Handled with exponential backoff

### YouTube Music
- **Library:** yt-dlp + ytmusicapi
- **Features:** Search, streaming URLs
- **Ad-blocking:** Custom filtering + sponsor block

### Radio Browser
- **API:** https://api.radio-browser.info
- **Features:** 30,000+ radio stations
- **Filters:** Genre, country, language

## Güvenlik ve Gizlilik

1. **API Keys:** Environment variables + encrypted storage
2. **User Data:** Local SQLite only, no cloud sync (optional)
3. **Ad-blocking:** Client-side filtering
4. **Cache:** Automatic cleanup of old cache files

## Geliştirme Aşamaları

### Phase 1: Core Desktop Application (Week 1-2)
- [ ] Project structure setup
- [ ] Basic PyQt6 GUI
- [ ] VLC audio player integration
- [ ] Basic playlist management
- [ ] SQLite database

### Phase 2: Streaming Integration (Week 3-4)
- [ ] Spotify API integration
- [ ] YouTube Music integration
- [ ] Search functionality
- [ ] Ad-blocking implementation

### Phase 3: Advanced Features (Week 5-6)
- [ ] 10-band equalizer with presets
- [ ] Online radio integration
- [ ] Mini player mode (Windows)
- [ ] Playlist import/export (M3U, JSON)

### Phase 4: iOS + CarPlay (Week 7-8)
- [ ] iOS app with SwiftUI
- [ ] CarPlay framework integration
- [ ] Audio session management
- [ ] Sync with desktop (optional)

### Phase 5: Polish & Testing (Week 9-10)
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] Bug fixes
- [ ] Documentation

## Konfigürasyon Dosyası

`music_player_config.json`:
```json
{
    "audio": {
        "default_volume": 70,
        "equalizer_enabled": true,
        "default_preset": "Flat"
    },
    "streaming": {
        "spotify_enabled": true,
        "youtube_enabled": true,
        "quality": "high",
        "cache_enabled": true,
        "cache_size_mb": 500
    },
    "ui": {
        "theme": "dark",
        "mini_player_on_top": true,
        "show_notifications": true
    },
    "radio": {
        "default_country": "TR",
        "default_genre": "pop"
    },
    "api_keys": {
        "spotify_client_id": "YOUR_CLIENT_ID",
        "spotify_client_secret": "YOUR_CLIENT_SECRET"
    }
}
```

## Gereksinimler

### Desktop (Python 3.10+)
```
PyQt6>=6.4.0
python-vlc>=3.0.0
spotipy>=2.23.0
yt-dlp>=2023.0.0
ytmusicapi>=1.0.0
numpy>=1.24.0
scipy>=1.10.0
sounddevice>=0.4.6
requests>=2.28.0
```

### iOS
- Xcode 14+
- iOS 14+ deployment target
- CarPlay entitlement

## Öne Çıkan Özellikler

✅ **Multi-platform:** Windows, Mac, iOS
✅ **Multi-source:** Spotify, YouTube Music, Radio
✅ **Offline Support:** Playlist caching
✅ **Professional EQ:** 10-band equalizer
✅ **Mini Player:** Windows always-on-top mode
✅ **CarPlay:** Safe driving integration
✅ **Ad-free:** Built-in ad blocking
✅ **Open Format:** M3U, JSON playlist export
✅ **Privacy-first:** Local-only data storage

## Notlar

- **Yasal Uyarı:** Spotify/YouTube API kullanımı terms of service'e uygun olmalı
- **Telif Hakkı:** Sadece streaming, indirme yok
- **Performance:** VLC backend düşük CPU kullanımı sağlar
- **Modüler:** Her modül bağımsız test edilebilir
