"""
Müzik Çalar - Stream Manager (Unified Interface)
"""
from typing import List, Dict, Optional, Any
from .spotify_client import SpotifyClient
from .youtube_music_client import YouTubeMusicClient
from .ad_blocker import AdBlocker


class StreamManager:
    """Tüm streaming servislerini yöneten unified interface"""

    def __init__(self, config: dict):
        """
        Stream manager başlat

        Args:
            config: Konfigürasyon dictionary
        """
        self.config = config

        # Spotify client
        self.spotify: Optional[SpotifyClient] = None
        if config.get('spotify_enabled', False):
            spotify_id = config.get('spotify_client_id', '')
            spotify_secret = config.get('spotify_client_secret', '')
            if spotify_id and spotify_secret:
                try:
                    self.spotify = SpotifyClient(spotify_id, spotify_secret)
                except Exception as e:
                    print(f"Spotify başlatma hatası: {e}")

        # YouTube Music client
        self.youtube: Optional[YouTubeMusicClient] = None
        if config.get('youtube_enabled', False):
            try:
                self.youtube = YouTubeMusicClient()
            except Exception as e:
                print(f"YouTube Music başlatma hatası: {e}")

        # Ad blocker
        self.ad_blocker = AdBlocker()

    def search_all(self, query: str, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """
        Tüm servislerde arama yap

        Args:
            query: Arama sorgusu
            limit: Her servis için maksimum sonuç sayısı

        Returns:
            {'spotify': [...], 'youtube': [...]}
        """
        results = {
            'spotify': [],
            'youtube': []
        }

        # Spotify'da ara
        if self.spotify:
            try:
                results['spotify'] = self.spotify.search_tracks(query, limit)
            except Exception as e:
                print(f"Spotify arama hatası: {e}")

        # YouTube Music'te ara
        if self.youtube:
            try:
                results['youtube'] = self.youtube.search_tracks(query, limit)
            except Exception as e:
                print(f"YouTube arama hatası: {e}")

        return results

    def search(self, query: str, source: str = 'all', limit: int = 20) -> List[Dict[str, Any]]:
        """
        Belirtilen serviste arama yap

        Args:
            query: Arama sorgusu
            source: 'spotify', 'youtube', veya 'all'
            limit: Maksimum sonuç sayısı

        Returns:
            Şarkı listesi
        """
        if source == 'all':
            results = self.search_all(query, limit)
            # İki listeyi birleştir, sırayla ekle
            combined = []
            max_len = max(len(results['spotify']), len(results['youtube']))
            for i in range(max_len):
                if i < len(results['spotify']):
                    combined.append(results['spotify'][i])
                if i < len(results['youtube']):
                    combined.append(results['youtube'][i])
            return combined[:limit * 2]  # Toplam limit

        elif source == 'spotify' and self.spotify:
            return self.spotify.search_tracks(query, limit)

        elif source == 'youtube' and self.youtube:
            return self.youtube.search_tracks(query, limit)

        return []

    def get_stream_url(self, track: Dict[str, Any]) -> Optional[str]:
        """
        Şarkı için stream URL al

        Args:
            track: Track bilgileri (source ve source_id içermeli)

        Returns:
            Stream URL
        """
        source = track.get('source', '')
        source_id = track.get('source_id', '')

        if not source_id:
            return None

        url = None

        # Spotify
        if source == 'spotify' and self.spotify:
            url = self.spotify.get_track_stream_url(source_id)

        # YouTube Music
        elif source == 'youtube' and self.youtube:
            url = self.youtube.get_track_stream_url(source_id)

        # Ad blocker ile kontrol et
        if url and self.ad_blocker.is_ad(url):
            print("Reklam engellendi")
            return None

        return url

    def get_playlist(self, playlist_id: str, source: str) -> Dict[str, Any]:
        """
        Playlist bilgilerini al

        Args:
            playlist_id: Playlist ID
            source: 'spotify' veya 'youtube'

        Returns:
            Playlist bilgileri
        """
        if source == 'spotify' and self.spotify:
            return self.spotify.get_playlist(playlist_id)
        elif source == 'youtube' and self.youtube:
            return self.youtube.get_playlist(playlist_id)

        return {}

    def get_user_playlists(self, source: str) -> List[Dict[str, Any]]:
        """
        Kullanıcının playlist'lerini al

        Args:
            source: 'spotify' veya 'youtube'

        Returns:
            Playlist listesi
        """
        if source == 'spotify' and self.spotify:
            return self.spotify.get_user_playlists()

        return []

    def get_favorites(self, source: str) -> List[Dict[str, Any]]:
        """
        Beğenilen şarkıları al

        Args:
            source: 'spotify'

        Returns:
            Şarkı listesi
        """
        if source == 'spotify' and self.spotify:
            return self.spotify.get_user_saved_tracks(limit=50)

        return []

    def get_recommendations(self, seed_track: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """
        Benzer şarkı önerileri al

        Args:
            seed_track: Başlangıç şarkısı
            limit: Maksimum öneri sayısı

        Returns:
            Önerilen şarkı listesi
        """
        source = seed_track.get('source', '')

        if source == 'spotify' and self.spotify:
            seed_id = seed_track.get('source_id', '')
            if seed_id:
                return self.spotify.get_recommendations(seed_tracks=[seed_id], limit=limit)

        elif source == 'youtube' and self.youtube:
            # YouTube için benzer arama yap
            query = f"{seed_track.get('artist', '')} {seed_track.get('title', '')}"
            return self.youtube.search_tracks(query, limit=limit)

        return []

    def is_spotify_available(self) -> bool:
        """Spotify servisinin kullanılabilir olup olmadığını kontrol et"""
        return self.spotify is not None and self.spotify.is_authenticated()

    def is_youtube_available(self) -> bool:
        """YouTube Music servisinin kullanılabilir olup olmadığını kontrol et"""
        return self.youtube is not None and self.youtube.is_available()

    def get_available_sources(self) -> List[str]:
        """Kullanılabilir servisleri listele"""
        sources = []
        if self.is_spotify_available():
            sources.append('spotify')
        if self.is_youtube_available():
            sources.append('youtube')
        return sources
