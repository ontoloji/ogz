"""
Müzik Çalar - Audio Player (VLC Backend)
"""
import vlc
from typing import Optional, Callable
from enum import Enum


class PlayerState(Enum):
    """Oynatıcı durumu"""
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2
    BUFFERING = 3


class AudioPlayer:
    """VLC tabanlı audio player"""

    def __init__(self):
        """Audio player başlat"""
        # VLC instance oluştur
        self.instance = vlc.Instance('--no-xlib')  # GUI olmadan
        self.player = self.instance.media_player_new()

        # Durum bilgileri
        self.state = PlayerState.STOPPED
        self.current_url: Optional[str] = None
        self.current_track_info: dict = {}

        # Callback'ler
        self.on_position_changed: Optional[Callable[[float], None]] = None
        self.on_state_changed: Optional[Callable[[PlayerState], None]] = None
        self.on_track_ended: Optional[Callable[[], None]] = None

        # Event manager
        self.event_manager = self.player.event_manager()
        self._setup_events()

    def _setup_events(self):
        """VLC event handler'larını ayarla"""
        self.event_manager.event_attach(
            vlc.EventType.MediaPlayerPlaying,
            self._on_playing
        )
        self.event_manager.event_attach(
            vlc.EventType.MediaPlayerPaused,
            self._on_paused
        )
        self.event_manager.event_attach(
            vlc.EventType.MediaPlayerStopped,
            self._on_stopped
        )
        self.event_manager.event_attach(
            vlc.EventType.MediaPlayerEndReached,
            self._on_end_reached
        )
        self.event_manager.event_attach(
            vlc.EventType.MediaPlayerPositionChanged,
            self._on_position_update
        )

    def _on_playing(self, event):
        """Playing event handler"""
        self.state = PlayerState.PLAYING
        if self.on_state_changed:
            self.on_state_changed(self.state)

    def _on_paused(self, event):
        """Paused event handler"""
        self.state = PlayerState.PAUSED
        if self.on_state_changed:
            self.on_state_changed(self.state)

    def _on_stopped(self, event):
        """Stopped event handler"""
        self.state = PlayerState.STOPPED
        if self.on_state_changed:
            self.on_state_changed(self.state)

    def _on_end_reached(self, event):
        """End reached event handler"""
        self.state = PlayerState.STOPPED
        if self.on_track_ended:
            self.on_track_ended()

    def _on_position_update(self, event):
        """Position update event handler"""
        position = self.get_position()
        if self.on_position_changed:
            self.on_position_changed(position)

    def play(self, url: str, track_info: dict = None):
        """
        Şarkıyı çal

        Args:
            url: Şarkı URL'i (stream URL veya dosya yolu)
            track_info: Şarkı bilgileri (title, artist, album, etc.)
        """
        self.current_url = url
        self.current_track_info = track_info or {}

        # Media oluştur ve oynat
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.player.play()

        self.state = PlayerState.PLAYING

    def pause(self):
        """Oynatmayı duraklat"""
        if self.state == PlayerState.PLAYING:
            self.player.pause()
            self.state = PlayerState.PAUSED

    def resume(self):
        """Oynatmaya devam et"""
        if self.state == PlayerState.PAUSED:
            self.player.play()
            self.state = PlayerState.PLAYING

    def toggle_play_pause(self):
        """Play/Pause toggle"""
        if self.state == PlayerState.PLAYING:
            self.pause()
        elif self.state == PlayerState.PAUSED:
            self.resume()

    def stop(self):
        """Oynatmayı durdur"""
        self.player.stop()
        self.state = PlayerState.STOPPED
        self.current_url = None

    def set_volume(self, volume: int):
        """
        Ses seviyesini ayarla

        Args:
            volume: 0-100 arası ses seviyesi
        """
        volume = max(0, min(100, volume))
        self.player.audio_set_volume(volume)

    def get_volume(self) -> int:
        """Mevcut ses seviyesini al"""
        return self.player.audio_get_volume()

    def set_position(self, position: float):
        """
        Oynatma pozisyonunu ayarla

        Args:
            position: 0.0-1.0 arası pozisyon
        """
        position = max(0.0, min(1.0, position))
        self.player.set_position(position)

    def get_position(self) -> float:
        """Mevcut oynatma pozisyonunu al (0.0-1.0)"""
        return self.player.get_position()

    def get_time(self) -> int:
        """Mevcut oynatma zamanını al (milisaniye)"""
        return self.player.get_time()

    def get_length(self) -> int:
        """Toplam şarkı uzunluğunu al (milisaniye)"""
        return self.player.get_length()

    def set_equalizer(self, bands: list):
        """
        10-band equalizer ayarla

        Args:
            bands: 10 elemanlı liste, her biri -20 ile +20 dB arası
        """
        if len(bands) != 10:
            raise ValueError("10 band değeri gerekli")

        # VLC equalizer oluştur
        equalizer = vlc.AudioEqualizer()
        equalizer.set_preamp(0)  # Preamplifier

        # Band frekansları (Hz): 31, 62, 125, 250, 500, 1k, 2k, 4k, 8k, 16k
        for i, amp in enumerate(bands):
            # Değerleri -20 ile +20 dB arasında sınırla
            amp = max(-20, min(20, amp))
            equalizer.set_amp_at_index(amp, i)

        # Equalizer'ı player'a uygula
        self.player.set_equalizer(equalizer)

    def is_playing(self) -> bool:
        """Oynatma durumunu kontrol et"""
        return self.state == PlayerState.PLAYING

    def is_paused(self) -> bool:
        """Duraklama durumunu kontrol et"""
        return self.state == PlayerState.PAUSED

    def get_current_track(self) -> dict:
        """Mevcut çalan şarkı bilgilerini al"""
        return self.current_track_info.copy()

    def release(self):
        """Kaynakları serbest bırak"""
        self.stop()
        self.player.release()
        self.instance.release()
