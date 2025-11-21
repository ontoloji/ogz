"""
Örnek SORT test verisi oluşturan script
"""
import pandas as pd
import numpy as np
from pathlib import Path

def create_sort2_sample_data():
    """
    SORT 2 test döngüsüne benzer örnek veri oluşturur
    """
    # SORT 2 parametreleri
    duration = 1150  # saniye
    max_speed = 40  # km/h
    avg_speed = 20  # km/h

    # Zaman dizisi (1 Hz örnekleme)
    time = np.arange(0, duration, 1)

    # Hız profili oluştur (basitleştirilmiş SORT 2 döngüsü)
    speed = np.zeros(len(time))

    # Döngü fazları
    phases = [
        # (başlangıç, bitiş, hedef_hız, faz_tipi)
        (0, 100, 0, 'stop'),
        (100, 150, 25, 'accel'),
        (150, 250, 25, 'cruise'),
        (250, 300, 15, 'decel'),
        (300, 350, 15, 'cruise'),
        (350, 400, 0, 'decel'),
        (400, 500, 0, 'stop'),
        (500, 550, 30, 'accel'),
        (550, 650, 30, 'cruise'),
        (650, 700, 20, 'decel'),
        (700, 750, 20, 'cruise'),
        (750, 800, 0, 'decel'),
        (800, 850, 0, 'stop'),
        (850, 900, 40, 'accel'),
        (900, 1000, 40, 'cruise'),
        (1000, 1050, 10, 'decel'),
        (1050, 1100, 10, 'cruise'),
        (1100, 1150, 0, 'decel'),
    ]

    for start, end, target_speed, phase_type in phases:
        if start >= len(time):
            break

        end = min(end, len(time))
        segment_length = end - start

        if phase_type == 'stop':
            speed[start:end] = 0
        elif phase_type == 'cruise':
            speed[start:end] = target_speed
        elif phase_type == 'accel':
            # Lineer hızlanma
            prev_speed = speed[start-1] if start > 0 else 0
            speed[start:end] = np.linspace(prev_speed, target_speed, segment_length)
        elif phase_type == 'decel':
            # Lineer yavaşlama
            prev_speed = speed[start-1] if start > 0 else 0
            speed[start:end] = np.linspace(prev_speed, target_speed, segment_length)

    # Gürültü ekle (gerçekçilik için)
    speed += np.random.normal(0, 0.5, len(speed))
    speed = np.clip(speed, 0, max_speed)

    # Voltaj (nominal 400V, değişken yük)
    voltage = 400 + np.random.normal(0, 5, len(time))

    # Akım (hıza ve ivmeye bağlı)
    # Temel formül: I = P / V, P = k * v + k2 * a
    acceleration = np.gradient(speed)
    power_demand = 50 * speed + 100 * np.maximum(acceleration, 0)  # Hızlanmada daha fazla güç
    current = power_demand * 1000 / voltage  # W / V = A

    # Regeneratif frenleme (negatif ivmede)
    regen_mask = acceleration < -0.5
    current[regen_mask] = -50 * np.abs(acceleration[regen_mask])  # Negatif akım

    # Gürültü ekle
    current += np.random.normal(0, 5, len(current))

    # Sıcaklık (ortam sıcaklığı + motor ısınması)
    base_temp = 25  # °C
    temp_increase = np.cumsum(np.abs(current) / 100000)  # Kümülatif ısınma
    temp_increase = np.clip(temp_increase, 0, 15)
    temperature = base_temp + temp_increase + np.random.normal(0, 1, len(time))

    # DataFrame oluştur
    df = pd.DataFrame({
        'Zaman': time,
        'Hız': speed,
        'Akım': current,
        'Voltaj': voltage,
        'Sıcaklık': temperature
    })

    return df

def main():
    """Ana fonksiyon"""
    print("Örnek SORT test verisi oluşturuluyor...")

    # Veri oluştur
    df = create_sort2_sample_data()

    # Kaydet
    output_path = Path(__file__).parent / "data" / "ornek_test_verisi.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"✓ Örnek veri oluşturuldu: {output_path}")
    print(f"  - {len(df)} satır veri")
    print(f"  - Süre: {df['Zaman'].max():.1f} saniye")
    print(f"  - Maks hız: {df['Hız'].max():.1f} km/h")
    print(f"  - Ort hız: {df['Hız'].mean():.1f} km/h")

if __name__ == "__main__":
    main()
