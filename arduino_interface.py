"""
SORT Test Otomasyon Sistemi - Arduino İletişim Modülü
Arduino Uno üzerinden analog çıkış kontrolü (PWM -> RC Filter)
DAF Motor ve IBK için 2 kanallı analog sinyal üretimi
"""

import logging
import serial
import time
import threading
from typing import Optional
from utils import map_value, clamp


class ArduinoInterface:
    """
    Arduino Uno Serial İletişim

    2 Kanallı PWM Analog Çıkış:
    - Kanal 1 (DAF Motor): 0.5V - 4.5V (Pedal %0=%0.5V, %100=4.5V)
    - Kanal 2 (IBK): 2.5V - 4.5V (Pedal %0=2.5V, %100=4.5V)

    Komut formatı: P<channel>,<percentage>\n
    Örnek: P1,75\n (Kanal 1, %75 gaz)
    """

    # Kanal sabitleri
    CHANNEL_DAF = 1
    CHANNEL_IBK = 2

    # Voltaj aralıkları
    DAF_MIN_VOLTAGE = 0.5
    DAF_MAX_VOLTAGE = 4.5
    IBK_MIN_VOLTAGE = 2.5
    IBK_MAX_VOLTAGE = 4.5

    def __init__(self, port: str = 'COM3', baudrate: int = 115200, timeout: float = 1.0):
        """
        Arduino interface başlat

        Args:
            port: Serial port (örn: 'COM3', '/dev/ttyUSB0')
            baudrate: Baud rate (115200)
            timeout: Serial okuma timeout (saniye)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False

        # Kanal değerleri
        self.channel1_percent = 0.0  # DAF
        self.channel2_percent = 0.0  # IBK

        # Thread güvenliği
        self.lock = threading.Lock()

        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """Arduino'ya bağlan"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )

            # Arduino reset sonrası hazır olmasını bekle
            time.sleep(2.0)

            # Tamponları temizle
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()

            self.is_connected = True
            self.logger.info(f"Arduino bağlantısı başarılı: {self.port} @ {self.baudrate} baud")

            # Her iki kanalı da sıfırla
            self.set_pedal(self.CHANNEL_DAF, 0.0)
            self.set_pedal(self.CHANNEL_IBK, 0.0)

            return True

        except serial.SerialException as e:
            self.logger.error(f"Arduino bağlantı hatası: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            self.logger.error(f"Beklenmeyen hata: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Arduino bağlantısını kes"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                # Güvenlik: Çıkışları sıfırla
                self.set_pedal(self.CHANNEL_DAF, 0.0)
                self.set_pedal(self.CHANNEL_IBK, 0.0)
                time.sleep(0.1)

                self.serial_conn.close()
                self.logger.info("Arduino bağlantısı kapatıldı")
            except Exception as e:
                self.logger.error(f"Arduino kapatma hatası: {e}")

        self.is_connected = False
        self.serial_conn = None

    def set_pedal(self, channel: int, pedal_percent: float) -> bool:
        """
        Gaz pedalı değerini ayarla

        Args:
            channel: Kanal numarası (1=DAF, 2=IBK)
            pedal_percent: Gaz pedalı yüzdesi (0-100)

        Returns:
            Başarılı ise True
        """
        if not self.is_connected or not self.serial_conn:
            self.logger.warning("Arduino bağlı değil")
            return False

        # Değeri sınırla
        pedal_percent = clamp(pedal_percent, 0.0, 100.0)

        # Komut oluştur
        command = f"P{channel},{int(pedal_percent)}\n"

        try:
            with self.lock:
                # Komutu gönder
                self.serial_conn.write(command.encode('ascii'))
                self.serial_conn.flush()

                # Yanıt oku (Arduino "OK" gönderir)
                response = self.serial_conn.readline().decode('ascii').strip()

                if response == "OK":
                    # Başarılı - değeri kaydet
                    if channel == self.CHANNEL_DAF:
                        self.channel1_percent = pedal_percent
                    elif channel == self.CHANNEL_IBK:
                        self.channel2_percent = pedal_percent

                    self.logger.debug(f"Arduino kanal {channel}: {pedal_percent:.0f}%")
                    return True
                else:
                    self.logger.warning(f"Beklenmeyen Arduino yanıtı: {response}")
                    return False

        except serial.SerialTimeoutException:
            self.logger.error("Arduino serial timeout")
            return False
        except Exception as e:
            self.logger.error(f"Arduino komut gönderme hatası: {e}")
            return False

    def set_daf_pedal(self, pedal_percent: float) -> bool:
        """DAF motor gaz pedalı ayarla"""
        return self.set_pedal(self.CHANNEL_DAF, pedal_percent)

    def set_ibk_pedal(self, pedal_percent: float) -> bool:
        """IBK gaz pedalı ayarla"""
        return self.set_pedal(self.CHANNEL_IBK, pedal_percent)

    def get_pedal(self, channel: int) -> float:
        """Kanal pedal değerini al"""
        if channel == self.CHANNEL_DAF:
            return self.channel1_percent
        elif channel == self.CHANNEL_IBK:
            return self.channel2_percent
        else:
            return 0.0

    def calculate_voltage(self, channel: int, pedal_percent: float) -> float:
        """
        Pedal yüzdesine karşılık gelen voltajı hesapla

        Args:
            channel: Kanal numarası
            pedal_percent: Pedal yüzdesi (0-100)

        Returns:
            Voltaj değeri
        """
        pedal_percent = clamp(pedal_percent, 0.0, 100.0)

        if channel == self.CHANNEL_DAF:
            # DAF: 0.5V - 4.5V
            return map_value(pedal_percent, 0, 100, self.DAF_MIN_VOLTAGE, self.DAF_MAX_VOLTAGE)
        elif channel == self.CHANNEL_IBK:
            # IBK: 2.5V - 4.5V
            return map_value(pedal_percent, 0, 100, self.IBK_MIN_VOLTAGE, self.IBK_MAX_VOLTAGE)
        else:
            return 0.0

    def calibrate(self) -> dict:
        """
        Kalibrasyon testi yap

        Returns:
            Test sonuçları
        """
        results = {
            'daf_min': None,
            'daf_max': None,
            'ibk_min': None,
            'ibk_max': None
        }

        if not self.is_connected:
            self.logger.error("Kalibrasyon için Arduino bağlı olmalı")
            return results

        self.logger.info("Kalibrasyon başlıyor...")

        # DAF min
        self.logger.info("DAF min voltaj testi (0%)")
        self.set_daf_pedal(0.0)
        time.sleep(1.0)
        results['daf_min'] = self.calculate_voltage(self.CHANNEL_DAF, 0.0)

        # DAF max
        self.logger.info("DAF max voltaj testi (100%)")
        self.set_daf_pedal(100.0)
        time.sleep(1.0)
        results['daf_max'] = self.calculate_voltage(self.CHANNEL_DAF, 100.0)

        # DAF sıfırla
        self.set_daf_pedal(0.0)
        time.sleep(0.5)

        # IBK min
        self.logger.info("IBK min voltaj testi (0%)")
        self.set_ibk_pedal(0.0)
        time.sleep(1.0)
        results['ibk_min'] = self.calculate_voltage(self.CHANNEL_IBK, 0.0)

        # IBK max
        self.logger.info("IBK max voltaj testi (100%)")
        self.set_ibk_pedal(100.0)
        time.sleep(1.0)
        results['ibk_max'] = self.calculate_voltage(self.CHANNEL_IBK, 100.0)

        # IBK sıfırla
        self.set_ibk_pedal(0.0)

        self.logger.info("Kalibrasyon tamamlandı")
        return results

    def test_sweep(self, channel: int, duration: float = 5.0):
        """
        Kanal test sweep (0% -> 100% -> 0%)

        Args:
            channel: Kanal numarası
            duration: Test süresi (saniye)
        """
        if not self.is_connected:
            self.logger.error("Test için Arduino bağlı olmalı")
            return

        self.logger.info(f"Kanal {channel} test sweep başlıyor...")

        steps = 20
        delay = duration / (steps * 2)

        # 0 -> 100
        for i in range(steps + 1):
            percent = (i / steps) * 100.0
            self.set_pedal(channel, percent)
            time.sleep(delay)

        # 100 -> 0
        for i in range(steps, -1, -1):
            percent = (i / steps) * 100.0
            self.set_pedal(channel, percent)
            time.sleep(delay)

        self.logger.info("Test sweep tamamlandı")

    def get_diagnostics(self) -> dict:
        """Arduino tanılama bilgileri"""
        return {
            'connected': self.is_connected,
            'port': self.port,
            'baudrate': self.baudrate,
            'channel1_percent': self.channel1_percent,
            'channel2_percent': self.channel2_percent,
            'channel1_voltage': self.calculate_voltage(self.CHANNEL_DAF, self.channel1_percent),
            'channel2_voltage': self.calculate_voltage(self.CHANNEL_IBK, self.channel2_percent)
        }


class MockArduinoInterface(ArduinoInterface):
    """
    Mock Arduino interface (test için)

    Gerçek Arduino olmadan test yapabilmek için
    """

    def __init__(self, **kwargs):
        # Parent init'i minimalde çalıştır
        self.port = kwargs.get('port', 'MOCK')
        self.baudrate = kwargs.get('baudrate', 115200)
        self.timeout = kwargs.get('timeout', 1.0)
        self.serial_conn = None
        self.is_connected = False

        self.channel1_percent = 0.0
        self.channel2_percent = 0.0
        self.lock = threading.Lock()

        self.logger = logging.getLogger(__name__)
        self.logger.info("Mock Arduino interface oluşturuldu")

    def connect(self) -> bool:
        """Mock bağlantı"""
        self.is_connected = True
        self.logger.info("Mock Arduino bağlantısı simüle edildi")
        return True

    def disconnect(self):
        """Mock bağlantı kesme"""
        self.channel1_percent = 0.0
        self.channel2_percent = 0.0
        self.is_connected = False
        self.logger.info("Mock Arduino bağlantısı kesildi")

    def set_pedal(self, channel: int, pedal_percent: float) -> bool:
        """Mock pedal ayarlama"""
        pedal_percent = clamp(pedal_percent, 0.0, 100.0)

        if channel == self.CHANNEL_DAF:
            self.channel1_percent = pedal_percent
            voltage = self.calculate_voltage(channel, pedal_percent)
            self.logger.debug(f"Mock DAF: {pedal_percent:.0f}% ({voltage:.2f}V)")
        elif channel == self.CHANNEL_IBK:
            self.channel2_percent = pedal_percent
            voltage = self.calculate_voltage(channel, pedal_percent)
            self.logger.debug(f"Mock IBK: {pedal_percent:.0f}% ({voltage:.2f}V)")

        return True


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG)

    # Mock Arduino test
    arduino = MockArduinoInterface()
    arduino.connect()

    print("\n=== Kalibrasyon Testi ===")
    calib_results = arduino.calibrate()
    for key, value in calib_results.items():
        print(f"{key}: {value:.2f}V")

    print("\n=== DAF Test Sweep ===")
    arduino.test_sweep(ArduinoInterface.CHANNEL_DAF, duration=3.0)

    print("\n=== IBK Test Sweep ===")
    arduino.test_sweep(ArduinoInterface.CHANNEL_IBK, duration=3.0)

    print("\n=== Tanılama Bilgileri ===")
    diag = arduino.get_diagnostics()
    for key, value in diag.items():
        print(f"{key}: {value}")

    arduino.disconnect()
    print("\nTest tamamlandı")
