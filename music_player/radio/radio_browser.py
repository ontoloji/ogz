"""
Müzik Çalar - Online Radio (Radio Browser API)
"""
import requests
from typing import List, Dict, Optional, Any
import random


class RadioBrowser:
    """Radio Browser API client - 30,000+ internet radio stations"""

    # Radio Browser API base URLs (use random server for load balancing)
    BASE_URLS = [
        "https://de1.api.radio-browser.info",
        "https://nl1.api.radio-browser.info",
        "https://at1.api.radio-browser.info"
    ]

    def __init__(self):
        """Radio browser client başlat"""
        self.base_url = random.choice(self.BASE_URLS)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MusicPlayer/1.0',
            'Content-Type': 'application/json'
        })

    def search_stations(self, name: str = "", country: str = "", language: str = "",
                       tag: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Radyo istasyonu ara

        Args:
            name: İstasyon adı
            country: Ülke kodu (örn: TR, US, GB)
            language: Dil kodu (örn: turkish, english)
            tag: Tag/Genre (örn: pop, rock, jazz)
            limit: Maksimum sonuç sayısı

        Returns:
            Radyo istasyonu listesi
        """
        url = f"{self.base_url}/json/stations/search"

        params = {
            'limit': limit,
            'hidebroken': 'true',  # Çalışmayan istasyonları gizle
            'order': 'votes',  # En çok oy alanlara göre sırala
            'reverse': 'true'
        }

        if name:
            params['name'] = name
        if country:
            params['country'] = country.upper()
        if language:
            params['language'] = language.lower()
        if tag:
            params['tag'] = tag.lower()

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            stations = response.json()
            return self._parse_stations(stations)

        except Exception as e:
            print(f"Radio Browser arama hatası: {e}")
            return []

    def get_top_stations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        En popüler radyo istasyonlarını al

        Args:
            limit: Maksimum sonuç sayısı

        Returns:
            Radyo istasyonu listesi
        """
        url = f"{self.base_url}/json/stations/topvote/{limit}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            stations = response.json()
            return self._parse_stations(stations)

        except Exception as e:
            print(f"Top stations alma hatası: {e}")
            return []

    def get_stations_by_country(self, country: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Ülkeye göre radyo istasyonları al

        Args:
            country: Ülke kodu (örn: TR, US)
            limit: Maksimum sonuç sayısı

        Returns:
            Radyo istasyonu listesi
        """
        return self.search_stations(country=country, limit=limit)

    def get_stations_by_genre(self, genre: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Türe göre radyo istasyonları al

        Args:
            genre: Tür (pop, rock, jazz, classical, etc.)
            limit: Maksimum sonuç sayısı

        Returns:
            Radyo istasyonu listesi
        """
        return self.search_stations(tag=genre, limit=limit)

    def get_station_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        UUID ile istasyon bilgisi al

        Args:
            uuid: Station UUID

        Returns:
            İstasyon bilgisi
        """
        url = f"{self.base_url}/json/stations/byuuid/{uuid}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            stations = response.json()
            if stations:
                return self._parse_station(stations[0])

        except Exception as e:
            print(f"Station bilgisi alma hatası: {e}")

        return None

    def get_countries(self) -> List[Dict[str, Any]]:
        """
        Tüm ülkeleri al

        Returns:
            Ülke listesi: [{'name': 'Turkey', 'code': 'TR', 'station_count': 123}, ...]
        """
        url = f"{self.base_url}/json/countries"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            countries = response.json()
            return [
                {
                    'name': c['name'],
                    'code': c['stationcount'] if c['stationcount'] > 0 else c['name'],
                    'station_count': c['stationcount']
                }
                for c in countries if c['stationcount'] > 0
            ]

        except Exception as e:
            print(f"Ülke listesi alma hatası: {e}")
            return []

    def get_genres(self) -> List[Dict[str, Any]]:
        """
        Tüm türleri al

        Returns:
            Tür listesi: [{'name': 'pop', 'station_count': 456}, ...]
        """
        url = f"{self.base_url}/json/tags"

        try:
            response = self.session.get(url, params={'order': 'stationcount', 'reverse': 'true'}, timeout=10)
            response.raise_for_status()

            tags = response.json()
            return [
                {
                    'name': t['name'],
                    'station_count': t['stationcount']
                }
                for t in tags if t['stationcount'] > 0
            ][:100]  # İlk 100 türü al

        except Exception as e:
            print(f"Tür listesi alma hatası: {e}")
            return []

    def get_languages(self) -> List[Dict[str, Any]]:
        """
        Tüm dilleri al

        Returns:
            Dil listesi
        """
        url = f"{self.base_url}/json/languages"

        try:
            response = self.session.get(url, params={'order': 'stationcount', 'reverse': 'true'}, timeout=10)
            response.raise_for_status()

            languages = response.json()
            return [
                {
                    'name': l['name'],
                    'station_count': l['stationcount']
                }
                for l in languages if l['stationcount'] > 0
            ][:50]  # İlk 50 dili al

        except Exception as e:
            print(f"Dil listesi alma hatası: {e}")
            return []

    def vote_for_station(self, uuid: str) -> bool:
        """
        İstasyona oy ver (popülerlik için)

        Args:
            uuid: Station UUID

        Returns:
            True: Başarılı, False: Hata
        """
        url = f"{self.base_url}/json/vote/{uuid}"

        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return True
        except:
            return False

    def click_station(self, uuid: str) -> bool:
        """
        İstasyon tıklandı olarak işaretle (istatistik için)

        Args:
            uuid: Station UUID

        Returns:
            True: Başarılı
        """
        url = f"{self.base_url}/json/url/{uuid}"

        try:
            response = self.session.get(url, timeout=5)
            # URL döndürür, tıklama kaydedilir
            return True
        except:
            return False

    def _parse_stations(self, stations: List[dict]) -> List[Dict[str, Any]]:
        """İstasyon listesini parse et"""
        return [self._parse_station(s) for s in stations]

    def _parse_station(self, station: dict) -> Dict[str, Any]:
        """Tek istasyonu parse et"""
        return {
            'uuid': station.get('stationuuid', ''),
            'name': station.get('name', 'Unknown Station'),
            'stream_url': station.get('url_resolved', station.get('url', '')),
            'homepage': station.get('homepage', ''),
            'favicon': station.get('favicon', ''),
            'country': station.get('country', ''),
            'language': station.get('language', ''),
            'tags': station.get('tags', '').split(',') if station.get('tags') else [],
            'codec': station.get('codec', ''),
            'bitrate': station.get('bitrate', 0),
            'votes': station.get('votes', 0),
            'click_count': station.get('clickcount', 0),
            'is_https': station.get('url_resolved', '').startswith('https://'),
        }

    def get_stream_url(self, uuid: str) -> Optional[str]:
        """
        İstasyon stream URL'i al ve tıklama kaydet

        Args:
            uuid: Station UUID

        Returns:
            Stream URL
        """
        station = self.get_station_by_uuid(uuid)
        if station:
            self.click_station(uuid)  # Tıklama kaydet
            return station['stream_url']
        return None
