"""
Müzik Çalar - Konfigürasyon Yönetimi
"""
import json
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Uygulama konfigürasyon yöneticisi"""

    DEFAULT_CONFIG = {
        "audio": {
            "default_volume": 70,
            "equalizer_enabled": True,
            "default_preset": "Flat"
        },
        "streaming": {
            "spotify_enabled": True,
            "youtube_enabled": True,
            "quality": "high",
            "cache_enabled": True,
            "cache_size_mb": 500
        },
        "ui": {
            "theme": "dark",
            "mini_player_on_top": True,
            "show_notifications": True,
            "language": "tr"
        },
        "radio": {
            "default_country": "TR",
            "default_genre": "pop"
        },
        "api_keys": {
            "spotify_client_id": "",
            "spotify_client_secret": "",
            "youtube_api_key": ""
        },
        "paths": {
            "cache_dir": "cache",
            "playlists_dir": "playlists",
            "database": "music_player.db"
        }
    }

    def __init__(self, config_path: str = "music_player_config.json"):
        """
        Konfigürasyon yöneticisini başlat

        Args:
            config_path: Konfigürasyon dosyası yolu
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Konfigürasyonu dosyadan yükle, yoksa varsayılan oluştur"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # Eksik anahtarları varsayılanlarla doldur
                self._merge_defaults()
            except Exception as e:
                print(f"Konfigürasyon yükleme hatası: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()

    def save(self):
        """Konfigürasyonu dosyaya kaydet"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Konfigürasyon kaydetme hatası: {e}")

    def _merge_defaults(self):
        """Eksik konfigürasyon anahtarlarını varsayılanlarla doldur"""
        def merge_dict(target: dict, source: dict):
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target[key], dict):
                    merge_dict(target[key], value)

        merge_dict(self.config, self.DEFAULT_CONFIG)

    def get(self, *keys, default=None):
        """
        Nested dictionary'den değer al

        Args:
            *keys: Anahtar hiyerarşisi (örn: 'audio', 'default_volume')
            default: Bulunamazsa döndürülecek değer

        Returns:
            İstenen değer veya default
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, *keys, value):
        """
        Nested dictionary'e değer ata

        Args:
            *keys: Anahtar hiyerarşisi
            value: Atanacak değer
        """
        target = self.config
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        self.save()

    def get_cache_dir(self) -> Path:
        """Cache klasörünü al, yoksa oluştur"""
        cache_dir = Path(self.get('paths', 'cache_dir', default='cache'))
        cache_dir.mkdir(exist_ok=True)
        return cache_dir

    def get_playlists_dir(self) -> Path:
        """Playlist klasörünü al, yoksa oluştur"""
        playlists_dir = Path(self.get('paths', 'playlists_dir', default='playlists'))
        playlists_dir.mkdir(exist_ok=True)
        return playlists_dir

    def get_database_path(self) -> Path:
        """Veritabanı dosya yolunu al"""
        return Path(self.get('paths', 'database', default='music_player.db'))


# Global konfigürasyon instance
_config_instance = None


def get_config() -> Config:
    """Global konfigürasyon instance'ını al"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
