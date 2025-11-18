"""
SORT Test Otomasyon Sistemi - CAN İletişim Modülü
Kvaser Memorator Pro 2xHS v2 ile CAN iletişimi
"""

import logging
import struct
import threading
import time
from typing import Callable, Optional

# Kvaser CANlib import (Windows için)
# NOT: Linux'ta çalışmayacak, sadece Windows için
try:
    from canlib import canlib, Frame
    CANLIB_AVAILABLE = True
except ImportError:
    CANLIB_AVAILABLE = False
    logging.warning("Kvaser CANlib bulunamadı. CAN işlevselliği sınırlı olacak.")


class CANInterface:
    """
    Kvaser CAN interface

    Elektrikli araç gaz pedalı kontrolü ve VBOX hız okuma
    """

    # CAN Mesaj ID'leri
    TX_PEDAL_ID = 217056130  # 0xCF00002 - Gaz pedalı mesajı (TX)
    RX_SPEED_ID = 770        # 0x302 - VBOX hız mesajı (RX)

    # Pedal durumu değerleri
    PEDAL_PRESSED = 254
    PEDAL_RELEASED = 255

    def __init__(self, channel: int = 0, bitrate: int = 500000):
        """
        CAN interface başlat

        Args:
            channel: CAN kanal numarası (genelde 0)
            bitrate: CAN bit rate (500000 = 500 kbit/s)
        """
        self.channel_num = channel
        self.bitrate = bitrate
        self.channel = None
        self.is_connected = False

        # Callback'ler
        self.speed_callback: Optional[Callable[[float], None]] = None

        # Thread kontrol
        self.running = False
        self.rx_thread = None
        self.tx_thread = None

        # Veri
        self.current_speed = 0.0  # km/h
        self.current_pedal = 0.0  # %
        self.last_rx_time = 0.0
        self.tx_interval = 0.02  # 20ms

        self.logger = logging.getLogger(__name__)

        if not CANLIB_AVAILABLE:
            self.logger.error("Kvaser CANlib yüklü değil!")

    def connect(self) -> bool:
        """CAN kanala bağlan"""
        if not CANLIB_AVAILABLE:
            self.logger.error("CANlib kütüphanesi bulunamadı")
            return False

        try:
            # Kanal aç
            self.channel = canlib.openChannel(self.channel_num, canlib.canOPEN_ACCEPT_VIRTUAL)

            # Bit rate ayarla
            self.channel.setBusParams(self.bitrate)

            # Bus'ı aç
            self.channel.busOn()

            self.is_connected = True
            self.logger.info(f"CAN bağlantısı başarılı: Kanal {self.channel_num}, {self.bitrate} bit/s")

            # Thread'leri başlat
            self._start_threads()

            return True

        except Exception as e:
            self.logger.error(f"CAN bağlantı hatası: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """CAN bağlantısını kes"""
        self._stop_threads()

        if self.channel:
            try:
                self.channel.busOff()
                self.channel.close()
                self.logger.info("CAN bağlantısı kapatıldı")
            except Exception as e:
                self.logger.error(f"CAN kapatma hatası: {e}")

        self.is_connected = False
        self.channel = None

    def set_pedal(self, pedal_percent: float):
        """
        Gaz pedalı değerini ayarla

        Args:
            pedal_percent: Gaz pedalı (0-100%)
        """
        # Sınırla
        pedal_percent = max(0.0, min(100.0, pedal_percent))
        self.current_pedal = pedal_percent

    def get_speed(self) -> float:
        """Mevcut hızı al (km/h)"""
        return self.current_speed

    def set_speed_callback(self, callback: Callable[[float], None]):
        """Hız güncellemesi için callback ayarla"""
        self.speed_callback = callback

    def _start_threads(self):
        """İletişim thread'lerini başlat"""
        self.running = True

        # RX thread (hız okuma)
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True, name="CAN_RX")
        self.rx_thread.start()

        # TX thread (pedal gönderme)
        self.tx_thread = threading.Thread(target=self._tx_loop, daemon=True, name="CAN_TX")
        self.tx_thread.start()

        self.logger.debug("CAN thread'leri başlatıldı")

    def _stop_threads(self):
        """İletişim thread'lerini durdur"""
        self.running = False

        if self.rx_thread:
            self.rx_thread.join(timeout=1.0)
        if self.tx_thread:
            self.tx_thread.join(timeout=1.0)

        self.logger.debug("CAN thread'leri durduruldu")

    def _rx_loop(self):
        """CAN RX loop (hız mesajı okuma)"""
        timeout = 100  # ms

        while self.running and self.is_connected:
            try:
                # Mesaj oku
                frame = self.channel.read(timeout=timeout)

                if frame.id == self.RX_SPEED_ID:
                    # VBOX hız mesajı
                    self._parse_speed_message(frame)
                    self.last_rx_time = time.time()

            except canlib.CanNoMsg:
                # Timeout - normal durum
                pass
            except Exception as e:
                self.logger.error(f"CAN RX hatası: {e}")
                time.sleep(0.1)

        self.logger.debug("CAN RX loop sonlandı")

    def _tx_loop(self):
        """CAN TX loop (pedal mesajı gönderme)"""
        next_send = time.time()

        while self.running and self.is_connected:
            current_time = time.time()

            if current_time >= next_send:
                # Pedal mesajı gönder
                self._send_pedal_message()
                next_send = current_time + self.tx_interval

            # Kısa sleep (CPU kullanımını azalt)
            time.sleep(0.001)

        self.logger.debug("CAN TX loop sonlandı")

    def _send_pedal_message(self):
        """Gaz pedalı CAN mesajı gönder"""
        try:
            # Pedal değerini 0-255 aralığına çevir
            pedal_value = int((self.current_pedal / 100.0) * 255)
            pedal_value = max(0, min(255, pedal_value))

            # Pedal durumu
            if self.current_pedal > 0:
                pedal_status = self.PEDAL_PRESSED
            else:
                pedal_status = self.PEDAL_RELEASED

            # CAN mesajı oluştur (8 byte)
            # Byte 0-1: Pedal değeri (16-bit Little Endian)
            # Byte 2: Pedal durumu
            # Byte 3-7: Rezerve (0x00)
            data = bytearray(8)
            data[0] = pedal_value & 0xFF        # Low byte
            data[1] = (pedal_value >> 8) & 0xFF # High byte
            data[2] = pedal_status
            data[3:8] = [0x00] * 5

            # Frame oluştur ve gönder
            frame = Frame(id_=self.TX_PEDAL_ID, data=data, dlc=8)
            self.channel.write(frame)

        except Exception as e:
            self.logger.error(f"Pedal mesajı gönderme hatası: {e}")

    def _parse_speed_message(self, frame: Frame):
        """
        VBOX hız mesajını parse et

        Format:
            - ID: 0x302 (770)
            - Byte 4-5: Hız (16-bit Little Endian, km/h)
        """
        try:
            if len(frame.data) >= 6:
                # Byte 4-5'i oku (Little Endian)
                speed_raw = struct.unpack('<H', bytes(frame.data[4:6]))[0]
                speed_kmh = float(speed_raw)

                # Güncelle
                self.current_speed = speed_kmh

                # Callback çağır
                if self.speed_callback:
                    self.speed_callback(speed_kmh)

        except Exception as e:
            self.logger.error(f"Hız mesajı parse hatası: {e}")

    def check_timeout(self, timeout: float = 1.0) -> bool:
        """
        RX timeout kontrolü

        Args:
            timeout: Timeout süresi (saniye)

        Returns:
            True = timeout var, False = normal
        """
        if self.last_rx_time == 0:
            return False  # Henüz mesaj alınmadı

        elapsed = time.time() - self.last_rx_time
        return elapsed > timeout

    def get_diagnostics(self) -> dict:
        """CAN tanılama bilgileri"""
        return {
            'connected': self.is_connected,
            'channel': self.channel_num,
            'bitrate': self.bitrate,
            'current_speed': self.current_speed,
            'current_pedal': self.current_pedal,
            'rx_timeout': self.check_timeout(),
            'last_rx_time': self.last_rx_time
        }


class MockCANInterface(CANInterface):
    """
    Mock CAN interface (test için)

    Gerçek CAN donanımı olmadan test yapabilmek için
    """

    def __init__(self, **kwargs):
        # Parent init'i çağırma - mock versiyonu
        self.channel_num = kwargs.get('channel', 0)
        self.bitrate = kwargs.get('bitrate', 500000)
        self.channel = None
        self.is_connected = False

        self.speed_callback: Optional[Callable[[float], None]] = None
        self.running = False
        self.rx_thread = None
        self.tx_thread = None

        self.current_speed = 0.0
        self.current_pedal = 0.0
        self.last_rx_time = time.time()
        self.tx_interval = 0.02

        self.logger = logging.getLogger(__name__)
        self.logger.info("Mock CAN interface oluşturuldu")

        # Simülasyon parametreleri
        self.simulated_acceleration = 0.0  # m/s^2

    def connect(self) -> bool:
        """Mock bağlantı"""
        self.is_connected = True
        self.logger.info("Mock CAN bağlantısı simüle edildi")
        self._start_threads()
        return True

    def disconnect(self):
        """Mock bağlantı kesme"""
        self._stop_threads()
        self.is_connected = False
        self.logger.info("Mock CAN bağlantısı kesildi")

    def _rx_loop(self):
        """Mock RX loop - hız simülasyonu"""
        dt = 0.1  # 100ms

        while self.running and self.is_connected:
            # Basit araç modeli
            # Hızlanma pedal ile orantılı
            target_accel = (self.current_pedal / 100.0) * 2.0  # m/s^2 (max 2 m/s^2)
            drag = self.current_speed * 0.05  # Hava direnci

            self.simulated_acceleration = target_accel - drag

            # Hızı güncelle
            speed_ms = self.current_speed / 3.6  # km/h -> m/s
            speed_ms += self.simulated_acceleration * dt
            speed_ms = max(0.0, speed_ms)  # Negatif hız olmasın

            self.current_speed = speed_ms * 3.6  # m/s -> km/h
            self.last_rx_time = time.time()

            # Callback
            if self.speed_callback:
                self.speed_callback(self.current_speed)

            time.sleep(dt)

    def _tx_loop(self):
        """Mock TX loop"""
        # Mock versiyonda TX gerekmiyor
        while self.running and self.is_connected:
            time.sleep(0.1)


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG)

    # Mock CAN test
    can = MockCANInterface()

    def speed_update(speed):
        print(f"Hız güncellendi: {speed:.1f} km/h")

    can.set_speed_callback(speed_update)
    can.connect()

    print("Test başlıyor...")
    time.sleep(1)

    # %50 gaz
    print("Gaz pedalı: %50")
    can.set_pedal(50)
    time.sleep(3)

    # %80 gaz
    print("Gaz pedalı: %80")
    can.set_pedal(80)
    time.sleep(3)

    # Gaz bırak
    print("Gaz pedalı: %0")
    can.set_pedal(0)
    time.sleep(3)

    can.disconnect()
    print("Test tamamlandı")
