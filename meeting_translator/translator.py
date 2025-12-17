"""
Çeviri modülü
İngilizce-Türkçe çeviri yapar
"""
from deep_translator import GoogleTranslator
from config import Config
import threading
import queue

class Translator:
    def __init__(self):
        self.config = Config()
        self.translator = GoogleTranslator(
            source=self.config.SOURCE_LANG,
            target=self.config.TARGET_LANG
        )
        self.translation_queue = queue.Queue()
        self.cache = {}  # Çeviri önbelleği

    def translate(self, text, min_length=None):
        """
        Metni çevir

        Args:
            text: Çevrilecek metin (İngilizce)
            min_length: Minimum metin uzunluğu (karakterde), None ise config'den alınır

        Returns:
            str: Çevrilmiş metin (Türkçe)
        """
        if not text:
            return ""
        
        # Strip işlemini bir kere yap
        text_stripped = text.strip()
        if not text_stripped:
            return ""
        
        # Minimum uzunluk kontrolü
        if min_length is None:
            min_length = self.config.MIN_TRANSLATION_LENGTH
        
        # Çok kısa metinleri çevirme (gereksiz API çağrısı)
        if len(text_stripped) < min_length:
            return ""

        # Önbellekte varsa kullan (orijinal metni kullan)
        if text in self.cache:
            return self.cache[text]

        try:
            translated = self.translator.translate(text)

            # Önbelleğe ekle
            self.cache[text] = translated

            # Önbellek çok büyürse temizle
            if len(self.cache) > 100:
                # İlk 50 öğeyi sil
                keys_to_remove = list(self.cache.keys())[:50]
                for key in keys_to_remove:
                    del self.cache[key]

            return translated

        except Exception as e:
            print(f"Çeviri hatası: {e}")
            return text  # Hata durumunda orijinal metni döndür

    def translate_async(self, text, callback=None):
        """
        Asenkron olarak çevir

        Args:
            text: Çevrilecek metin
            callback: Sonuç döndüğünde çağrılacak fonksiyon
        """
        def worker():
            translated = self.translate(text)
            if callback:
                callback(translated)
            else:
                self.translation_queue.put(translated)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def get_translation(self, timeout=1):
        """Kuyruktan çeviriyi al"""
        try:
            return self.translation_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def clear_cache(self):
        """Önbelleği temizle"""
        self.cache.clear()


if __name__ == "__main__":
    # Test kodu
    translator = Translator()

    test_texts = [
        "Hello, how are you?",
        "This is a test of the translation system.",
        "Meeting will start in 5 minutes.",
        "Can you hear me?",
        "Thank you for your presentation."
    ]

    print("Çeviri testleri:\n")
    for text in test_texts:
        translated = translator.translate(text)
        print(f"EN: {text}")
        print(f"TR: {translated}")
        print()
