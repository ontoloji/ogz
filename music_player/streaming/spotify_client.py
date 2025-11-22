"""
Müzik Çalar - Spotify API Client
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing import List, Dict, Optional, Any
import time


class SpotifyClient:
    """Spotify Web API client"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8888/callback"):
        """
        Spotify client başlat

        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # Scope - kullanıcı verilerine erişim izinleri
        self.scope = "user-library-read user-library-modify playlist-read-private playlist-modify-private user-read-playback-state user-modify-playback-state streaming"

        self.sp: Optional[spotipy.Spotify] = None
        self._initialize()

    def _initialize(self):
        """Spotify API client'ı başlat"""
        try:
            # OAuth ile authentication
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            print(f"Spotify başlatma hatası: {e}")
            # Fallback: Client credentials (kullanıcı verisi yok)
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def search_tracks(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Şarkı ara

        Args:
            query: Arama sorgusu
            limit: Maksimum sonuç sayısı

        Returns:
            Şarkı listesi
        """
        if not self.sp:
            return []

        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []

            for item in results['tracks']['items']:
                track = {
                    'id': item['id'],
                    'title': item['name'],
                    'artist': ', '.join([artist['name'] for artist in item['artists']]),
                    'album': item['album']['name'],
                    'duration': item['duration_ms'] // 1000,  # Saniye cinsinden
                    'thumbnail_url': item['album']['images'][0]['url'] if item['album']['images'] else '',
                    'source': 'spotify',
                    'source_id': item['id'],
                    'spotify_uri': item['uri'],
                    'preview_url': item.get('preview_url', ''),  # 30 sn önizleme
                    'external_url': item['external_urls']['spotify']
                }
                tracks.append(track)

            return tracks

        except Exception as e:
            print(f"Spotify arama hatası: {e}")
            return []

    def get_track_stream_url(self, track_id: str) -> Optional[str]:
        """
        Şarkı stream URL'i al

        NOT: Spotify Web API doğrudan stream URL vermez.
        Preview URL (30 sn) veya Web Playback SDK kullanılmalı.

        Args:
            track_id: Spotify track ID

        Returns:
            Preview URL (30 saniyelik)
        """
        try:
            track = self.sp.track(track_id)
            return track.get('preview_url')  # 30 saniyelik önizleme
        except Exception as e:
            print(f"Spotify track bilgisi alma hatası: {e}")
            return None

    def get_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """
        Playlist bilgilerini al

        Args:
            playlist_id: Spotify playlist ID

        Returns:
            Playlist bilgileri ve şarkılar
        """
        try:
            playlist = self.sp.playlist(playlist_id)

            tracks = []
            for item in playlist['tracks']['items']:
                if item['track']:
                    track = {
                        'id': item['track']['id'],
                        'title': item['track']['name'],
                        'artist': ', '.join([a['name'] for a in item['track']['artists']]),
                        'album': item['track']['album']['name'],
                        'duration': item['track']['duration_ms'] // 1000,
                        'source': 'spotify',
                        'source_id': item['track']['id'],
                        'thumbnail_url': item['track']['album']['images'][0]['url'] if item['track']['album']['images'] else ''
                    }
                    tracks.append(track)

            return {
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'owner': playlist['owner']['display_name'],
                'tracks': tracks,
                'total_tracks': playlist['tracks']['total']
            }

        except Exception as e:
            print(f"Spotify playlist alma hatası: {e}")
            return {}

    def get_user_playlists(self) -> List[Dict[str, Any]]:
        """
        Kullanıcının playlist'lerini al

        Returns:
            Playlist listesi
        """
        try:
            results = self.sp.current_user_playlists()
            playlists = []

            for item in results['items']:
                playlist = {
                    'id': item['id'],
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'owner': item['owner']['display_name'],
                    'tracks_count': item['tracks']['total'],
                    'public': item['public'],
                    'image_url': item['images'][0]['url'] if item['images'] else ''
                }
                playlists.append(playlist)

            return playlists

        except Exception as e:
            print(f"Spotify kullanıcı playlists hatası: {e}")
            return []

    def get_user_saved_tracks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Kullanıcının beğendiği şarkıları al

        Args:
            limit: Maksimum sonuç sayısı

        Returns:
            Şarkı listesi
        """
        try:
            results = self.sp.current_user_saved_tracks(limit=limit)
            tracks = []

            for item in results['items']:
                track = item['track']
                tracks.append({
                    'id': track['id'],
                    'title': track['name'],
                    'artist': ', '.join([a['name'] for a in track['artists']]),
                    'album': track['album']['name'],
                    'duration': track['duration_ms'] // 1000,
                    'source': 'spotify',
                    'source_id': track['id'],
                    'thumbnail_url': track['album']['images'][0]['url'] if track['album']['images'] else ''
                })

            return tracks

        except Exception as e:
            print(f"Spotify saved tracks hatası: {e}")
            return []

    def get_recommendations(self, seed_tracks: List[str] = None,
                           seed_artists: List[str] = None,
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        Öneri şarkıları al

        Args:
            seed_tracks: Başlangıç track ID'leri
            seed_artists: Başlangıç artist ID'leri
            limit: Maksimum sonuç sayısı

        Returns:
            Önerilen şarkı listesi
        """
        try:
            results = self.sp.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists,
                limit=limit
            )

            tracks = []
            for track in results['tracks']:
                tracks.append({
                    'id': track['id'],
                    'title': track['name'],
                    'artist': ', '.join([a['name'] for a in track['artists']]),
                    'album': track['album']['name'],
                    'duration': track['duration_ms'] // 1000,
                    'source': 'spotify',
                    'source_id': track['id'],
                    'thumbnail_url': track['album']['images'][0]['url'] if track['album']['images'] else ''
                })

            return tracks

        except Exception as e:
            print(f"Spotify öneriler hatası: {e}")
            return []

    def is_authenticated(self) -> bool:
        """OAuth authentication durumunu kontrol et"""
        try:
            if self.sp:
                self.sp.current_user()
                return True
        except:
            pass
        return False
