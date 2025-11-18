"""
SORT Test Otomasyon Sistemi - eDAQ Entegrasyon Modülü
HBK eDAQ HTTP REST API üzerinden enerji tüketimi okuma (XML)
"""

import logging
import threading
import time
import xml.etree.ElementTree as ET
from typing import Callable, Optional
import requests


class eDAQInterface:
    """
    HBK eDAQ HTTP REST API

    Enerji tüketimi verisi okuma (XML formatında)
    """

    def __init__(self, ip: str = "192.168.1.100", port: int = 8080,
                 channel_name: str = "Energy", poll_interval: float = 0.4):
        """
        eDAQ interface başlat

        Args:
            ip: eDAQ IP adresi
            port: eDAQ HTTP portu
            channel_name: Enerji kanalı adı
            poll_interval: Veri okuma periyodu (saniye)
        """
        self.ip = ip
        self.port = port
        self.channel_name = channel_name
        self.poll_interval = poll_interval

        # Endpoint
        self.base_url = f"http://{ip}:{port}"
        self.data_endpoint = f"{self.base_url}/measurement/data"

        # Veri
        self.current_energy = 0.0  # kWh
        self.is_connected = False
        self.last_read_time = 0.0

        # Thread
        self.running = False
        self.poll_thread = None

        # Callback
        self.energy_callback: Optional[Callable[[float], None]] = None

        # HTTP timeout
        self.timeout = 2.0  # saniye

        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """eDAQ'a bağlan ve bağlantıyı test et"""
        try:
            # Test GET request
            response = requests.get(self.data_endpoint, timeout=self.timeout)

            if response.status_code == 200:
                self.is_connected = True
                self.logger.info(f"eDAQ bağlantısı başarılı: {self.base_url}")

                # Polling thread başlat
                self._start_polling()
                return True
            else:
                self.logger.error(f"eDAQ bağlantı hatası: HTTP {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            self.logger.error("eDAQ bağlantı timeout")
            return False
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"eDAQ bağlantı hatası: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Beklenmeyen hata: {e}")
            return False

    def disconnect(self):
        """eDAQ bağlantısını kes"""
        self._stop_polling()
        self.is_connected = False
        self.logger.info("eDAQ bağlantısı kapatıldı")

    def get_energy(self) -> float:
        """Mevcut enerji tüketimini al (kWh)"""
        return self.current_energy

    def set_energy_callback(self, callback: Callable[[float], None]):
        """Enerji güncellemesi için callback ayarla"""
        self.energy_callback = callback

    def _start_polling(self):
        """Polling thread başlat"""
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True, name="eDAQ_Poll")
        self.poll_thread.start()
        self.logger.debug("eDAQ polling thread başlatıldı")

    def _stop_polling(self):
        """Polling thread durdur"""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=2.0)
        self.logger.debug("eDAQ polling thread durduruldu")

    def _poll_loop(self):
        """Polling loop (periyodik veri okuma)"""
        next_read = time.time()

        while self.running and self.is_connected:
            current_time = time.time()

            if current_time >= next_read:
                # Veri oku
                energy = self._read_energy()

                if energy is not None:
                    self.current_energy = energy
                    self.last_read_time = current_time

                    # Callback çağır
                    if self.energy_callback:
                        self.energy_callback(energy)

                next_read = current_time + self.poll_interval

            # Kısa sleep (CPU kullanımını azalt)
            time.sleep(0.01)

        self.logger.debug("eDAQ poll loop sonlandı")

    def _read_energy(self) -> Optional[float]:
        """
        eDAQ'dan enerji verisini oku

        Returns:
            Enerji değeri (kWh) veya None (hata durumunda)
        """
        try:
            response = requests.get(self.data_endpoint, timeout=self.timeout)

            if response.status_code == 200:
                # XML parse et
                energy = self._parse_xml_response(response.text)
                return energy
            else:
                self.logger.warning(f"eDAQ HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            self.logger.warning("eDAQ okuma timeout")
            return None
        except Exception as e:
            self.logger.error(f"eDAQ okuma hatası: {e}")
            return None

    def _parse_xml_response(self, xml_text: str) -> Optional[float]:
        """
        XML yanıtını parse et ve enerji değerini çıkar

        Örnek XML formatı:
        <measurement>
            <channel name="Energy" unit="kWh">12.345</channel>
            <channel name="Voltage" unit="V">230.5</channel>
        </measurement>

        Args:
            xml_text: XML metin

        Returns:
            Enerji değeri (kWh) veya None
        """
        try:
            root = ET.fromstring(xml_text)

            # Channel elemanlarını tara
            for channel in root.findall('.//channel'):
                name = channel.get('name')
                if name == self.channel_name:
                    value_text = channel.text
                    if value_text:
                        return float(value_text)

            self.logger.warning(f"eDAQ XML'de '{self.channel_name}' kanalı bulunamadı")
            return None

        except ET.ParseError as e:
            self.logger.error(f"XML parse hatası: {e}")
            return None
        except ValueError as e:
            self.logger.error(f"Sayı dönüşüm hatası: {e}")
            return None
        except Exception as e:
            self.logger.error(f"XML işleme hatası: {e}")
            return None

    def reset_energy(self) -> bool:
        """
        Enerji sayacını sıfırla (eDAQ'da reset komutu varsa)

        Not: Bu API endpoint'ine bağlı olarak çalışır
        """
        try:
            reset_endpoint = f"{self.base_url}/measurement/reset"
            response = requests.post(reset_endpoint, timeout=self.timeout)

            if response.status_code == 200:
                self.current_energy = 0.0
                self.logger.info("eDAQ enerji sayacı sıfırlandı")
                return True
            else:
                self.logger.warning(f"eDAQ reset hatası: HTTP {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"eDAQ reset hatası: {e}")
            return False

    def get_diagnostics(self) -> dict:
        """eDAQ tanılama bilgileri"""
        return {
            'connected': self.is_connected,
            'ip': self.ip,
            'port': self.port,
            'channel_name': self.channel_name,
            'current_energy': self.current_energy,
            'poll_interval': self.poll_interval,
            'last_read_time': self.last_read_time
        }


class MockeDAQInterface(eDAQInterface):
    """
    Mock eDAQ interface (test için)

    Gerçek eDAQ olmadan test yapabilmek için
    """

    def __init__(self, **kwargs):
        # Parent init'i minimalde çalıştır
        self.ip = kwargs.get('ip', '192.168.1.100')
        self.port = kwargs.get('port', 8080)
        self.channel_name = kwargs.get('channel_name', 'Energy')
        self.poll_interval = kwargs.get('poll_interval', 0.4)

        self.base_url = f"http://{self.ip}:{self.port}"
        self.data_endpoint = f"{self.base_url}/measurement/data"

        self.current_energy = 0.0
        self.is_connected = False
        self.last_read_time = 0.0

        self.running = False
        self.poll_thread = None
        self.energy_callback = None
        self.timeout = 2.0

        self.logger = logging.getLogger(__name__)
        self.logger.info("Mock eDAQ interface oluşturuldu")

        # Simülasyon parametreleri
        self.simulated_power = 0.0  # kW (anlık güç)
        self.start_time = None

    def connect(self) -> bool:
        """Mock bağlantı"""
        self.is_connected = True
        self.start_time = time.time()
        self.logger.info("Mock eDAQ bağlantısı simüle edildi")
        self._start_polling()
        return True

    def disconnect(self):
        """Mock bağlantı kesme"""
        self._stop_polling()
        self.is_connected = False
        self.logger.info("Mock eDAQ bağlantısı kesildi")

    def _read_energy(self) -> Optional[float]:
        """Mock enerji okuma (zaman ve güç tabanlı simülasyon)"""
        if self.start_time is None:
            return 0.0

        # Geçen süre (saat)
        elapsed_hours = (time.time() - self.start_time) / 3600.0

        # Sabit güç varsayımı ile enerji hesapla
        # Gerçek uygulamada hız/pedal ile orantılı olabilir
        energy = self.simulated_power * elapsed_hours

        # Küçük rastgele varyasyon ekle
        import random
        energy += random.uniform(-0.01, 0.01)
        energy = max(0.0, energy)

        return energy

    def set_simulated_power(self, power_kw: float):
        """Simüle edilen anlık gücü ayarla (test için)"""
        self.simulated_power = power_kw
        self.logger.debug(f"Mock eDAQ simüle güç: {power_kw:.2f} kW")

    def reset_energy(self) -> bool:
        """Mock enerji sıfırlama"""
        self.current_energy = 0.0
        self.start_time = time.time()
        self.logger.info("Mock eDAQ enerji sayacı sıfırlandı")
        return True


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.DEBUG)

    # Mock eDAQ test
    edaq = MockeDAQInterface()

    def energy_update(energy):
        print(f"Enerji güncellendi: {energy:.3f} kWh")

    edaq.set_energy_callback(energy_update)
    edaq.connect()

    print("Test başlıyor...")

    # Simüle 5 kW güç
    edaq.set_simulated_power(5.0)
    time.sleep(3)

    # Simüle 10 kW güç
    edaq.set_simulated_power(10.0)
    time.sleep(3)

    # Güç kes
    edaq.set_simulated_power(0.0)
    time.sleep(2)

    # Tanılama
    print("\nTanılama bilgileri:")
    diag = edaq.get_diagnostics()
    for key, value in diag.items():
        print(f"  {key}: {value}")

    edaq.disconnect()
    print("\nTest tamamlandı")
