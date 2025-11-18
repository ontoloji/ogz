"""
SORT Test Otomasyon Sistemi - PID Kontrol Modülü
Sabit hız kontrolü için PID (Proportional-Integral-Derivative) kontrolcüsü
"""

import time
import logging
from utils import clamp


class PIDController:
    """
    PID Controller for speed control

    Output = Kp * error + Ki * integral + Kd * derivative
    """

    def __init__(self, kp: float = 2.0, ki: float = 0.5, kd: float = 0.1,
                 output_min: float = 0.0, output_max: float = 100.0,
                 integral_limit: float = 50.0):
        """
        PID kontrolcü başlat

        Args:
            kp: Proportional gain (oransal kazanç)
            ki: Integral gain (integral kazanç)
            kd: Derivative gain (türev kazanç)
            output_min: Minimum çıkış değeri (%)
            output_max: Maximum çıkış değeri (%)
            integral_limit: Integral birikimi sınırı (anti-windup)
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.integral_limit = integral_limit

        # İç değişkenler
        self.setpoint = 0.0  # Hedef hız
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = None
        self.last_output = 0.0

        self.logger = logging.getLogger(__name__)

    def set_setpoint(self, setpoint: float):
        """Hedef değeri ayarla"""
        self.setpoint = setpoint
        self.logger.debug(f"PID hedef değer ayarlandı: {setpoint:.1f} km/h")

    def reset(self):
        """PID durumunu sıfırla"""
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = None
        self.last_output = 0.0
        self.logger.debug("PID sıfırlandı")

    def update(self, current_value: float, dt: float = None) -> float:
        """
        PID çıkışını hesapla

        Args:
            current_value: Mevcut hız (km/h)
            dt: Delta time (saniye). None ise otomatik hesapla

        Returns:
            Gaz pedalı çıkışı (0-100%)
        """
        # Delta time hesapla
        current_time = time.time()
        if dt is None:
            if self.last_time is None:
                dt = 0.1  # İlk çalıştırma için varsayılan
            else:
                dt = current_time - self.last_time

        self.last_time = current_time

        # Hata hesapla
        error = self.setpoint - current_value

        # Proportional terimi
        p_term = self.kp * error

        # Integral terimi (anti-windup ile)
        self.integral += error * dt
        # Integral limiti uygula
        self.integral = clamp(self.integral, -self.integral_limit, self.integral_limit)
        i_term = self.ki * self.integral

        # Derivative terimi
        if dt > 0:
            derivative = (error - self.last_error) / dt
        else:
            derivative = 0.0
        d_term = self.kd * derivative

        # Toplam çıkış
        output = p_term + i_term + d_term

        # Çıkış limitlerini uygula
        output = clamp(output, self.output_min, self.output_max)

        # Debug log
        if abs(error) > 0.5:  # Sadece önemli hatalar için log
            self.logger.debug(
                f"PID: Setpoint={self.setpoint:.1f}, "
                f"Current={current_value:.1f}, "
                f"Error={error:.2f}, "
                f"P={p_term:.2f}, I={i_term:.2f}, D={d_term:.2f}, "
                f"Output={output:.1f}%"
            )

        # Durumu kaydet
        self.last_error = error
        self.last_output = output

        return output

    def get_error(self) -> float:
        """Son hata değerini al"""
        return self.last_error

    def is_at_setpoint(self, tolerance: float = 1.0) -> bool:
        """Hedef değere ulaşıldı mı? (tolerans dahilinde)"""
        return abs(self.last_error) <= tolerance

    def set_gains(self, kp: float = None, ki: float = None, kd: float = None):
        """PID kazançlarını ayarla"""
        if kp is not None:
            self.kp = kp
        if ki is not None:
            self.ki = ki
        if kd is not None:
            self.kd = kd

        self.logger.info(f"PID kazançları güncellendi: Kp={self.kp}, Ki={self.ki}, Kd={self.kd}")

    def get_gains(self) -> tuple:
        """Mevcut PID kazançlarını al"""
        return self.kp, self.ki, self.kd

    def set_output_limits(self, output_min: float, output_max: float):
        """Çıkış limitlerini ayarla"""
        self.output_min = output_min
        self.output_max = output_max
        self.logger.debug(f"PID çıkış limitleri: {output_min:.1f}% - {output_max:.1f}%")

    def auto_tune(self, oscillation_data: list) -> tuple:
        """
        Basit Ziegler-Nichols tabanlı oto-tuning

        Args:
            oscillation_data: [(time, speed), ...] formatında veri

        Returns:
            (kp, ki, kd) önerilen değerler
        """
        # Bu gelişmiş bir özellik - basit versiyon için manuel ayar önerilir
        # Gerçek implementasyon için kritik kazanç ve periyot hesabı gerekir
        self.logger.warning("Oto-tuning henüz implement edilmedi. Manuel ayar kullanın.")
        return self.kp, self.ki, self.kd


class AdaptivePIDController(PIDController):
    """
    Uyarlanabilir PID kontrolcü
    Hız aralığına göre farklı kazanç değerleri kullanır
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Hız aralıklarına göre kazanç profilleri
        # Format: (max_speed, kp, ki, kd)
        self.gain_profiles = [
            (25, 2.5, 0.6, 0.15),  # Düşük hız (0-25 km/h)
            (45, 2.0, 0.5, 0.10),  # Orta hız (25-45 km/h)
            (70, 1.5, 0.4, 0.08),  # Yüksek hız (45+ km/h)
        ]

    def update(self, current_value: float, dt: float = None) -> float:
        """PID çıkışını hesapla (uyarlanabilir kazançlar ile)"""
        # Mevcut hıza göre en uygun kazanç profilini seç
        self._adapt_gains(current_value)

        # Normal PID güncelleme
        return super().update(current_value, dt)

    def _adapt_gains(self, current_speed: float):
        """Hıza göre kazançları ayarla"""
        for max_speed, kp, ki, kd in self.gain_profiles:
            if current_speed <= max_speed:
                if (self.kp != kp or self.ki != ki or self.kd != kd):
                    self.kp = kp
                    self.ki = ki
                    self.kd = kd
                    self.logger.debug(
                        f"Kazançlar uyarlandı ({current_speed:.1f} km/h): "
                        f"Kp={kp}, Ki={ki}, Kd={kd}"
                    )
                break


if __name__ == "__main__":
    # Test
    import matplotlib.pyplot as plt
    import numpy as np

    logging.basicConfig(level=logging.DEBUG)

    # Basit PID testi
    pid = PIDController(kp=2.0, ki=0.5, kd=0.1)
    pid.set_setpoint(30.0)  # Hedef: 30 km/h

    # Simülasyon
    dt = 0.1  # 100ms
    time_steps = 200  # 20 saniye

    times = []
    speeds = []
    outputs = []
    setpoints = []

    current_speed = 0.0
    for i in range(time_steps):
        # PID çıkışı
        pedal_output = pid.update(current_speed, dt)

        # Basit araç modeli (hızlanma pedal ile orantılı)
        # dv/dt = (pedal - drag) / mass
        acceleration = (pedal_output - current_speed * 0.5) / 10.0
        current_speed += acceleration * dt
        current_speed = max(0.0, current_speed)  # Negatif hız olmasın

        # Kaydet
        times.append(i * dt)
        speeds.append(current_speed)
        outputs.append(pedal_output)
        setpoints.append(pid.setpoint)

        # Setpoint değiştir (test için)
        if i == 100:
            pid.set_setpoint(40.0)

    # Grafik
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(times, speeds, 'b-', label='Gerçek Hız', linewidth=2)
    plt.plot(times, setpoints, 'r--', label='Hedef Hız', linewidth=2)
    plt.ylabel('Hız (km/h)')
    plt.legend()
    plt.grid(True)
    plt.title('PID Hız Kontrolü Simülasyonu')

    plt.subplot(2, 1, 2)
    plt.plot(times, outputs, 'g-', label='Gaz Pedalı', linewidth=2)
    plt.ylabel('Pedal (%)')
    plt.xlabel('Zaman (s)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('pid_test.png')
    print("PID test grafiği 'pid_test.png' olarak kaydedildi")
