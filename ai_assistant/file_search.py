"""
Dosya Arama Modülü
Sistem genelinde dosya araması yapar
"""

import os
import fnmatch
from pathlib import Path
import threading


class FileSearcher:
    def __init__(self):
        # Arama yapılacak ana dizinler (Windows)
        self.search_paths = [
            Path.home() / 'Desktop',
            Path.home() / 'Documents',
            Path.home() / 'Downloads',
            Path.home(),
        ]

        # Hariç tutulacak dizinler
        self.exclude_dirs = [
            'AppData',
            'Application Data',
            '.git',
            'node_modules',
            '__pycache__',
            '.venv',
            'venv',
            '.cache',
            'Cache',
            '$RECYCLE.BIN',
            'System Volume Information',
        ]

        self.results = []
        self.max_depth = 5  # Maksimum dizin derinliği

    def search(self, pattern, max_results=50, file_types=None):
        """
        Dosya ara

        Args:
            pattern: Arama deseni (örn: "*.py", "rapor", "proje")
            max_results: Maksimum sonuç sayısı
            file_types: Dosya uzantıları listesi (örn: ['.txt', '.pdf'])

        Returns:
            Bulunan dosya yolları listesi
        """
        self.results = []

        # Pattern'i hazırla
        if not any(char in pattern for char in ['*', '?', '[']):
            # Wildcard yoksa ekle
            pattern = f"*{pattern}*"

        # Arama iş parçacıklarını başlat
        threads = []
        for search_path in self.search_paths:
            if search_path.exists():
                thread = threading.Thread(
                    target=self._search_directory,
                    args=(search_path, pattern, file_types, 0)
                )
                threads.append(thread)
                thread.start()

        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join()

        # Sonuçları sırala (en yeni dosyalar önce)
        self.results.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)

        return self.results[:max_results]

    def _search_directory(self, directory, pattern, file_types, depth):
        """
        Dizinde arama yap (recursive)
        """
        if depth > self.max_depth:
            return

        try:
            for entry in os.scandir(directory):
                try:
                    # Hariç tutulan dizinleri atla
                    if entry.is_dir():
                        if entry.name in self.exclude_dirs or entry.name.startswith('.'):
                            continue

                        # Alt dizinde ara
                        self._search_directory(Path(entry.path), pattern, file_types, depth + 1)

                    elif entry.is_file():
                        # Dosya tipi kontrolü
                        if file_types:
                            if not any(entry.name.endswith(ft) for ft in file_types):
                                continue

                        # Pattern eşleşmesi
                        if fnmatch.fnmatch(entry.name.lower(), pattern.lower()):
                            self.results.append(entry.path)

                except (PermissionError, OSError):
                    # Erişim hatalarını görmezden gel
                    continue

        except (PermissionError, OSError):
            # Dizin erişim hatalarını görmezden gel
            pass

    def search_by_extension(self, extension, max_results=50):
        """
        Uzantıya göre dosya ara

        Args:
            extension: Dosya uzantısı (örn: ".py", ".txt")
            max_results: Maksimum sonuç sayısı

        Returns:
            Bulunan dosya yolları listesi
        """
        if not extension.startswith('.'):
            extension = '.' + extension

        return self.search(f"*{extension}", max_results=max_results)

    def search_recent_files(self, days=7, max_results=50):
        """
        Son N gün içinde değiştirilmiş dosyaları bul

        Args:
            days: Kaç gün geriye gidilecek
            max_results: Maksimum sonuç sayısı

        Returns:
            Bulunan dosya yolları listesi
        """
        import time
        from datetime import datetime, timedelta

        cutoff_time = time.time() - (days * 24 * 60 * 60)
        recent_files = []

        for search_path in self.search_paths:
            if not search_path.exists():
                continue

            try:
                for entry in os.scandir(search_path):
                    try:
                        if entry.is_file() and entry.stat().st_mtime > cutoff_time:
                            recent_files.append((entry.path, entry.stat().st_mtime))
                    except (PermissionError, OSError):
                        continue
            except (PermissionError, OSError):
                continue

        # Değiştirilme zamanına göre sırala (en yeni önce)
        recent_files.sort(key=lambda x: x[1], reverse=True)

        return [f[0] for f in recent_files[:max_results]]


# Test için
if __name__ == "__main__":
    searcher = FileSearcher()

    print("Python dosyalarını arıyor...")
    results = searcher.search("*.py", max_results=10)

    if results:
        print(f"\n{len(results)} sonuç bulundu:")
        for i, file_path in enumerate(results, 1):
            print(f"{i}. {file_path}")
    else:
        print("Sonuç bulunamadı.")
