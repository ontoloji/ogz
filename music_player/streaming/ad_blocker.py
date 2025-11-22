"""
Müzik Çalar - Ad Blocker
"""
import re
from typing import List, Set
from urllib.parse import urlparse


class AdBlocker:
    """Reklam engelleme modülü"""

    def __init__(self):
        """Ad blocker başlat"""

        # Yaygın reklam domainleri
        self.ad_domains: Set[str] = {
            'googleads.g.doubleclick.net',
            'pagead2.googlesyndication.com',
            'adservice.google.com',
            'googlesyndication.com',
            'doubleclick.net',
            'googleadservices.com',
            'advertising.com',
            'ads.youtube.com',
            'youtubei.googleapis.com/v1/player/ad',
        }

        # Reklam URL pattern'leri
        self.ad_patterns: List[re.Pattern] = [
            re.compile(r'/ad[s]?/', re.IGNORECASE),
            re.compile(r'advertising', re.IGNORECASE),
            re.compile(r'doubleclick', re.IGNORECASE),
            re.compile(r'googleads', re.IGNORECASE),
            re.compile(r'pagead', re.IGNORECASE),
            re.compile(r'adservice', re.IGNORECASE),
            re.compile(r'/sponsor', re.IGNORECASE),
        ]

        # YouTube özel reklam ID'leri (playlist/video ID'ler)
        self.youtube_ad_ids: Set[str] = set()

        # SponsorBlock segment types (YouTube için)
        self.sponsor_categories: Set[str] = {
            'sponsor',
            'intro',
            'outro',
            'selfpromo',
            'interaction',
            'music_offtopic'
        }

    def is_ad(self, url: str) -> bool:
        """
        URL'nin reklam olup olmadığını kontrol et

        Args:
            url: Kontrol edilecek URL

        Returns:
            True: Reklam, False: Değil
        """
        if not url:
            return False

        # Domain kontrolü
        parsed = urlparse(url)
        if parsed.netloc in self.ad_domains:
            return True

        # Pattern kontrolü
        for pattern in self.ad_patterns:
            if pattern.search(url):
                return True

        # YouTube video ID kontrolü
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = self._extract_youtube_id(url)
            if video_id in self.youtube_ad_ids:
                return True

        return False

    def add_ad_domain(self, domain: str):
        """
        Reklam domain listesine ekle

        Args:
            domain: Engellenecek domain
        """
        self.ad_domains.add(domain.lower())

    def add_ad_pattern(self, pattern: str):
        """
        Reklam pattern listesine ekle

        Args:
            pattern: Regex pattern
        """
        self.ad_patterns.append(re.compile(pattern, re.IGNORECASE))

    def add_youtube_ad_id(self, video_id: str):
        """
        YouTube reklam video ID'si ekle

        Args:
            video_id: YouTube video ID
        """
        self.youtube_ad_ids.add(video_id)

    def _extract_youtube_id(self, url: str) -> str:
        """YouTube URL'den video ID çıkar"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?]+)',
            r'youtube\.com/embed/([^&\n?]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return ""

    def get_sponsor_segments(self, video_id: str) -> List[dict]:
        """
        SponsorBlock API'den sponsor segmentlerini al
        (YouTube videolarındaki sponsor içerikleri atlamak için)

        Args:
            video_id: YouTube video ID

        Returns:
            Segment listesi: [{'start': 10.5, 'end': 45.2, 'category': 'sponsor'}, ...]
        """
        try:
            import requests

            url = f"https://sponsor.ajay.app/api/skipSegments?videoID={video_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                segments = response.json()
                filtered = []

                for segment in segments:
                    if segment.get('category') in self.sponsor_categories:
                        filtered.append({
                            'start': segment['segment'][0],
                            'end': segment['segment'][1],
                            'category': segment.get('category', 'unknown')
                        })

                return filtered

        except Exception as e:
            print(f"SponsorBlock API hatası: {e}")

        return []

    def should_skip_segment(self, video_id: str, current_time: float) -> bool:
        """
        Belirtilen zamanda sponsor segment varsa skip edilmeli mi?

        Args:
            video_id: YouTube video ID
            current_time: Mevcut oynatma zamanı (saniye)

        Returns:
            True: Skip edilmeli, False: Devam
        """
        segments = self.get_sponsor_segments(video_id)

        for segment in segments:
            if segment['start'] <= current_time <= segment['end']:
                return True

        return False

    def get_next_skip_time(self, video_id: str, current_time: float) -> float:
        """
        Bir sonraki sponsor segment sonrası zamanı al

        Args:
            video_id: YouTube video ID
            current_time: Mevcut oynatma zamanı

        Returns:
            Skip sonrası zaman (saniye), yoksa -1
        """
        segments = self.get_sponsor_segments(video_id)

        for segment in segments:
            if segment['start'] <= current_time <= segment['end']:
                return segment['end']

        return -1

    def filter_playlist(self, tracks: List[dict]) -> List[dict]:
        """
        Playlist'ten reklam içeren şarkıları filtrele

        Args:
            tracks: Şarkı listesi

        Returns:
            Filtrelenmiş şarkı listesi
        """
        filtered = []

        for track in tracks:
            # Şarkı URL'lerini kontrol et
            urls_to_check = []

            if 'stream_url' in track:
                urls_to_check.append(track['stream_url'])
            if 'external_url' in track:
                urls_to_check.append(track['external_url'])

            # Hiçbir URL reklam değilse ekle
            is_ad_track = False
            for url in urls_to_check:
                if self.is_ad(url):
                    is_ad_track = True
                    break

            if not is_ad_track:
                filtered.append(track)

        return filtered

    def load_custom_blocklist(self, filepath: str):
        """
        Özel reklam engelme listesi yükle

        Args:
            filepath: Blocklist dosya yolu (her satırda bir domain/pattern)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Domain mı pattern mi?
                        if '/' not in line and '.' in line:
                            self.add_ad_domain(line)
                        else:
                            self.add_ad_pattern(line)

            print(f"Blocklist yüklendi: {filepath}")

        except FileNotFoundError:
            print(f"Blocklist dosyası bulunamadı: {filepath}")
        except Exception as e:
            print(f"Blocklist yükleme hatası: {e}")
