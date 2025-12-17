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
import numpy as np
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
        
        # Segment-based buffering için
        self.audio_buffer = []
        self.text_buffer = ""
        self.last_audio_time = None
        self.translation_timer = None
        self.timer_lock = threading.Lock()

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

    def trigger_translation(self):
        """
        Timer tarafından çağrılır: buffer'daki metni çevir ve göster
        """
        with self.timer_lock:
            self.translation_timer = None
            
            if self.text_buffer and len(self.text_buffer.strip()) >= 3:
                print(f"\n[EN]: {self.text_buffer}")
                
                # Türkçeye çevir
                turkish_text = self.translator.translate(self.text_buffer)
                if turkish_text:  # Boş değilse göster
                    print(f"[TR]: {turkish_text}")
                    
                    # Altyazıyı güncelle
                    self.overlay.update_text(self.text_buffer, turkish_text)
                
                # Buffer'ı temizle
                self.text_buffer = ""
    
    def reset_translation_timer(self):
        """
        Çeviri timer'ını sıfırla/yeniden başlat
        Yeni ses geldiğinde mevcut timer'ı iptal edip yeni bir tane başlatır
        """
        with self.timer_lock:
            # Mevcut timer'ı iptal et
            if self.translation_timer is not None:
                self.translation_timer.cancel()
            
            # 2.5 saniye sonra çeviri tetikle
            self.translation_timer = threading.Timer(2.5, self.trigger_translation)
            self.translation_timer.daemon = True
            self.translation_timer.start()

    def process_audio_loop(self):
        """Ses işleme döngüsü (segment-based detection ile)"""
        print("\nSes işleme başlatıldı (segment detection aktif)...")

        while self.is_running:
            try:
                # Ses parçası al
                audio_chunk = self.audio_capture.get_audio_chunk(timeout=0.5)

                if audio_chunk is None:
                    continue

                # Ses seviyesini kontrol et (sessizlik filtresi)
                rms = np.sqrt(np.mean(audio_chunk**2))
                if rms < 0.01:  # Çok düşük ses seviyesi
                    continue

                # Buffer'a ekle
                self.audio_buffer.append(audio_chunk)
                self.last_audio_time = time.time()
                
                # Buffer'ın çok büyümesini önle (maksimum 30 saniye)
                max_buffer_chunks = int(30 / self.config.CHUNK_DURATION)
                if len(self.audio_buffer) > max_buffer_chunks:
                    self.audio_buffer = self.audio_buffer[-max_buffer_chunks:]
                
                # Buffer'daki tüm ses verisini birleştir
                combined_audio = np.concatenate(self.audio_buffer)
                
                # Whisper ile segment bilgileriyle transkripsiyonu yap
                result = self.stt.transcribe_audio(combined_audio, return_segments=True)
                
                if result and "text" in result and result["text"].strip():
                    current_text = result["text"].strip()
                    
                    # Segment bilgilerini kontrol et
                    segments = result.get("segments", [])
                    
                    # En son segment'i al
                    if segments:
                        last_segment = segments[-1]
                        last_segment_text = last_segment.get("text", "").strip()
                        
                        # Segment tamamlandı mı kontrol et (noktalama var mı?)
                        if self.stt.is_segment_complete(last_segment_text):
                            # Cümle tamamlandı, hemen çevir
                            print(f"\n[Segment Tamamlandı - EN]: {current_text}")
                            
                            # Minimum uzunluk kontrolü
                            if len(current_text) >= 3:
                                turkish_text = self.translator.translate(current_text)
                                if turkish_text:
                                    print(f"[TR]: {turkish_text}")
                                    self.overlay.update_text(current_text, turkish_text)
                            
                            # Buffer'ları temizle
                            self.audio_buffer = []
                            self.text_buffer = ""
                            
                            # Timer varsa iptal et
                            with self.timer_lock:
                                if self.translation_timer is not None:
                                    self.translation_timer.cancel()
                                    self.translation_timer = None
                        else:
                            # Segment henüz tamamlanmadı, buffer'da tut
                            self.text_buffer = current_text
                            
                            # Timer'ı sıfırla (2.5 saniye sessizlik sonrası çevir)
                            self.reset_translation_timer()

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

        # Timer'ı iptal et
        with self.timer_lock:
            if self.translation_timer is not None:
                self.translation_timer.cancel()
                self.translation_timer = None

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
