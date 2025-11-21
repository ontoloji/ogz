#!/usr/bin/env python3
"""
Örnek test verisi oluşturucu
SORT test verisi simülasyonu
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime


def generate_sort_test_data(test_type='SORT1', duration=1000, output_dir='test_data'):
    """
    SORT test verisi oluştur

    Args:
        test_type: Test tipi ('SORT1', 'SORT2', 'SORT3')
        duration: Test süresi (saniye)
        output_dir: Çıktı dizini
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Örnek {test_type} test verisi oluşturuluyor...")

    # Zaman dizisi
    time = np.arange(0, duration, 1)

    # Hız profili (gerçekçi simülasyon)
    speed = np.zeros(len(time))
    segment_duration = 50  # Her segment ~50 saniye

    for i in range(0, len(time), segment_duration):
        # Hızlanma
        if i % (segment_duration * 2) == 0:
            target_speed = np.random.choice([20, 30, 40, 50])
            for j in range(min(10, len(time) - i)):
                speed[i + j] = target_speed * (j / 10)

            # Sabit hız
            for j in range(10, min(30, len(time) - i)):
                speed[i + j] = target_speed + np.random.normal(0, 1)

            # Yavaşlama
            for j in range(30, min(40, len(time) - i)):
                speed[i + j] = target_speed * (1 - (j - 30) / 10)

    speed = np.maximum(speed, 0)  # Negatif hız olmasın

    # Mesafe (hızın integrali)
    distance = np.cumsum(speed / 3.6)  # km/h -> m/s, sonra kümülatif

    # Gaz pedalı (hızla ilişkili)
    throttle = np.zeros(len(time))
    for i in range(1, len(time)):
        if speed[i] > speed[i-1]:
            throttle[i] = min(100, 50 + (speed[i] - speed[i-1]) * 10)
        elif speed[i] < speed[i-1]:
            throttle[i] = 0
        else:
            throttle[i] = 20 + speed[i] / 2

    # Enerji tüketimi (basitleştirilmiş model)
    power = speed * throttle / 100 * 50  # Watt (basitleştirilmiş)
    energy = np.cumsum(power / 3600)  # Wh (saniye -> saat)

    # DataFrame oluştur
    df = pd.DataFrame({
        'Time': time,
        'Speed': speed,
        'Distance': distance,
        'Throttle': throttle,
        'Energy': energy
    })

    # Dosya adı
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{test_type}_TEST_{timestamp}.csv"
    filepath = output_dir / filename

    # CSV'ye kaydet
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"✓ Veri kaydedildi: {filepath}")

    # Metadata oluştur
    metadata = {
        'test_type': test_type,
        'test_date': datetime.now().strftime('%Y-%m-%d'),
        'vehicle_type': 'Elektrikli Otobüs',
        'vehicle_plate': '34 TEST 123',
        'driver': 'Test Sürücüsü',
        'test_engineer': 'Test Mühendisi',
        'test_location': 'Test Pisti',
        'ambient_temperature': 25.0,
        'humidity': 60.0,
        'duration': duration,
        'total_distance': float(distance[-1]),
        'total_energy': float(energy[-1]),
        'odometer': 12345
    }

    # Metadata'yı kaydet
    meta_filepath = output_dir / f"{filename.replace('.csv', '.meta.json')}"
    with open(meta_filepath, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ Metadata kaydedildi: {meta_filepath}")

    return filepath, meta_filepath


def create_logo_placeholder(output_path='test_report_generator/assets/otokar_logo.png'):
    """
    Basit logo placeholder oluştur
    """
    from PIL import Image, ImageDraw, ImageFont

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 600x300 boyutunda beyaz arka plan
    img = Image.new('RGB', (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Otokar renkleri
    primary_color = (0, 51, 102)  # #003366
    secondary_color = (255, 102, 0)  # #FF6600

    # Dikdörtgen çerçeve
    draw.rectangle([(50, 50), (550, 250)], outline=primary_color, width=5)

    # OTOKAR metni (basit)
    try:
        # Sistem fontunu kullan
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
    except:
        font = ImageFont.load_default()

    text = "OTOKAR"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (600 - text_width) // 2
    y = (300 - text_height) // 2 - 20

    # Metni çiz
    draw.text((x, y), text, fill=primary_color, font=font)

    # Alt metin
    try:
        small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    except:
        small_font = ImageFont.load_default()

    subtext = "Test Report System"
    bbox = draw.textbbox((0, 0), subtext, font=small_font)
    text_width = bbox[2] - bbox[0]
    x = (600 - text_width) // 2
    y = y + 80

    draw.text((x, y), subtext, fill=secondary_color, font=small_font)

    # Kaydet
    img.save(output_path)
    print(f"✓ Logo placeholder oluşturuldu: {output_path}")

    return output_path


if __name__ == '__main__':
    print("="*60)
    print("ÖRNEK VERİ OLUŞTURUCU")
    print("="*60)

    # Örnek test verileri oluştur
    generate_sort_test_data('SORT1', duration=800)
    generate_sort_test_data('SORT2', duration=600)
    generate_sort_test_data('SORT3', duration=1000)

    print("\n" + "="*60)
    print("LOGO PLACEHOLDER OLUŞTURUCU")
    print("="*60)

    # Logo placeholder oluştur
    create_logo_placeholder()

    print("\n✓ Tüm örnek veriler oluşturuldu!")
