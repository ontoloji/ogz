# 🎵 Ambient Sounds / Background Noise Sistemi

30 farklı ambient/doğa sesi ile konsantrasyon ve rahatlama.

## 🌟 Özellikler

- **30 Farklı Ses**: Doğa, ambient, rahatlama
- **Kombinasyon**: Birden fazla ses aynı anda
- **Offline Çalışma**: İnternet gerektirmez
- **Radio Modu**: Noise açıldığında radio durur
- **Ses Kontrolü**: Her ses için ayrı volume

## 📂 Ses Kategorileri

### 🌿 Doğa Sesleri (10)
1. 🌧️ Yağmur
2. ⚡ Gök Gürültüsü
3. 💨 Rüzgar
4. 🌊 Okyanus Dalgaları
5. 〰️ Nehir
6. 💧 Şelale
7. 🌲 Orman
8. 🐦 Kuş Sesleri
9. 🦗 Cırcırböceği
10. 🔥 Ateş

### 🎧 Ambient Sesleri (10)
11. ⬜ Beyaz Gürültü
12. 🟫 Kahverengi Gürültü
13. 🌸 Pembe Gürültü
14. 🌀 Vantilatör
15. 🕐 Saat Tik Tak
16. 🎐 Rüzgar Çanları
17. ☕ Kafe
18. 📚 Kütüphane
19. 🚂 Tren
20. ✈️ Uçak

### 😌 Rahatlama Sesleri (10)
21. 🌙 Gece Sesleri
22. 🏕️ Kamp Ateşi
23. 🐱 Kedi Mırıltısı
24. 🪵 Şömine
25. 🚿 Duş
26. ⛲ Çeşme
27. 🐸 Kurbağalar
28. 🦅 Martılar
29. 🏖️ Sahil Dalgaları
30. 🌊 Su Altı

## 📥 Ses Dosyalarını İndirme

### Otomatik Kontrol
```bash
python3 download_sounds.py
```

### Manuel İndirme

**Adım 1:** `sounds/` klasörü oluşturun

**Adım 2:** Ses dosyalarını indirin:
- **Freesound.org**: CC0 lisanslı ücretsiz sesler
- **Zapsplat.com**: Ücretsiz (kayıt gerekli)
- **myNoise.net**: Yüksek kaliteli ambient sesler

**Adım 3:** Ses dosyalarını `sounds/` klasörüne koyun
```
sounds/
├── rain.mp3
├── thunder.mp3
├── wind.mp3
└── ... (30 dosya)
```

### Ses Dosyası Özellikleri
- **Format**: MP3, OGG veya WAV
- **Süre**: 30-60 saniye (loop için)
- **Kalite**: 128kbps minimum
- **Loop**: Seamless (başı-sonu uyumlu)

## 🎮 Kullanım

### Temel Kullanım
1. **Noise Modu**: "🎵 Noise" butonuna tıkla
2. **Ses Seç**: İstediğin seslere tıkla (yeşil = aktif)
3. **Kombinasyon**: Birden fazla ses seçebilirsin
4. **Volume**: Her ses için ayrı ses kontrolü

### Örnek Kombinasyonlar

**Çalışma/Odaklanma:**
```
☕ Kafe + ⬜ Beyaz Gürültü + 🌧️ Yağmur
```

**Uyku:**
```
🌧️ Yağmur + ⚡ Gök Gürültüsü + 🌙 Gece Sesleri
```

**Rahatlama:**
```
🌊 Okyanus + 🐦 Kuş Sesleri + 💨 Rüzgar
```

**Meditasyon:**
```
🏖️ Sahil + 🎐 Rüzgar Çanları + ⛲ Çeşme
```

**Kafe Ortamı:**
```
☕ Kafe + 🕐 Saat + 📚 Kütüphane
```

## 🔧 Teknik Detaylar

### Multi-Channel Playback
- Her ses ayrı VLC player instance
- Aynı anda 30 ses çalabilir
- Bağımsız volume kontrol
- Loop mode (sonsuz tekrar)

### Mod Switching
- **Radio Modu**: Normal radyo dinleme
- **Noise Modu**: Ambient sesler
- Otomatik switching (radio durur)

### Dosya Yapısı
```
project/
├── internet_radio_player.py  # Ana uygulama
├── ambient_sounds.py          # Ses tanımları
├── download_sounds.py         # İndirme yardımcısı
├── sounds/                    # Ses dosyaları klasörü
│   ├── rain.mp3
│   ├── ocean.mp3
│   └── ... (30 dosya)
└── AMBIENT_SOUNDS_README.md   # Bu dosya
```

## 💡 İpuçları

### Ses Bul up

**Freesound.org:**
1. Kayıt ol (ücretsiz)
2. "rain loop" ara
3. CC0 filtresi uygula
4. İndir

**YouTube:**
1. "ambient sounds 1 hour" ara
2. youtube-dl ile indir
3. Audacity'de 30 sn loop kes

**myNoise.net:**
1. İstediğin sesi seç
2. "Download" butonuna tıkla
3. sounds/ klasörüne taşı

### Loop Oluşturma (Audacity)

1. Ses dosyasını aç
2. 30 saniyelik bölüm seç
3. Fade in/out ekle (başı-sonu)
4. MP3 olarak export et
5. sounds/ klasörüne kaydet

### Performans

- **30 ses aynı anda**: ~100 MB RAM
- **CPU kullanımı**: %5-10
- **Disk alanı**: ~300 MB (30 dosya)

## 🆘 Sorun Giderme

### "Ses dosyası bulunamadı"
**Çözüm:** `sounds/` klasörünü kontrol edin, dosya isimlerinin doğru olduğundan emin olun

### "Ses çalmıyor"
**Çözüm:** VLC kurulu olduğundan emin olun

### "Laggy/Takıllı"
**Çözüm:** Aynı anda çok fazla ses açmayın (max 5-6 önerilir)

## 📝 Lisans

Ses dosyaları için CC0 veya telif hakkı uyumlu içerik kullanın.

## 🔗 Önerilen Kaynaklar

- **Freesound**: https://freesound.org/
- **Zapsplat**: https://www.zapsplat.com/
- **BBC Sound Effects**: https://sound-effects.bbcrewind.co.uk/
- **myNoise**: https://mynoise.net/
- **Ambient Mixer**: https://www.ambient-mixer.com/

---

**Not:** Ambient sounds özelliği tamamen offline çalışır. Ses dosyalarını bir kez indirip `sounds/` klasörüne koyduktan sonra internet bağlantısı gerektirmez.
