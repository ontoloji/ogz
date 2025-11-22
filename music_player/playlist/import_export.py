"""
Müzik Çalar - Playlist Import/Export (M3U, JSON)
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


class PlaylistImportExport:
    """Playlist import/export işlemleri"""

    def __init__(self, playlist_manager):
        """
        Import/Export manager başlat

        Args:
            playlist_manager: PlaylistManager instance
        """
        self.playlist_manager = playlist_manager

    # === M3U EXPORT ===

    def export_to_m3u(self, playlist_id: int, filepath: Path, extended: bool = True) -> bool:
        """
        Playlist'i M3U formatında export et

        Args:
            playlist_id: Export edilecek playlist ID
            filepath: Hedef dosya yolu
            extended: Extended M3U (EXTM3U) kullan

        Returns:
            True: Başarılı, False: Hata
        """
        try:
            metadata = self.playlist_manager.export_playlist_metadata(playlist_id)
            tracks = metadata['tracks']

            with open(filepath, 'w', encoding='utf-8') as f:
                if extended:
                    # Extended M3U header
                    f.write("#EXTM3U\n")
                    f.write(f"#PLAYLIST:{metadata['name']}\n")
                    if metadata['description']:
                        f.write(f"#DESCRIPTION:{metadata['description']}\n")
                    f.write("\n")

                for track in tracks:
                    if extended:
                        # #EXTINF:duration,artist - title
                        duration = track.get('duration', -1)
                        artist = track.get('artist', '')
                        title = track.get('title', 'Unknown')

                        f.write(f"#EXTINF:{duration},{artist} - {title}\n")

                        # Ek bilgiler
                        if track.get('album'):
                            f.write(f"#EXTALB:{track['album']}\n")
                        if track.get('thumbnail_url'):
                            f.write(f"#EXTIMG:{track['thumbnail_url']}\n")

                    # URL veya file path
                    # Şimdilik source_id'yi URL olarak kullan
                    url = self._generate_track_url(track)
                    if url:
                        f.write(f"{url}\n")

                    if extended:
                        f.write("\n")

            return True

        except Exception as e:
            print(f"M3U export hatası: {e}")
            return False

    # === M3U IMPORT ===

    def import_from_m3u(self, filepath: Path, playlist_name: str = None) -> Optional[int]:
        """
        M3U dosyasından playlist import et

        Args:
            filepath: M3U dosya yolu
            playlist_name: Yeni playlist adı (None ise dosya adı)

        Returns:
            Yeni playlist ID veya None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Playlist adı
            if playlist_name is None:
                playlist_name = filepath.stem

            # Parse M3U
            is_extended = lines[0].strip() == "#EXTM3U"
            tracks = []

            current_track = {}
            for line in lines:
                line = line.strip()

                if not line or line.startswith("#EXTM3U"):
                    continue

                # EXTINF: duration,artist - title
                if line.startswith("#EXTINF:"):
                    match = re.match(r"#EXTINF:(-?\d+),(.+)", line)
                    if match:
                        duration = int(match.group(1))
                        info = match.group(2)

                        # Parse "artist - title"
                        if ' - ' in info:
                            artist, title = info.split(' - ', 1)
                        else:
                            artist, title = '', info

                        current_track = {
                            'duration': duration if duration >= 0 else 0,
                            'artist': artist.strip(),
                            'title': title.strip()
                        }

                # EXTALB: album
                elif line.startswith("#EXTALB:"):
                    album = line.replace("#EXTALB:", "").strip()
                    if current_track:
                        current_track['album'] = album

                # EXTIMG: thumbnail
                elif line.startswith("#EXTIMG:"):
                    thumbnail = line.replace("#EXTIMG:", "").strip()
                    if current_track:
                        current_track['thumbnail_url'] = thumbnail

                # URL veya file path
                elif not line.startswith("#"):
                    if current_track:
                        current_track['url'] = line
                        tracks.append(current_track)
                        current_track = {}
                    else:
                        # Extended olmayan M3U
                        tracks.append({'url': line, 'title': Path(line).name})

            # Playlist oluştur ve şarkıları ekle
            playlist_id = self.playlist_manager.create_playlist(playlist_name)

            for track_data in tracks:
                # URL'den source ve source_id çıkar
                source, source_id = self._parse_track_url(track_data.get('url', ''))

                track = {
                    'title': track_data.get('title', 'Unknown'),
                    'artist': track_data.get('artist', ''),
                    'album': track_data.get('album', ''),
                    'duration': track_data.get('duration', 0),
                    'source': source,
                    'source_id': source_id,
                    'thumbnail_url': track_data.get('thumbnail_url', '')
                }

                self.playlist_manager.add_track_to_playlist(playlist_id, track)

            return playlist_id

        except Exception as e:
            print(f"M3U import hatası: {e}")
            return None

    # === JSON EXPORT ===

    def export_to_json(self, playlist_id: int, filepath: Path) -> bool:
        """
        Playlist'i JSON formatında export et

        Args:
            playlist_id: Export edilecek playlist ID
            filepath: Hedef dosya yolu

        Returns:
            True: Başarılı, False: Hata
        """
        try:
            metadata = self.playlist_manager.export_playlist_metadata(playlist_id)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"JSON export hatası: {e}")
            return False

    # === JSON IMPORT ===

    def import_from_json(self, filepath: Path) -> Optional[int]:
        """
        JSON dosyasından playlist import et

        Args:
            filepath: JSON dosya yolu

        Returns:
            Yeni playlist ID veya None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            playlist_id = self.playlist_manager.import_playlist_from_metadata(metadata)
            return playlist_id

        except Exception as e:
            print(f"JSON import hatası: {e}")
            return None

    # === XSPF EXPORT (XML Shareable Playlist Format) ===

    def export_to_xspf(self, playlist_id: int, filepath: Path) -> bool:
        """
        Playlist'i XSPF formatında export et

        Args:
            playlist_id: Export edilecek playlist ID
            filepath: Hedef dosya yolu

        Returns:
            True: Başarılı, False: Hata
        """
        try:
            metadata = self.playlist_manager.export_playlist_metadata(playlist_id)
            tracks = metadata['tracks']

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<playlist version="1" xmlns="http://xspf.org/ns/0/">\n')
                f.write(f'  <title>{self._xml_escape(metadata["name"])}</title>\n')

                if metadata['description']:
                    f.write(f'  <annotation>{self._xml_escape(metadata["description"])}</annotation>\n')

                f.write('  <trackList>\n')

                for track in tracks:
                    f.write('    <track>\n')
                    f.write(f'      <title>{self._xml_escape(track.get("title", ""))}</title>\n')
                    f.write(f'      <creator>{self._xml_escape(track.get("artist", ""))}</creator>\n')
                    f.write(f'      <album>{self._xml_escape(track.get("album", ""))}</album>\n')
                    f.write(f'      <duration>{track.get("duration", 0) * 1000}</duration>\n')  # milliseconds

                    url = self._generate_track_url(track)
                    if url:
                        f.write(f'      <location>{self._xml_escape(url)}</location>\n')

                    if track.get('thumbnail_url'):
                        f.write(f'      <image>{self._xml_escape(track["thumbnail_url"])}</image>\n')

                    f.write('    </track>\n')

                f.write('  </trackList>\n')
                f.write('</playlist>\n')

            return True

        except Exception as e:
            print(f"XSPF export hatası: {e}")
            return False

    # === SPOTIFY PLAYLIST IMPORT ===

    def import_from_spotify_url(self, spotify_url: str, stream_manager) -> Optional[int]:
        """
        Spotify playlist URL'den import et

        Args:
            spotify_url: Spotify playlist URL veya ID
            stream_manager: StreamManager instance

        Returns:
            Yeni playlist ID veya None
        """
        try:
            if not stream_manager.spotify:
                print("Spotify bağlantısı yok")
                return None

            # URL'den playlist ID çıkar
            playlist_id_match = re.search(r'playlist/([a-zA-Z0-9]+)', spotify_url)
            if playlist_id_match:
                spotify_playlist_id = playlist_id_match.group(1)
            else:
                spotify_playlist_id = spotify_url  # Direkt ID verilmiş

            # Spotify'dan playlist al
            playlist_data = stream_manager.spotify.get_playlist(spotify_playlist_id)

            if not playlist_data:
                print("Spotify playlist bulunamadı")
                return None

            # Yeni playlist oluştur
            new_playlist_id = self.playlist_manager.create_playlist(
                name=playlist_data['name'],
                description=playlist_data.get('description', '')
            )

            # Şarkıları ekle
            for track in playlist_data.get('tracks', []):
                self.playlist_manager.add_track_to_playlist(new_playlist_id, track)

            return new_playlist_id

        except Exception as e:
            print(f"Spotify import hatası: {e}")
            return None

    # === HELPER METHODS ===

    def _generate_track_url(self, track: Dict[str, Any]) -> str:
        """
        Track bilgilerinden URL oluştur

        Args:
            track: Track bilgileri

        Returns:
            URL
        """
        source = track.get('source', '')
        source_id = track.get('source_id', '')

        if source == 'spotify':
            return f"spotify:track:{source_id}"
        elif source == 'youtube':
            return f"https://www.youtube.com/watch?v={source_id}"
        elif source == 'local':
            return source_id  # File path

        return ""

    def _parse_track_url(self, url: str) -> tuple:
        """
        URL'den source ve source_id çıkar

        Args:
            url: Track URL

        Returns:
            (source, source_id) tuple
        """
        if url.startswith("spotify:track:"):
            return ('spotify', url.replace("spotify:track:", ""))

        elif 'youtube.com/watch?v=' in url or 'youtu.be/' in url:
            # YouTube video ID çıkar
            patterns = [
                r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return ('youtube', match.group(1))

        elif url.startswith('http://') or url.startswith('https://'):
            return ('radio', url)  # Online radio stream

        else:
            # Local file
            return ('local', url)

        return ('unknown', url)

    def _xml_escape(self, text: str) -> str:
        """XML için özel karakterleri escape et"""
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }

        for char, escape in replacements.items():
            text = text.replace(char, escape)

        return text

    def get_supported_formats(self) -> List[str]:
        """Desteklenen dosya formatlarını listele"""
        return ['m3u', 'm3u8', 'json', 'xspf']

    def auto_detect_format(self, filepath: Path) -> Optional[str]:
        """Dosya formatını otomatik tespit et"""
        extension = filepath.suffix.lower().lstrip('.')

        if extension in ['m3u', 'm3u8']:
            return 'm3u'
        elif extension == 'json':
            return 'json'
        elif extension == 'xspf':
            return 'xspf'

        return None
