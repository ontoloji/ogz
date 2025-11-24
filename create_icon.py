#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Radio Icon Generator
PIL/Pillow ile basit bir radyo ikonu oluşturur
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import sys

    def create_radio_icon(output_file='radio_icon.ico', size=256):
        """Basit bir radyo ikonu oluştur"""
        # Kare görüntü oluştur
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Arka plan - yuvarlak gradyan etkisi
        center = size // 2
        radius = size // 2 - 10

        # Dış çember (radyo gövdesi) - mavi tonlar
        draw.ellipse([10, 10, size-10, size-10], fill=(33, 150, 243, 255))

        # İç çember (daha açık)
        inner_margin = 20
        draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin],
                     fill=(66, 165, 245, 255))

        # Radyo dalgaları - sağ üst
        wave_color = (255, 255, 255, 200)
        wave_x = center + 40
        wave_y = center - 40

        # 3 dalga çiz
        for i in range(3):
            radius_offset = 15 + (i * 15)
            draw.arc([wave_x - radius_offset, wave_y - radius_offset,
                     wave_x + radius_offset, wave_y + radius_offset],
                     start=-45, end=45, fill=wave_color, width=4)

        # Anten - merkez üst
        antenna_x = center
        antenna_y = 30
        draw.line([antenna_x, antenna_y, antenna_x, antenna_y + 30],
                  fill=(255, 255, 255, 255), width=5)
        draw.ellipse([antenna_x - 8, antenna_y - 8, antenna_x + 8, antenna_y + 8],
                     fill=(255, 255, 255, 255))

        # Ses simgesi - sol alt
        speaker_x = center - 60
        speaker_y = center + 40
        # Speaker cone
        draw.polygon([(speaker_x, speaker_y - 15),
                     (speaker_x, speaker_y + 15),
                     (speaker_x + 20, speaker_y + 25),
                     (speaker_x + 20, speaker_y - 25)],
                    fill=(255, 255, 255, 255))
        # Sound waves
        for i in range(3):
            offset = 25 + (i * 8)
            draw.arc([speaker_x + offset - 10, speaker_y - 20 - (i * 5),
                     speaker_x + offset + 10, speaker_y + 20 + (i * 5)],
                     start=-30, end=30, fill=(255, 255, 255, 200), width=3)

        # ICO dosyası olarak kaydet (birden fazla boyut)
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        images = []
        for s in sizes:
            images.append(img.resize(s, Image.Resampling.LANCZOS))

        images[0].save(output_file, format='ICO', sizes=[(s[0], s[1]) for s in sizes])
        print(f"✓ İkon oluşturuldu: {output_file}")
        print(f"  Boyutlar: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        return True

    except ImportError:
        print("❌ PIL/Pillow kütüphanesi bulunamadı!")
        print("   Yüklemek için: pip install Pillow")
        return False

    except Exception as e:
        print(f"❌ İkon oluşturulamadı: {e}")
        return False

if __name__ == '__main__':
    print("Internet Radyo Çalar - İkon Oluşturucu")
    print("=" * 50)

    success = create_radio_icon('radio_icon.ico')

    if success:
        print("\nİkon başarıyla oluşturuldu!")
        print("Build scriptini çalıştırarak EXE'yi oluşturabilirsiniz.")
    else:
        print("\nİkon oluşturulamadı.")
        print("Alternatif: Manuel olarak radio_icon.ico dosyası ekleyin.")
        print("İkon kaynakları:")
        print("  - https://www.flaticon.com")
        print("  - https://icons8.com")

    input("\nDevam etmek için Enter'a basın...")
