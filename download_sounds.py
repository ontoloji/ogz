#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ambient Ses Dosyalarını İndirme Scripti

NOT: Bu script temsilidir. Gerçek ses dosyaları için:
1. Freesound.org'dan CC0 lisanslı sesler indirin
2. Veya kendi ses dosyalarınızı kullanın
3. sounds/ klasörüne yerleştirin

Her ses dosyası:
- 30-60 saniye loop
- MP3 veya OGG format
- 128kbps veya daha yüksek
- Loop için seamless (başı-sonu uyumlu)
"""

import os
import sys

# Ses dosyaları için önerilen kaynaklar
SOUND_SOURCES = {
    "Freesound": "https://freesound.org/ (CC0 lisanslı, ücretsiz)",
    "Zapsplat": "https://www.zapsplat.com/ (Ücretsiz, kayıt gerekli)",
    "BBC Sound Effects": "https://sound-effects.bbcrewind.co.uk/ (Ücretsiz)",
    "YouTube Audio Library": "https://studio.youtube.com/channel/UCxxx/music (Ücretsiz)",
    "Ambient Mixer": "https://www.ambient-mixer.com/ (Online, indirilebilir)",
}

# Örnek arama terimleri
SEARCH_TERMS = {
    "rain.mp3": "rain loop ambient",
    "thunder.mp3": "thunder storm loop",
    "wind.mp3": "wind howling loop",
    "ocean.mp3": "ocean waves loop",
    "river.mp3": "river flowing loop",
    "waterfall.mp3": "waterfall loop",
    "forest.mp3": "forest ambience loop",
    "birds.mp3": "birds chirping loop",
    "crickets.mp3": "crickets night loop",
    "fire.mp3": "crackling fire loop",
    "white_noise.mp3": "white noise loop",
    "brown_noise.mp3": "brown noise loop",
    "pink_noise.mp3": "pink noise loop",
    "fan.mp3": "fan spinning loop",
    "clock.mp3": "clock ticking loop",
    "wind_chimes.mp3": "wind chimes loop",
    "coffee_shop.mp3": "coffee shop ambience",
    "library.mp3": "library ambience",
    "train.mp3": "train travel loop",
    "airplane.mp3": "airplane cabin loop",
    "night.mp3": "night sounds loop",
    "campfire.mp3": "campfire crackling loop",
    "cat_purr.mp3": "cat purring loop",
    "fireplace.mp3": "fireplace crackling loop",
    "shower.mp3": "shower water loop",
    "fountain.mp3": "water fountain loop",
    "frogs.mp3": "frogs croaking loop",
    "seagulls.mp3": "seagulls crying loop",
    "beach.mp3": "beach waves loop",
    "underwater.mp3": "underwater bubbles loop",
}


def create_sounds_directory():
    """sounds/ klasörünü oluştur"""
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        print("✓ sounds/ klasörü oluşturuldu")
    else:
        print("✓ sounds/ klasörü mevcut")


def check_existing_sounds():
    """Mevcut ses dosyalarını kontrol et"""
    if not os.path.exists("sounds"):
        return []

    existing = []
    for filename in os.listdir("sounds"):
        if filename.endswith(('.mp3', '.ogg', '.wav')):
            existing.append(filename)

    return existing


def print_instructions():
    """Kullanıcıya talimatları göster"""
    print("\n" + "="*60)
    print("  AMBIENT SES DOSYALARI İNDİRME REHBERİ")
    print("="*60)
    print()
    print("30 farklı ambient ses dosyası gerekiyor.")
    print()
    print("📁 Konum: sounds/ klasörü")
    print("📝 Format: MP3, OGG veya WAV")
    print("⏱️  Süre: 30-60 saniye loop")
    print("🔊 Kalite: 128kbps veya üzeri")
    print()
    print("🌐 ÖNERİLEN KAYNAKLAR:")
    print("-" * 60)
    for name, url in SOUND_SOURCES.items():
        print(f"  • {name}: {url}")
    print()
    print("🔍 ARAMA TERİMLERİ:")
    print("-" * 60)
    for i, (filename, search) in enumerate(SEARCH_TERMS.items(), 1):
        print(f"  {i:2d}. {filename:20s} → \"{search}\"")
    print()
    print("💡 HIZLI YÖNTEMLobby:")
    print("-" * 60)
    print("  1. myNoise.net'ten indirin (yüksek kalite)")
    print("  2. YouTube'dan 'ambient sounds 1 hour' arayın")
    print("  3. Audacity ile 30 saniyelik loop oluşturun")
    print()
    print("⚠️  NOT: Telif hakları uyumlu/ücretsiz sesler kullanın!")
    print("="*60)


def main():
    print()
    print("🎵 Ambient Ses Dosyaları Yönetimi")
    print()

    create_sounds_directory()
    existing = check_existing_sounds()

    if existing:
        print(f"\n✓ Bulunan ses dosyaları ({len(existing)}/30):")
        for sound in sorted(existing):
            print(f"  • {sound}")

    missing = 30 - len(existing)
    if missing > 0:
        print(f"\n⚠️  Eksik dosya sayısı: {missing}")
        print_instructions()
    else:
        print("\n✅ Tüm ses dosyaları mevcut!")

    print("\n" + "="*60)
    print("Hazır olduğunuzda programı çalıştırabilirsiniz.")
    print("="*60)
    print()


if __name__ == '__main__':
    main()
