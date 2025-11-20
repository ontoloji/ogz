# Meeting Translator

Teams ve benzeri online toplantılarda konuşulanları gerçek zamanlı olarak İngilizceden Türkçeye çeviren ve ekranda altyazı olarak gösteren Windows uygulaması.

## Özellikler

- ✅ **Gerçek Zamanlı Çeviri**: Konuşulanları anında algılar ve çevirir
- ✅ **Sistem Sesi Yakalama**: Hoparlörden çıkan sesleri dinler (mikrofon değil)
- ✅ **Yüksek Doğruluk**: OpenAI Whisper ile konuşma tanıma
- ✅ **Overlay Altyazı**: Ekranın altında veya üstünde şeffaf altyazı penceresi
- ✅ **Taşınabilir**: Altyazı penceresini istediğiniz yere sürükleyebilirsiniz
- ✅ **Hafif ve Hızlı**: Optimize edilmiş işleme döngüsü

## Gereksinimler

### Sistem Gereksinimleri
- **İşletim Sistemi**: Windows 10/11
- **RAM**: En az 4GB (8GB önerilir)
- **İşlemce**: Intel i5 veya AMD Ryzen 5 ve üzeri
- **Python**: 3.8+ (sadece kaynak koddan çalıştırıyorsanız)

## Hızlı Başlangıç

### 🚀 Seçenek 1: EXE Dosyası ile (ÖNERİLEN - Python Gerekmez!)

**En kolay yol - Python yüklemeden kullanın:**

1. **MeetingTranslator.exe** dosyasını indirin (veya build edin)
2. **Çift tıklayın ve çalıştırın**
3. İlk çalıştırmada Whisper modeli otomatik indirilecek (birkaç dakika)
4. Hazır! 🎉

**Not:** Windows Defender "Bilinmeyen uygulama" uyarısı verebilir - "Yine de çalıştır" seçin.

### 📦 Seçenek 2: Python ile Kaynak Koddan

Python yüklü ve kaynak kodu çalıştırmak istiyorsanız:

```bash
install.bat    # İlk kurulum
run.bat        # Uygulamayı çalıştır
```

## Kurulum Detayları

### 💻 EXE Dosyası Oluşturma (Geliştiriciler İçin)

Kendi bilgisayarınızda .exe dosyası oluşturmak için:

#### 1. Gereksinimleri Kurun
```bash
install.bat                      # Standart kurulum
pip install -r requirements_dev.txt  # PyInstaller'ı ekle
```

#### 2. EXE Oluşturun

**Tek dosya versiyon (önerilir - taşınabilir):**
```bash
build_exe.bat
```
Çıktı: `dist\MeetingTranslator.exe` (tek dosya, ~500MB)

**Dizin versiyon (daha hızlı başlar):**
```bash
build_exe_onedir.bat
```
Çıktı: `dist\MeetingTranslator\` klasörü

#### 3. Build Süresi
- İlk build: 5-10 dakika
- Sonraki build'ler: 2-3 dakika

#### 4. EXE Dosyasını Paylaşma
- Oluşan .exe dosyasını kopyalayıp başka bilgisayarlarda çalıştırabilirsiniz
- Python yüklemesi gerekmez
- İlk çalıştırmada Whisper modeli indirilir

### 🐍 Python ile Kurulum (Kaynak Kod)

#### 1. Python Kurulumu
Eğer Python yüklü değilse, [python.org](https://www.python.org/downloads/) adresinden Python 3.8+ sürümünü indirin ve kurun.

**Önemli**: Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin.

### 2. Proje Dosyalarını İndirme
```bash
# Git ile
git clone <repository-url>
cd meeting_translator

# veya ZIP olarak indirip çıkartın
```

### 3. Sanal Ortam Oluşturma (Önerilir)
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Gereksinimleri Kurma
```bash
pip install -r requirements.txt
```

**Not**: İlk kurulum birkaç dakika sürebilir çünkü PyTorch gibi büyük kütüphaneler indirilecektir.

## Windows Ses Ayarları

Uygulamanın sistem sesini yakalayabilmesi için Windows'ta **Stereo Mix** veya benzeri bir loopback cihazını etkinleştirmeniz gerekir:

### Stereo Mix'i Etkinleştirme

1. **Sağ alt köşedeki hoparlör simgesine sağ tıklayın** → "Ses ayarları" veya "Sound settings"
2. **"Ses Denetim Masası"nı açın** (Sound Control Panel)
3. **"Kayıt" (Recording) sekmesine gidin**
4. **Boş bir alana sağ tıklayın** → "Devre dışı cihazları göster" (Show Disabled Devices)
5. **"Stereo Mix"i bulun** → Sağ tıklayın → "Etkinleştir" (Enable)
6. **"Stereo Mix"e sağ tıklayın** → "Varsayılan Cihaz Olarak Ayarla" (Set as Default Device)

**Alternatif Yöntemler:**
- Bazı sistemlerde "Wave Out Mix", "What U Hear" veya "Loopback" adıyla görünebilir
- VB-Audio Virtual Cable gibi sanal ses cihazları da kullanılabilir

## Kullanım

### Uygulamayı Başlatma

```bash
python main.py
```

### İlk Çalıştırma
İlk çalıştırmada Whisper modeli indirilecektir (yaklaşık 150MB, birkaç dakika sürebilir).

### Kullanım Sırasında

1. **Uygulama başladığında** ekranda şeffaf bir altyazı penceresi görünecek
2. **Toplantınızı başlatın** (Teams, Zoom, Google Meet, vb.)
3. **Konuşmalar otomatik olarak algılanıp çevrilecek** ve altyazıda görünecek
4. **Pencereyi taşımak için** üst kısımdaki başlık çubuğunu sürükleyin
5. **Geçici gizlemek için** "−" butonuna basın (3 saniye sonra tekrar görünür)
6. **Kapatmak için** "✕" butonuna basın veya Ctrl+C

## Yapılandırma

`config.py` dosyasından ayarları değiştirebilirsiniz:

```python
# Whisper model boyutu (tiny, base, small, medium, large)
WHISPER_MODEL = "base"  # Daha iyi doğruluk için "small" veya "medium" kullanın

# Altyazı pozisyonu
SUBTITLE_POSITION = "bottom"  # veya "top"

# Altyazı boyutu
SUBTITLE_FONT_SIZE = 24  # Daha büyük veya küçük yapabilirsiniz

# Şeffaflık
SUBTITLE_OPACITY = 0.7  # 0.0 (tamamen şeffaf) - 1.0 (opak) arası
```

## Sorun Giderme

### "Ses cihazı bulunamadı" hatası
- Stereo Mix'in etkin olduğundan emin olun
- Ses ayarlarından varsayılan cihazı kontrol edin

### Konuşmalar algılanmıyor
- Toplantı sesinin Windows'ta çaldığından emin olun
- Ses seviyesini artırın
- Stereo Mix'in seviyesini kontrol edin

### Çeviri çok yavaş
- Daha küçük bir Whisper modeli seçin (`config.py` → `WHISPER_MODEL = "tiny"`)
- Bilgisayarınızın kaynaklarını kontrol edin

### GPU kullanmak isterseniz
PyTorch'un GPU destekli versiyonunu kurun:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Performans İpuçları

1. **Daha hızlı işleme** için `WHISPER_MODEL = "tiny"` veya `"base"` kullanın
2. **Daha iyi doğruluk** için `WHISPER_MODEL = "small"` veya `"medium"` kullanın
3. **GPU varsa** CUDA destekli PyTorch kurun
4. **Gereksiz uygulamaları kapatın** ve toplantı sırasında performansı artırın

## Teknik Detaylar

### Mimari
```
┌─────────────────┐
│  Sistem Sesi    │ (Hoparlör çıkışı)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Audio Capture   │ (sounddevice ile ses yakalama)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Speech-to-Text  │ (OpenAI Whisper)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Translator    │ (Google Translate API)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Subtitle Overlay│ (tkinter şeffaf pencere)
└─────────────────┘
```

### Kullanılan Teknolojiler
- **OpenAI Whisper**: Son teknoloji konuşma tanıma
- **Deep Translator**: Google Translate API wrapper
- **sounddevice**: Düşük gecikmeli ses yakalama
- **tkinter**: Platform bağımsız GUI
- **NumPy**: Hızlı ses işleme

## Lisans

MIT License - Kişisel ve ticari kullanım için serbesttir.

## Katkıda Bulunma

Hatalar, öneriler ve geliştirmeler için issue açabilir veya pull request gönderebilirsiniz.

## Sık Sorulan Sorular

**S: Mikrofonumu kapatırsam çalışır mı?**
C: Evet! Bu uygulama hoparlörden çıkan sesi dinler, mikrofonunuzu değil.

**S: İnternete ihtiyacım var mı?**
C: Whisper yerel olarak çalışır (internet gerekmez), ancak Google Translate için internet gereklidir. İnternetsiz çalışması için offline çeviri modelleri eklenebilir.

**S: Türkçeden İngilizceye de çevirebilir mi?**
C: `config.py` dosyasından `SOURCE_LANG` ve `TARGET_LANG` değerlerini değiştirerek istediğiniz dil çiftini kullanabilirsiniz.

**S: Başka toplantı uygulamalarında çalışır mı?**
C: Evet! Teams, Zoom, Google Meet, Discord veya ses çıkışı olan herhangi bir uygulamada çalışır.

**S: EXE dosyası neden bu kadar büyük (~500MB)?**
C: PyTorch ve Whisper modeli dahil edildiği için boyutu büyüktür. Alternatif olarak dizin versiyonunu kullanabilirsiniz.

**S: Windows Defender uyarı veriyor, güvenli mi?**
C: Evet, tamamen güvenlidir. PyInstaller ile oluşturulan yeni .exe dosyaları bazen "bilinmeyen yayıncı" uyarısı alabilir. Kaynak kodları inceleyebilirsiniz.

**S: Python versiyonu mu EXE versiyonu mu daha iyi?**
C:
- **EXE**: Daha kolay, Python gerekmez, taşınabilir
- **Python**: Daha esnek, özelleştirilebilir, daha küçük boyut

## İletişim

Sorularınız için issue açabilirsiniz.

---

**Keyifli toplantılar! 🎉**
