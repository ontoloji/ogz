#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internet Radyo Çalar İkon Oluşturucu
Kırmızı yuvarlak içinde beyaz "RPo" yazısı
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import sys

    def create_radio_icon(output_file='radio_icon.ico'):
        """Kırmızı daire içinde beyaz RPo ikonu oluştur"""

        # Farklı boyutlarda ikon oluştur
        sizes = [256, 128, 64, 48, 32, 16]
        images = []

        for size in sizes:
            # RGBA modunda şeffaf görüntü
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Kırmızı daire çiz
            margin = 2
            draw.ellipse([margin, margin, size-margin, size-margin],
                        fill='#E53935',  # Kırmızı
                        outline='#C62828',  # Koyu kırmızı kenarlık
                        width=max(1, size // 32))

            # Yazı tipi boyutu (ikon boyutuna göre)
            font_size = int(size * 0.35)

            try:
                # Sistem fontunu kullanmayı dene
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    # Varsayılan font
                    font = ImageFont.load_default()

            # "RPo" yazısını merkeze yerleştir
            text = "RPo"

            # Metin boyutunu hesapla
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Merkez pozisyon
            x = (size - text_width) // 2
            y = (size - text_height) // 2 - size // 20  # Biraz yukarı kaydır

            # Beyaz yazı
            draw.text((x, y), text, fill='white', font=font)

            images.append(img)

        # ICO dosyası olarak kaydet
        images[0].save(output_file, format='ICO',
                      sizes=[(s, s) for s in sizes],
                      append_images=images[1:])

        print(f"✓ İkon oluşturuldu: {output_file}")
        print(f"  Boyutlar: {', '.join([f'{s}x{s}' for s in sizes])}")
        return True

except ImportError:
    print("❌ PIL/Pillow kütüphanesi bulunamadı!")
    print("   Yüklemek için: pip install Pillow")
    sys.exit(1)

except Exception as e:
    print(f"❌ İkon oluşturulamadı: {e}")
    sys.exit(1)


if __name__ == '__main__':
    print("Internet Radyo Çalar - İkon Oluşturucu")
    print("=" * 50)
    print("Kırmızı yuvarlak içinde beyaz 'RPo' yazısı")
    print()

    success = create_radio_icon('radio_icon.ico')

    if success:
        print("\n✓ İkon başarıyla oluşturuldu!")
        print("  Uygulamada otomatik olarak kullanılacak.")
    else:
        print("\n✗ İkon oluşturulamadı.")

    input("\nDevam etmek için Enter'a basın...")
