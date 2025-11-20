"""
Konuşmayı metne çevirme modülü
OpenAI Whisper kullanır
"""
import whisper
import numpy as np
import threading
import queue
from config import Config

class SpeechToText:
    def __init__(self):
        self.config = Config()
        self.model = None
        self.is_loaded = False
        self.text_queue = queue.Queue()

    def load_model(self):
        """Whisper modelini yükle"""
        if self.is_loaded:
            return

        print(f"Whisper modeli yükleniyor: {self.config.WHISPER_MODEL}")
        try:
            self.model = whisper.load_model(self.config.WHISPER_MODEL)
            self.is_loaded = True
            print("Whisper modeli başarıyla yüklendi")
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
            raise

    def transcribe_audio(self, audio_data):
        """
        Ses verisini metne çevir

        Args:
            audio_data: numpy array (float32, -1.0 to 1.0)

        Returns:
            str: Metne çevrilmiş ses
        """
        if not self.is_loaded:
            raise RuntimeError("Model yüklenmedi. Önce load_model() çağırın.")

        try:
            # Ses verisinin sessizlik olup olmadığını kontrol et
            rms = np.sqrt(np.mean(audio_data**2))
            if rms < 0.01:  # Çok düşük ses seviyesi
                return ""

            # Whisper beklediği formata çevir
            # Whisper float32 array bekler, [-1.0, 1.0] aralığında
            audio_float32 = audio_data.astype(np.float32)

            # Normalizasyon
            max_val = np.abs(audio_float32).max()
            if max_val > 0:
                audio_float32 = audio_float32 / max_val

            # Whisper ile transkripsiyonu yap
            result = self.model.transcribe(
                audio_float32,
                language=self.config.WHISPER_LANGUAGE,
                task="transcribe",
                fp16=False,  # CPU için False
                verbose=False
            )

            text = result["text"].strip()
            return text

        except Exception as e:
            print(f"Transkripsiyon hatası: {e}")
            return ""

    def transcribe_async(self, audio_data, callback=None):
        """
        Asenkron olarak ses verisini metne çevir

        Args:
            audio_data: numpy array
            callback: Sonuç döndüğünde çağrılacak fonksiyon
        """
        def worker():
            text = self.transcribe_audio(audio_data)
            if callback:
                callback(text)
            else:
                self.text_queue.put(text)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def get_text(self, timeout=1):
        """Kuyruktan metni al"""
        try:
            return self.text_queue.get(timeout=timeout)
        except queue.Empty:
            return None


if __name__ == "__main__":
    # Test kodu
    import soundfile as sf

    stt = SpeechToText()
    stt.load_model()

    # Test ses dosyası varsa
    try:
        # Örnek: test.wav dosyası olmalı
        audio, sr = sf.read("test.wav")
        if sr != 16000:
            print(f"Uyarı: Örnekleme hızı {sr}, 16000'e dönüştürülmeli")

        print("Transkripsiyon yapılıyor...")
        text = stt.transcribe_audio(audio)
        print(f"Sonuç: {text}")

    except Exception as e:
        print(f"Test hatası: {e}")
        print("Test için bir 'test.wav' dosyası ekleyin")
