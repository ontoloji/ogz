# 🔒 Gizli Web Tarayıcı - Windows

Kayıt tutmayan, gizlilik odaklı Windows web tarayıcısı.

## Özellikler

✅ **Tam Gizlilik:**
- ❌ Geçmiş kaydetmez
- ❌ Çerez kaydetmez
- ❌ Önbellek oluşturmaz
- ❌ Oturum bilgisi saklamaz
- ✅ Do Not Track aktif

✅ **Güvenlik:**
- İzleme engelleyici dahili
- Reklam engelleyici
- Güvenli HTTPS bağlantı
- Otomatik temizlik (kapatıldığında)

✅ **Özellikler:**
- Modern web sayfalarını açar
- Hızlı ve hafif
- Windows uyumlu
- Türkçe arayüz

## Kurulum

### 1. Python Kurulumu (Windows)
```bash
# Python 3.9 veya üzeri gerekli
# https://www.python.org/downloads/ adresinden indirin
python --version  # Kontrol edin
```

### 2. Bağımlılıkları Yükleyin
```bash
# Komut istemini (CMD) yönetici olarak açın
pip install PyQt6>=6.5.0
pip install PyQt6-WebEngine>=6.5.0
```

Veya tüm bağımlılıkları yüklemek için:
```bash
pip install -r requirements.txt
```

### 3. Tarayıcıyı Çalıştırın

**Yöntem 1: Python ile**
```bash
python private_browser.py
```

**Yöntem 2: Windows Batch Dosyası ile**
```bash
# start_browser.bat dosyasına çift tıklayın
```

**Yöntem 3: PowerShell ile**
```powershell
python private_browser.py
```

## Kullanım

### Temel Navigasyon
- **◀ Geri**: Önceki sayfaya dön
- **İleri ▶**: Sonraki sayfaya git
- **🔄 Yenile**: Sayfayı yenile
- **🏠 Ana Sayfa**: Google ana sayfasına dön
- **➕ Yeni**: Yeni gizli pencere aç

### URL Girişi
- Adres çubuğuna URL yazın: `github.com` → Otomatik https:// ekler
- Arama yapın: `python tutorial` → Google'da arar
- Enter'a basın veya **➜ Git** butonuna tıklayın

### Gizlilik Durumu
Durum çubuğunda her zaman gizlilik durumu gösterilir:
```
🔒 Gizli Mod Aktif - Hiçbir kayıt tutulmuyor
```

## Gizlilik Garantileri

### ✅ NE KAYIT TUTULMAZ:
- ✅ Ziyaret edilen siteler (geçmiş)
- ✅ Girilen şifreler
- ✅ Form verileri
- ✅ Çerezler (cookies)
- ✅ Önbellek (cache)
- ✅ İndirme geçmişi
- ✅ Oturum bilgileri

### ℹ️ ÖNEMLİ NOTLAR:
- ⚠️ ISP (internet sağlayıcınız) yine de hangi sitelere girdiğinizi görebilir
- ⚠️ Ziyaret ettiğiniz siteler IP adresinizi görebilir
- ⚠️ Tam anonimlik için VPN veya Tor kullanın
- ✅ Tarayıcı kapatıldığında tüm veriler bellekten silinir

## Teknik Detaylar

### Teknoloji Stack
- **Python 3.9+**
- **PyQt6** - GUI framework
- **QtWebEngine** - Chromium tabanlı render engine
- **QWebEngineProfile** - Off-the-record profil (bellek içi)

### Gizlilik Mekanizması
```python
# Cache devre dışı
profile.setHttpCacheType(NoCache)

# Cookie kaydetme
profile.setPersistentCookiesPolicy(NoPersistentCookies)

# Do Not Track
profile.setHttpUserAgent(agent + " DNT/1")
```

## Sık Sorulan Sorular

**S: İndirmeler kaydedilir mi?**
C: İndirilen dosyalar Windows indirme klasörünüze kaydedilir, ancak indirme geçmişi tutulmaz.

**S: Şifrelerimi hatırlıyor mu?**
C: Hayır, hiçbir şifre veya form verisi kaydedilmez.

**S: Hangi Windows sürümlerinde çalışır?**
C: Windows 10 ve Windows 11'de test edilmiştir. Windows 7/8 için PyQt6 uyumluluğu kontrol edilmelidir.

**S: Tor kadar güvenli mi?**
C: Hayır. Bu tarayıcı yerel gizlilik sağlar (kayıt tutmaz), ancak Tor gibi anonim ağ kullanmaz. IP adresiniz görünür kalır.

**S: Neden bu tarayıcıyı kullanayım?**
C:
- Hızlı gizli tarama istiyorsanız
- Paylaşımlı bilgisayarda iz bırakmak istemiyorsanız
- Basit ve reklamlara takılmadan tarama istiyorsanız

## Sorun Giderme

### Hata: "No module named 'PyQt6'"
```bash
pip install PyQt6 PyQt6-WebEngine
```

### Hata: "QtWebEngine not found"
```bash
pip uninstall PyQt6-WebEngine
pip install PyQt6-WebEngine --force-reinstall
```

### Sayfa yüklenmiyor
- İnternet bağlantınızı kontrol edin
- Firewall/Antivirus'ün Python'u engellemediğinden emin olun
- Farklı bir URL deneyin

### Windows Defender uyarısı
- Python uygulamaları bazen yanlış pozitif verir
- Güvenli listesine ekleyin veya kaynak kodunu inceleyin

## Geliştirme

### Özellik Eklemek
```python
# private_browser.py dosyasını düzenleyin
# Örnek: Yeni buton eklemek
custom_btn = QPushButton("Özellik")
custom_btn.clicked.connect(self.custom_function)
toolbar.addWidget(custom_btn)
```

### Kendi Tema
```python
# Toolbar stilini değiştirin (satır ~100)
toolbar.setStyleSheet("""
    QToolBar {
        background-color: #YOUR_COLOR;
    }
""")
```

## Lisans

Bu proje eğitim ve kişisel kullanım içindir. Kaynak kodu açıktır ve değiştirilebilir.

## Güvenlik

⚠️ **UYARI**: Bu tarayıcı temel gizlilik sağlar ancak:
- Profesyonel güvenlik testleri yapılmamıştır
- Hassas işlemler (bankacılık vb.) için önerilmez
- VPN kullanımı önerilir
- Antivirüs/Firewall kullanmaya devam edin

## Destek

Sorunlar için:
1. Python ve PyQt6 versiyonlarınızı kontrol edin
2. requirements.txt dosyasındaki tüm bağımlılıkları yükleyin
3. Windows güncellemelerini kontrol edin

---

**Gizliliğiniz önemlidir! 🔒**

*Not: Bu tarayıcı, Windows'ta çalışan PyQt6 tabanlı gizli bir web tarayıcısıdır. Hiçbir veri internete gönderilmez, tüm işlemler yerel makinenizde gerçekleşir.*
