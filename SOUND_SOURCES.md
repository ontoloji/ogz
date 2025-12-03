# 🎵 Ambient Ses Dosyaları Kaynakları

## 📥 Hızlı İndirme Linkleri

### 1. Freesound.org (Önerilen)
**Avantajları:** CC0 lisanslı, yasal, ücretsiz, yüksek kalite

**Nasıl kullanılır:**
1. https://freesound.org hesap aç (ücretsiz)
2. Aşağıdaki direkt linkleri kullan:

#### Doğa Sesleri
- **Yağmur:** https://freesound.org/search/?q=rain+loop&f=license%3A%22Creative+Commons+0%22
- **Gök Gürültüsü:** https://freesound.org/search/?q=thunder+storm&f=license%3A%22Creative+Commons+0%22
- **Okyanus:** https://freesound.org/search/?q=ocean+waves+loop&f=license%3A%22Creative+Commons+0%22
- **Nehir:** https://freesound.org/search/?q=river+flowing&f=license%3A%22Creative+Commons+0%22
- **Şelale:** https://freesound.org/search/?q=waterfall&f=license%3A%22Creative+Commons+0%22
- **Orman:** https://freesound.org/search/?q=forest+ambience&f=license%3A%22Creative+Commons+0%22
- **Kuş Sesleri:** https://freesound.org/search/?q=birds+chirping&f=license%3A%22Creative+Commons+0%22
- **Ateş:** https://freesound.org/search/?q=fire+crackling&f=license%3A%22Creative+Commons+0%22

#### Ambient Sesleri
- **Beyaz Gürültü:** https://freesound.org/search/?q=white+noise&f=license%3A%22Creative+Commons+0%22
- **Kahverengi Gürültü:** https://freesound.org/search/?q=brown+noise&f=license%3A%22Creative+Commons+0%22
- **Pembe Gürültü:** https://freesound.org/search/?q=pink+noise&f=license%3A%22Creative+Commons+0%22
- **Vantilatör:** https://freesound.org/search/?q=fan+spinning&f=license%3A%22Creative+Commons+0%22
- **Kafe:** https://freesound.org/search/?q=coffee+shop+ambience&f=license%3A%22Creative+Commons+0%22

#### Rahatlama Sesleri
- **Kedi Mırıltısı:** https://freesound.org/search/?q=cat+purring&f=license%3A%22Creative+Commons+0%22
- **Şömine:** https://freesound.org/search/?q=fireplace&f=license%3A%22Creative+Commons+0%22
- **Duş:** https://freesound.org/search/?q=shower+water&f=license%3A%22Creative+Commons+0%22

### 2. BBC Sound Effects (Ücretsiz, Kaliteli)
https://sound-effects.bbcrewind.co.uk/

- 16,000+ ücretsiz ses efekti
- Profesyonel kalite
- Ticari kullanım için uygun
- Direkt indirme

### 3. Zapsplat (Ücretsiz, Kayıt Gerekli)
https://www.zapsplat.com/

- 140,000+ ses efekti
- Ücretsiz hesap ile sınırsız indirme
- Kategorilere göre organize
- MP3 ve WAV formatları

### 4. Epidemic Sound (Premium, Deneme Var)
https://www.epidemicsound.com/

- 30 günlük ücretsiz deneme
- Yüksek kalite ambient sesler
- Profesyonel kullanım için

## 🛠️ Ses Dosyası Hazırlama

### Gereksinimler
- **Format:** MP3, OGG veya WAV
- **Süre:** 30-60 saniye (loop için)
- **Kalite:** 128kbps veya üzeri
- **Loop:** Başı-sonu uyumlu (seamless)

### Audacity ile Loop Oluşturma

1. Audacity'yi indir: https://www.audacityteam.org/
2. Ses dosyasını aç
3. 30 saniye seç (dosya çok uzunsa)
4. Effect → Fade In/Fade Out (başta ve sonda)
5. Export → MP3
6. `sounds/` klasörüne kaydet

### ffmpeg ile Dönüştürme

```bash
# WAV'ı MP3'e çevir
ffmpeg -i input.wav -b:a 128k sounds/rain.mp3

# Ses seviyesini normalize et
ffmpeg -i input.mp3 -af "volume=1.5" sounds/rain.mp3

# 30 saniye kes
ffmpeg -i input.mp3 -ss 0 -t 30 sounds/rain.mp3
```

## 📋 Gerekli Dosya Listesi

İşte `sounds/` klasörüne koymanız gereken 30 dosya:

### Doğa (10 dosya)
- [ ] `rain.mp3` - Yağmur
- [ ] `thunder.mp3` - Gök gürültüsü
- [ ] `wind.mp3` - Rüzgar
- [ ] `ocean.mp3` - Okyanus dalgaları
- [ ] `river.mp3` - Nehir
- [ ] `waterfall.mp3` - Şelale
- [ ] `forest.mp3` - Orman
- [ ] `birds.mp3` - Kuş sesleri
- [ ] `crickets.mp3` - Cırcır böceği
- [ ] `fire.mp3` - Ateş

### Ambient (10 dosya)
- [ ] `white_noise.mp3` - Beyaz gürültü
- [ ] `brown_noise.mp3` - Kahverengi gürültü
- [ ] `pink_noise.mp3` - Pembe gürültü
- [ ] `fan.mp3` - Vantilatör
- [ ] `clock.mp3` - Saat tik tak
- [ ] `wind_chimes.mp3` - Rüzgar çanları
- [ ] `coffee_shop.mp3` - Kafe
- [ ] `library.mp3` - Kütüphane
- [ ] `train.mp3` - Tren
- [ ] `airplane.mp3` - Uçak

### Rahatlama (10 dosya)
- [ ] `night.mp3` - Gece sesleri
- [ ] `campfire.mp3` - Kamp ateşi
- [ ] `cat_purr.mp3` - Kedi mırıltısı
- [ ] `fireplace.mp3` - Şömine
- [ ] `shower.mp3` - Duş
- [ ] `fountain.mp3` - Çeşme
- [ ] `frogs.mp3` - Kurbağalar
- [ ] `seagulls.mp3` - Martılar
- [ ] `beach.mp3` - Sahil dalgaları
- [ ] `underwater.mp3` - Su altı

## 💡 Pro İpuçları

1. **Test Et:** Her sesi indirdikten sonra VLC'de aç ve seamless loop için kontrol et
2. **Normalize Et:** Tüm seslerin ses seviyesi yaklaşık aynı olsun
3. **Backup Al:** İndirdiğin seslerin yedeğini al
4. **Playlist Oluştur:** Favori kombinasyonlarını not al

## ⚖️ Telif Hakları

**Dikkat:** Sadece telif hakkı olmayan veya CC0/CC-BY lisanslı sesleri kullan!

- ✅ Freesound CC0
- ✅ BBC Sound Effects
- ✅ Kendi kaydettiğin sesler
- ❌ YouTube'dan telif hakkı korumalı içerik
- ❌ Spotify, Apple Music'ten kayıt

## 🆘 Sorun mu yaşıyorsun?

Sesleri indirmekte zorlanıyorsan:
1. `AMBIENT_SOUNDS_README.md` dosyasını oku
2. Freesound.org'a üye ol (5 dakika)
3. Her sesi tek tek ara ve indir (30 dakika)
4. Dosya adlarını doğru yaz (`rain.mp3`, `ocean.mp3`, vb.)

---

**İyi dinlemeler! 🎵**
