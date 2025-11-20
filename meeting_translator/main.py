"""
Meeting Translator - Ana Uygulama
Teams ve benzeri toplantılarda gerçek zamanlı İngilizce-Türkçe altyazı

Kullanım:
    python main.py

Kontroller:
    - Overlay penceresini sürükleyerek taşıyabilirsiniz
    - "−" butonu ile geçici olarak gizleyebilirsiniz
    - "✕" butonu veya Ctrl+C ile kapatabilirsiniz
"""

import sys
import time
import threading
import signal
from audio_capture import AudioCapture
from speech_to_text import SpeechToText
from translator import Translator
from subtitle_overlay import SubtitleOverlay
from config import Config

class MeetingTranslator:
    def __init__(self):
        self.config = Config()
        self.audio_capture = None
        self.stt = None
        self.translator = None
        self.overlay = None
        self.is_running = False
        self.processing_thread = None

    def initialize(self):
        """Tüm bileşenleri başlat"""
        print("Meeting Translator başlatılıyor...")
        print("-" * 50)

        # Ses yakalayıcıyı başlat
        print("\n1. Ses yakalayıcı hazırlanıyor...")
        self.audio_capture = AudioCapture()

        # Kullanılabilir cihazları listele
        self.audio_capture.list_audio_devices()

        # Speech-to-Text modelini yükle
        print("\n2. Konuşma tanıma modeli yükleniyor...")
        print("   (Bu işlem ilk seferde birkaç dakika sürebilir)")
        self.stt = SpeechToText()
        self.stt.load_model()

        # Çeviri servisini başlat
        print("\n3. Çeviri servisi hazırlanıyor...")
        self.translator = Translator()

        # Overlay penceresini başlat
        print("\n4. Altyazı penceresi oluşturuluyor...")
        self.overlay = SubtitleOverlay()

        print("\n" + "=" * 50)
        print("Hazırlık tamamlandı!")
        print("=" * 50)

    def process_audio_loop(self):
        """Ses işleme döngüsü (ayrı thread'de çalışır)"""
        print("\nSes işleme başlatıldı...")

        while self.is_running:
            try:
                # Ses parçası al
                audio_chunk = self.audio_capture.get_audio_chunk(timeout=0.5)

                if audio_chunk is None:
                    continue

                # Konuşmayı metne çevir
                english_text = self.stt.transcribe_audio(audio_chunk)

                if english_text and len(english_text.strip()) > 0:
                    print(f"\n[EN]: {english_text}")

                    # Türkçeye çevir
                    turkish_text = self.translator.translate(english_text)
                    print(f"[TR]: {turkish_text}")

                    # Altyazıyı güncelle
                    self.overlay.update_text(english_text, turkish_text)

            except Exception as e:
                print(f"İşleme hatası: {e}")
                import traceback
                traceback.print_exc()

        print("Ses işleme durduruldu")

    def start(self):
        """Uygulamayı başlat"""
        try:
            self.is_running = True

            # Overlay penceresini asenkron başlat
            self.overlay.run_async()
            time.sleep(1)  # Pencerenin açılması için bekle

            # Ses yakalamayı başlat
            print("\nSes yakalama başlatılıyor...")
            self.audio_capture.start_capture()

            # Ses işleme döngüsünü ayrı thread'de başlat
            self.processing_thread = threading.Thread(
                target=self.process_audio_loop,
                daemon=True
            )
            self.processing_thread.start()

            print("\n" + "=" * 50)
            print("MEETING TRANSLATOR ÇALIŞIYOR")
            print("=" * 50)
            print("\nNot:")
            print("- Windows'ta sistem sesini yakalamak için 'Stereo Mix' veya")
            print("  'Loopback' cihazının Sound Settings'den aktif olması gerekir")
            print("- Overlay penceresini taşıyabilirsiniz")
            print("- Kapatmak için penceredeki ✕ butonunu kullanın veya Ctrl+C")
            print("-" * 50)

            # Ana pencere döngüsü (blocking)
            self.overlay.run()

        except KeyboardInterrupt:
            print("\n\nKullanıcı tarafından durduruldu")
        except Exception as e:
            print(f"\nHata oluştu: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()

    def stop(self):
        """Uygulamayı durdur"""
        print("\nUygulama kapatılıyor...")

        self.is_running = False

        # Ses yakalamayı durdur
        if self.audio_capture:
            self.audio_capture.stop_capture()

        # Overlay'i kapat
        if self.overlay:
            self.overlay.stop()

        # İşleme thread'inin bitmesini bekle
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2)

        print("Uygulama kapatıldı")


def signal_handler(sig, frame):
    """Ctrl+C sinyalini yakala"""
    print("\n\nKapatma sinyali alındı...")
    sys.exit(0)


def main():
    """Ana fonksiyon"""
    # Sinyal yakalayıcısını ayarla
    signal.signal(signal.SIGINT, signal_handler)

    # Uygulamayı oluştur ve başlat
    app = MeetingTranslator()

    try:
        app.initialize()
        app.start()
    except Exception as e:
        print(f"\nFatal hata: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
