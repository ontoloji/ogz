"""
Müzik Çalar - YouTube Music Client
"""
from ytmusicapi import YTMusic
import yt_dlp
from typing import List, Dict, Optional, Any
import re


class YouTubeMusicClient:
    """YouTube Music API client"""

    def __init__(self):
        """YouTube Music client başlat"""
        try:
            self.ytmusic = YTMusic()
        except Exception as e:
            print(f"YTMusic başlatma hatası: {e}")
            self.ytmusic = None

        # yt-dlp ayarları (stream URL almak için)
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
        }

    def search_tracks(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Şarkı ara

        Args:
            query: Arama sorgusu
            limit: Maksimum sonuç sayısı

        Returns:
            Şarkı listesi
        """
        if not self.ytmusic:
            return []

        try:
            results = self.ytmusic.search(query, filter='songs', limit=limit)
            tracks = []

            for item in results:
                # Artist bilgisi
                artists = item.get('artists', [])
                artist_name = artists[0]['name'] if artists else 'Unknown Artist'

                # Album bilgisi
                album = item.get('album', {})
                album_name = album.get('name', '') if album else ''

                # Duration
                duration_text = item.get('duration', '0:00')
                duration = self._parse_duration(duration_text)

                # Thumbnail
                thumbnails = item.get('thumbnails', [])
                thumbnail_url = thumbnails[-1]['url'] if thumbnails else ''

                track = {
                    'id': item.get('videoId', ''),
                    'title': item.get('title', 'Unknown'),
                    'artist': artist_name,
                    'album': album_name,
                    'duration': duration,
                    'thumbnail_url': thumbnail_url,
                    'source': 'youtube',
                    'source_id': item.get('videoId', ''),
                    'is_explicit': item.get('isExplicit', False)
                }
                tracks.append(track)

            return tracks

        except Exception as e:
            print(f"YouTube Music arama hatası: {e}")
            return []

    def get_track_stream_url(self, video_id: str) -> Optional[str]:
        """
        Şarkı stream URL'i al (yt-dlp kullanarak)

        Args:
            video_id: YouTube video ID

        Returns:
            Stream URL
        """
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # En iyi audio formatını seç
                formats = info.get('formats', [])
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']

                if audio_formats:
                    # En yüksek kaliteli audio formatını seç
                    best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
                    return best_audio.get('url')
                elif formats:
                    # Fallback: Herhangi bir format
                    return formats[0].get('url')

            return None

        except Exception as e:
            print(f"YouTube stream URL alma hatası: {e}")
            return None

    def get_album(self, browse_id: str) -> Dict[str, Any]:
        """
        Album bilgilerini al

        Args:
            browse_id: YouTube Music album browse ID

        Returns:
            Album bilgileri ve şarkılar
        """
        if not self.ytmusic:
            return {}

        try:
            album = self.ytmusic.get_album(browse_id)

            tracks = []
            for track in album.get('tracks', []):
                duration = self._parse_duration(track.get('duration', '0:00'))

                tracks.append({
                    'id': track.get('videoId', ''),
                    'title': track.get('title', ''),
                    'artist': album.get('artist', ''),
                    'album': album.get('title', ''),
                    'duration': duration,
                    'source': 'youtube',
                    'source_id': track.get('videoId', '')
                })

            return {
                'id': browse_id,
                'title': album.get('title', ''),
                'artist': album.get('artist', ''),
                'year': album.get('year', ''),
                'tracks': tracks,
                'thumbnail_url': album.get('thumbnails', [{}])[-1].get('url', '')
            }

        except Exception as e:
            print(f"YouTube Music album alma hatası: {e}")
            return {}

    def get_playlist(self, playlist_id: str, limit: int = 100) -> Dict[str, Any]:
        """
        Playlist bilgilerini al

        Args:
            playlist_id: YouTube Music playlist ID
            limit: Maksimum track sayısı

        Returns:
            Playlist bilgileri
        """
        if not self.ytmusic:
            return {}

        try:
            playlist = self.ytmusic.get_playlist(playlist_id, limit=limit)

            tracks = []
            for track in playlist.get('tracks', []):
                artists = track.get('artists', [])
                artist_name = artists[0]['name'] if artists else 'Unknown'

                album = track.get('album', {})
                album_name = album.get('name', '') if album else ''

                duration = self._parse_duration(track.get('duration', '0:00'))

                thumbnails = track.get('thumbnails', [])
                thumbnail_url = thumbnails[-1]['url'] if thumbnails else ''

                tracks.append({
                    'id': track.get('videoId', ''),
                    'title': track.get('title', ''),
                    'artist': artist_name,
                    'album': album_name,
                    'duration': duration,
                    'source': 'youtube',
                    'source_id': track.get('videoId', ''),
                    'thumbnail_url': thumbnail_url
                })

            return {
                'id': playlist_id,
                'title': playlist.get('title', ''),
                'description': playlist.get('description', ''),
                'author': playlist.get('author', {}).get('name', ''),
                'tracks': tracks,
                'track_count': playlist.get('trackCount', len(tracks))
            }

        except Exception as e:
            print(f"YouTube Music playlist alma hatası: {e}")
            return {}

    def get_artist_info(self, browse_id: str) -> Dict[str, Any]:
        """
        Artist bilgilerini al

        Args:
            browse_id: YouTube Music artist browse ID

        Returns:
            Artist bilgileri
        """
        if not self.ytmusic:
            return {}

        try:
            artist = self.ytmusic.get_artist(browse_id)

            # En popüler şarkılar
            top_tracks = []
            for track in artist.get('songs', {}).get('results', [])[:10]:
                duration = self._parse_duration(track.get('duration', '0:00'))

                top_tracks.append({
                    'id': track.get('videoId', ''),
                    'title': track.get('title', ''),
                    'artist': artist.get('name', ''),
                    'duration': duration,
                    'source': 'youtube',
                    'source_id': track.get('videoId', '')
                })

            return {
                'id': browse_id,
                'name': artist.get('name', ''),
                'description': artist.get('description', ''),
                'subscribers': artist.get('subscribers', ''),
                'top_tracks': top_tracks
            }

        except Exception as e:
            print(f"YouTube Music artist bilgisi alma hatası: {e}")
            return {}

    def get_trending_tracks(self) -> List[Dict[str, Any]]:
        """
        Trend şarkıları al

        Returns:
            Trend şarkı listesi
        """
        # YTMusic API'de doğrudan trending endpoint yok, "Top songs" kullanabiliriz
        return self.search_tracks("top songs 2024", limit=20)

    def _parse_duration(self, duration_str: str) -> int:
        """
        Duration string'i saniyeye çevir

        Args:
            duration_str: "3:45" formatında string

        Returns:
            Saniye cinsinden süre
        """
        if not duration_str:
            return 0

        try:
            # Format: "MM:SS" veya "HH:MM:SS"
            parts = duration_str.split(':')
            parts = [int(p) for p in parts]

            if len(parts) == 2:  # MM:SS
                return parts[0] * 60 + parts[1]
            elif len(parts) == 3:  # HH:MM:SS
                return parts[0] * 3600 + parts[1] * 60 + parts[2]

            return 0
        except:
            return 0

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        YouTube URL'den video ID çıkar

        Args:
            url: YouTube URL

        Returns:
            Video ID
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?]+)',
            r'youtube\.com/embed/([^&\n?]+)',
            r'youtube\.com/v/([^&\n?]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def is_available(self) -> bool:
        """YouTube Music servisinin kullanılabilir olup olmadığını kontrol et"""
        return self.ytmusic is not None
