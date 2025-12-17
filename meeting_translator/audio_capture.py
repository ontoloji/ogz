"""
Sistem sesini yakalama modülü
Windows WASAPI loopback kullanarak sistem sesini yakalar
"""
import numpy as np
import sounddevice as sd
import queue
import threading
from config import Config

class AudioCapture:
    def __init__(self):
        self.config = Config()
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None
        self.buffer = []
        self.max_buffer_duration = self.config.MAX_BUFFER_DURATION

    def list_audio_devices(self):
        """Kullanılabilir ses cihazlarını listele"""
        devices = sd.query_devices()
        print("\n=== Kullanılabilir Ses Cihazları ===")
        for idx, device in enumerate(devices):
            print(f"{idx}: {device['name']}")
            print(f"   Giriş kanalları: {device['max_input_channels']}")
            print(f"   Çıkış kanalları: {device['max_output_channels']}")
            print()
        return devices

    def find_loopback_device(self):
        """Windows'ta loopback (stereo mix) cihazını bul"""
        devices = sd.query_devices()

        # WASAPI loopback için varsayılan hoparlör cihazını ara
        default_output = sd.query_devices(kind='output')
        print(f"\nVarsayılan çıkış cihazı: {default_output['name']}")

        # Stereo Mix veya loopback içeren cihazları ara
        for idx, device in enumerate(devices):
            name_lower = device['name'].lower()
            if ('stereo mix' in name_lower or
                'loopback' in name_lower or
                'wave out mix' in name_lower or
                'what u hear' in name_lower) and device['max_input_channels'] > 0:
                print(f"Loopback cihazı bulundu: {device['name']}")
                return idx

        # Bulunamazsa varsayılan input'u kullan
        print("Uyarı: Loopback cihazı bulunamadı, varsayılan mikrofon kullanılacak")
        print("Not: Windows'ta 'Stereo Mix' veya benzeri bir cihazı Sound Settings'den aktif etmeniz gerekebilir")
        return None

    def audio_callback(self, indata, frames, time, status):
        """Ses verisi geldiğinde çağrılan callback"""
        if status:
            print(f"Ses durumu: {status}")

        # Mono'ya çevir
        if indata.shape[1] > 1:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata[:, 0]

        self.buffer.extend(audio_data.tolist())

        # Buffer'ın çok büyümesini önle (maksimum 30 saniye)
        max_buffer_samples = int(self.config.SAMPLE_RATE * self.max_buffer_duration)
        if len(self.buffer) > max_buffer_samples:
            # Eski veriyi at
            self.buffer = self.buffer[-max_buffer_samples:]

        # Belirlenen süre kadar veri toplandığında kuyruğa ekle
        expected_samples = int(self.config.SAMPLE_RATE * self.config.CHUNK_DURATION)
        if len(self.buffer) >= expected_samples:
            chunk = np.array(self.buffer[:expected_samples], dtype=np.float32)
            self.buffer = self.buffer[expected_samples:]
            self.audio_queue.put(chunk)

    def start_capture(self, device_id=None):
        """Ses yakalamayı başlat"""
        if self.is_recording:
            print("Kayıt zaten aktif")
            return

        if device_id is None:
            device_id = self.find_loopback_device()

        try:
            self.is_recording = True
            self.buffer = []

            # Ses akışını başlat
            self.stream = sd.InputStream(
                device=device_id,
                channels=2,  # Stereo olarak yakala, sonra mono'ya çevir
                samplerate=self.config.SAMPLE_RATE,
                callback=self.audio_callback,
                blocksize=int(self.config.SAMPLE_RATE * 0.1)  # 100ms bloklar
            )
            self.stream.start()
            print(f"Ses yakalama başlatıldı (Cihaz: {device_id})")

        except Exception as e:
            print(f"Ses yakalama hatası: {e}")
            self.is_recording = False
            raise

    def stop_capture(self):
        """Ses yakalamayı durdur"""
        if not self.is_recording:
            return

        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("Ses yakalama durduruldu")

    def get_audio_chunk(self, timeout=1):
        """Kuyruktan ses parçası al"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def clear_queue(self):
        """Ses kuyruğunu temizle"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break


if __name__ == "__main__":
    # Test kodu
    capturer = AudioCapture()
    capturer.list_audio_devices()

    print("\nSes yakalama testi başlatılıyor...")
    capturer.start_capture()

    try:
        import time
        for i in range(5):
            chunk = capturer.get_audio_chunk()
            if chunk is not None:
                print(f"Ses parçası alındı: {len(chunk)} örnek, RMS: {np.sqrt(np.mean(chunk**2)):.4f}")
            time.sleep(0.1)
    finally:
        capturer.stop_capture()
