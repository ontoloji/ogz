"""
Müzik Çalar - Ana Program
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Config ve Database
from music_player.config import get_config
from music_player.database.models import DatabaseManager

# Audio
from music_player.audio.player import AudioPlayer
from music_player.audio.equalizer import Equalizer

# Streaming
from music_player.streaming.stream_manager import StreamManager

# Playlist
from music_player.playlist.playlist_manager import PlaylistManager
from music_player.playlist.import_export import PlaylistImportExport

# Radio
from music_player.radio.radio_browser import RadioBrowser

# GUI
from music_player.gui.main_window import MainWindow


class MusicPlayerApp:
    """Ana müzik çalar uygulaması"""

    def __init__(self):
        """Uygulama bileşenlerini başlat"""

        # Konfigürasyon
        self.config = get_config()

        # Veritabanı
        db_path = self.config.get_database_path()
        self.db_manager = DatabaseManager(db_path)

        # Audio player
        self.audio_player = AudioPlayer()

        # Equalizer
        self.equalizer = Equalizer()

        # Stream manager
        stream_config = {
            'spotify_enabled': self.config.get('streaming', 'spotify_enabled', default=True),
            'youtube_enabled': self.config.get('streaming', 'youtube_enabled', default=True),
            'spotify_client_id': self.config.get('api_keys', 'spotify_client_id', default=''),
            'spotify_client_secret': self.config.get('api_keys', 'spotify_client_secret', default=''),
        }
        self.stream_manager = StreamManager(stream_config)

        # Playlist manager
        self.playlist_manager = PlaylistManager(self.db_manager)
        self.playlist_import_export = PlaylistImportExport(self.playlist_manager)

        # Radio browser
        self.radio_browser = RadioBrowser()

        # Equalizer'ı player'a bağla
        self._setup_equalizer()

        # Auto-load son kullanılan preset
        self._load_last_settings()

    def _setup_equalizer(self):
        """Equalizer'ı audio player'a bağla"""
        # VLC player'a equalizer değerlerini uygula
        eq_values = self.equalizer.get_vlc_equalizer_values()
        self.audio_player.set_equalizer(eq_values)

    def _load_last_settings(self):
        """Son kullanılan ayarları yükle"""
        # EQ preset
        last_preset = self.config.get('audio', 'default_preset', default='Flat')
        self.equalizer.load_preset(last_preset)

        # Volume
        last_volume = self.config.get('audio', 'default_volume', default=70)
        self.audio_player.set_volume(last_volume)

        # EQ enabled
        eq_enabled = self.config.get('audio', 'equalizer_enabled', default=True)
        self.equalizer.enabled = eq_enabled

    def save_settings(self):
        """Mevcut ayarları kaydet"""
        # EQ preset
        self.config.set('audio', 'default_preset', value=self.equalizer.current_preset)

        # Volume
        self.config.set('audio', 'default_volume', value=self.audio_player.get_volume())

        # EQ enabled
        self.config.set('audio', 'equalizer_enabled', value=self.equalizer.enabled)

    def cleanup(self):
        """Uygulama kapanırken temizlik yap"""
        self.save_settings()
        self.audio_player.release()
        self.db_manager.close()


def main():
    """Ana program başlangıcı"""

    # QApplication oluştur
    app = QApplication(sys.argv)

    # Uygulama bilgileri
    app.setApplicationName("Müzik Çalar")
    app.setOrganizationName("MusicPlayer")
    app.setApplicationVersion("1.0.0")

    # High DPI support
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Müzik çalar uygulamasını başlat
    music_app = MusicPlayerApp()

    # Ana pencere
    main_window = MainWindow(music_app)
    main_window.show()

    # Event loop
    exit_code = app.exec()

    # Cleanup
    music_app.cleanup()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
