"""
Müzik Çalar - Playlist Yönetimi
"""
from typing import List, Dict, Optional, Any
from pathlib import Path
import json


class PlaylistManager:
    """Playlist CRUD operasyonları"""

    def __init__(self, db_manager):
        """
        Playlist manager başlat

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def create_playlist(self, name: str, description: str = "") -> int:
        """
        Yeni playlist oluştur

        Args:
            name: Playlist adı
            description: Açıklama

        Returns:
            Playlist ID
        """
        return self.db.create_playlist(name, description)

    def delete_playlist(self, playlist_id: int):
        """
        Playlist sil

        Args:
            playlist_id: Silinecek playlist ID
        """
        self.db.delete_playlist(playlist_id)

    def rename_playlist(self, playlist_id: int, new_name: str):
        """
        Playlist adını değiştir

        Args:
            playlist_id: Playlist ID
            new_name: Yeni isim
        """
        self.db.update_playlist(playlist_id, name=new_name)

    def update_playlist_description(self, playlist_id: int, description: str):
        """
        Playlist açıklamasını güncelle

        Args:
            playlist_id: Playlist ID
            description: Yeni açıklama
        """
        self.db.update_playlist(playlist_id, description=description)

    def get_all_playlists(self) -> List[Dict[str, Any]]:
        """
        Tüm playlist'leri getir

        Returns:
            Playlist listesi
        """
        return self.db.get_playlists()

    def get_playlist(self, playlist_id: int) -> Optional[Dict[str, Any]]:
        """
        Belirli bir playlist'i getir

        Args:
            playlist_id: Playlist ID

        Returns:
            Playlist bilgileri
        """
        playlists = self.db.get_playlists()
        for playlist in playlists:
            if playlist['id'] == playlist_id:
                return playlist
        return None

    def add_track_to_playlist(self, playlist_id: int, track: Dict[str, Any]):
        """
        Playlist'e şarkı ekle

        Args:
            playlist_id: Playlist ID
            track: Şarkı bilgileri
        """
        # Önce track'i veritabanına ekle (veya mevcut ID'yi al)
        track_id = self.db.add_track(
            title=track.get('title', ''),
            artist=track.get('artist', ''),
            album=track.get('album', ''),
            duration=track.get('duration', 0),
            source=track.get('source', ''),
            source_id=track.get('source_id', ''),
            thumbnail_url=track.get('thumbnail_url', '')
        )

        # Playlist'e ekle
        self.db.add_track_to_playlist(playlist_id, track_id)

    def remove_track_from_playlist(self, playlist_id: int, track_id: int):
        """
        Playlist'ten şarkı çıkar

        Args:
            playlist_id: Playlist ID
            track_id: Track ID
        """
        self.db.remove_track_from_playlist(playlist_id, track_id)

    def get_playlist_tracks(self, playlist_id: int) -> List[Dict[str, Any]]:
        """
        Playlist'teki şarkıları getir

        Args:
            playlist_id: Playlist ID

        Returns:
            Şarkı listesi
        """
        return self.db.get_playlist_tracks(playlist_id)

    def clear_playlist(self, playlist_id: int):
        """
        Playlist'teki tüm şarkıları sil

        Args:
            playlist_id: Playlist ID
        """
        tracks = self.get_playlist_tracks(playlist_id)
        for track in tracks:
            self.db.remove_track_from_playlist(playlist_id, track['id'])

    def duplicate_playlist(self, playlist_id: int, new_name: str = None) -> int:
        """
        Playlist'i kopyala

        Args:
            playlist_id: Kopyalanacak playlist ID
            new_name: Yeni playlist adı (None ise "Copy of X")

        Returns:
            Yeni playlist ID
        """
        original = self.get_playlist(playlist_id)
        if not original:
            raise ValueError(f"Playlist {playlist_id} bulunamadı")

        # Yeni isim belirle
        if new_name is None:
            new_name = f"Copy of {original['name']}"

        # Yeni playlist oluştur
        new_playlist_id = self.create_playlist(new_name, original.get('description', ''))

        # Şarkıları kopyala
        tracks = self.get_playlist_tracks(playlist_id)
        for track in tracks:
            self.db.add_track_to_playlist(new_playlist_id, track['id'])

        return new_playlist_id

    def merge_playlists(self, playlist_ids: List[int], new_name: str) -> int:
        """
        Birden fazla playlist'i birleştir

        Args:
            playlist_ids: Birleştirilecek playlist ID'leri
            new_name: Yeni playlist adı

        Returns:
            Yeni playlist ID
        """
        new_playlist_id = self.create_playlist(new_name)

        # Tüm şarkıları ekle (duplicate'ler otomatik filtrelenir)
        for playlist_id in playlist_ids:
            tracks = self.get_playlist_tracks(playlist_id)
            for track in tracks:
                try:
                    self.db.add_track_to_playlist(new_playlist_id, track['id'])
                except:
                    pass  # Duplicate, skip

        return new_playlist_id

    def get_playlist_duration(self, playlist_id: int) -> int:
        """
        Playlist toplam süresini hesapla

        Args:
            playlist_id: Playlist ID

        Returns:
            Toplam süre (saniye)
        """
        tracks = self.get_playlist_tracks(playlist_id)
        return sum(track.get('duration', 0) for track in tracks)

    def search_in_playlist(self, playlist_id: int, query: str) -> List[Dict[str, Any]]:
        """
        Playlist içinde ara

        Args:
            playlist_id: Playlist ID
            query: Arama sorgusu

        Returns:
            Eşleşen şarkılar
        """
        tracks = self.get_playlist_tracks(playlist_id)
        query_lower = query.lower()

        results = []
        for track in tracks:
            if (query_lower in track.get('title', '').lower() or
                query_lower in track.get('artist', '').lower() or
                query_lower in track.get('album', '').lower()):
                results.append(track)

        return results

    def reorder_tracks(self, playlist_id: int, track_positions: List[tuple]):
        """
        Playlist'teki şarkı sırasını değiştir

        Args:
            playlist_id: Playlist ID
            track_positions: [(track_id, new_position), ...] listesi
        """
        # Bu özellik için veritabanı güncellemesi gerekiyor
        # Şimdilik basit implementasyon:
        for track_id, new_position in track_positions:
            # Update position in playlist_tracks table
            self.db.connection.execute("""
                UPDATE playlist_tracks
                SET position = ?
                WHERE playlist_id = ? AND track_id = ?
            """, (new_position, playlist_id, track_id))

        self.db.connection.commit()

    def shuffle_playlist(self, playlist_id: int):
        """
        Playlist'i karıştır

        Args:
            playlist_id: Playlist ID
        """
        import random

        tracks = self.get_playlist_tracks(playlist_id)
        track_ids = [t['id'] for t in tracks]

        # Karıştır
        random.shuffle(track_ids)

        # Yeni sırayla güncelle
        positions = [(track_id, i + 1) for i, track_id in enumerate(track_ids)]
        self.reorder_tracks(playlist_id, positions)

    def export_playlist_metadata(self, playlist_id: int) -> Dict[str, Any]:
        """
        Playlist metadata'sını export formatında al

        Args:
            playlist_id: Playlist ID

        Returns:
            Export için hazır metadata
        """
        playlist = self.get_playlist(playlist_id)
        tracks = self.get_playlist_tracks(playlist_id)

        return {
            'name': playlist.get('name', ''),
            'description': playlist.get('description', ''),
            'track_count': len(tracks),
            'total_duration': self.get_playlist_duration(playlist_id),
            'created_at': playlist.get('created_at', ''),
            'updated_at': playlist.get('updated_at', ''),
            'tracks': [
                {
                    'title': t.get('title', ''),
                    'artist': t.get('artist', ''),
                    'album': t.get('album', ''),
                    'duration': t.get('duration', 0),
                    'source': t.get('source', ''),
                    'source_id': t.get('source_id', '')
                }
                for t in tracks
            ]
        }

    def import_playlist_from_metadata(self, metadata: Dict[str, Any]) -> int:
        """
        Metadata'dan playlist oluştur

        Args:
            metadata: Playlist metadata

        Returns:
            Yeni playlist ID
        """
        playlist_id = self.create_playlist(
            name=metadata.get('name', 'Imported Playlist'),
            description=metadata.get('description', '')
        )

        for track_data in metadata.get('tracks', []):
            track_id = self.db.add_track(
                title=track_data.get('title', ''),
                artist=track_data.get('artist', ''),
                album=track_data.get('album', ''),
                duration=track_data.get('duration', 0),
                source=track_data.get('source', ''),
                source_id=track_data.get('source_id', ''),
                thumbnail_url=track_data.get('thumbnail_url', '')
            )
            self.db.add_track_to_playlist(playlist_id, track_id)

        return playlist_id
