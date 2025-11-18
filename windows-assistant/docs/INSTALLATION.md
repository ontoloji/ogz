# 🔧 Kurulum Kılavuzu

## Sistem Gereksinimleri

### Zorunlu
- **İşletim Sistemi**: Windows 10 veya Windows 11
- **Python**: 3.8 veya üzeri
- **RAM**: En az 4 GB (8 GB önerilir)
- **Disk Alanı**: En az 500 MB

### Opsiyonel
- **Microsoft Outlook**: Takvim entegrasyonu için
- **Azure AD Hesabı**: Outlook Graph API için
- **İnternet Bağlantısı**: Outlook senkronizasyonu için

## Hızlı Kurulum (Windows)

### Yöntem 1: Otomatik Kurulum (Önerilen)

1. Projeyi indirin veya klonlayın
2. `install.bat` dosyasına çift tıklayın
3. Kurulumun tamamlanmasını bekleyin
4. `run.bat` ile uygulamayı başlatın

### Yöntem 2: Manuel Kurulum

#### Adım 1: Python Kontrolü

Komut istemcisini (CMD) açın ve şunu çalıştırın:

```bash
python --version
```

Python 3.8 veya üzeri sürüm görünmelidir. Görmüyorsanız:
1. https://www.python.org/downloads/ adresine gidin
2. Python'un son sürümünü indirin
3. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
4. Kurulumu tamamlayın
5. Bilgisayarınızı yeniden başlatın

#### Adım 2: Projeyi İndirin

**Git ile:**
```bash
git clone <repository-url>
cd windows-assistant
```

**Veya ZIP olarak:**
1. GitHub'dan projeyi ZIP olarak indirin
2. ZIP dosyasını açın
3. Komut istemcisinde proje klasörüne gidin

#### Adım 3: Sanal Ortam Oluşturun

```bash
python -m venv venv
```

#### Adım 4: Sanal Ortamı Etkinleştirin

```bash
venv\Scripts\activate
```

Başarılı olursa komut satırınızın başında `(venv)` görünecektir.

#### Adım 5: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

Bu işlem birkaç dakika sürebilir.

#### Adım 6: Uygulamayı Başlatın

```bash
python src/main.py
```

## Linux/Mac Kurulumu (Deneysel)

**Not**: Bu uygulama Windows için tasarlanmıştır, ancak Linux/Mac'te de çalıştırılabilir (bildirimler çalışmayabilir).

```bash
# Python 3 kurulumu (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Proje kurulumu
git clone <repository-url>
cd windows-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Outlook Entegrasyonu Kurulumu

### Adım 1: Azure AD Uygulama Kaydı

1. **Azure Portal'a gidin**: https://portal.azure.com
2. **Giriş yapın** Microsoft hesabınızla
3. **Azure Active Directory** seçin
4. **App registrations** > **New registration**

### Adım 2: Uygulama Bilgileri

- **Name**: `Personal Assistant` veya istediğiniz bir isim
- **Supported account types**:
  - "Accounts in any organizational directory and personal Microsoft accounts"
- **Redirect URI**:
  - Platform: Web
  - URI: `http://localhost:8000/auth/callback`

**Register** butonuna tıklayın.

### Adım 3: Client ID ve Secret

1. Uygulama sayfasında **Overview** sekmesinde **Application (client) ID**'yi kopyalayın
2. **Certificates & secrets** sekmesine gidin
3. **New client secret** butonuna tıklayın
4. Açıklama girin (örn: "desktop-app")
5. Süre seçin (örn: 24 ay)
6. **Add** butonuna tıklayın
7. **Value** sütunundaki değeri hemen kopyalayın (bir daha gösterilmeyecek!)

### Adım 4: API İzinleri

1. **API permissions** sekmesine gidin
2. **Add a permission** butonuna tıklayın
3. **Microsoft Graph** seçin
4. **Delegated permissions** seçin
5. Şu izinleri arayıp ekleyin:
   - `Calendars.Read`
   - `Calendars.Read.Shared`
   - `User.Read`
6. **Add permissions** butonuna tıklayın
7. (Opsiyonel) **Grant admin consent** butonuna tıklayın

### Adım 5: Uygulamada Yapılandırma

**Şu anda uygulama demo modunda çalışmaktadır.** Gerçek entegrasyon için:

1. `src/services/outlook_service.py` dosyasını açın
2. Dosyanın sonundaki yorum satırlarındaki örnek kodu kullanın
3. `msal` kütüphanesini yükleyin:
   ```bash
   pip install msal requests
   ```
4. Client ID ve Secret değerlerini güvenli bir şekilde saklayın

## Sorun Giderme

### "Python bulunamadı" Hatası

**Çözüm:**
1. Python'u yükleyin: https://www.python.org/downloads/
2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
3. Bilgisayarı yeniden başlatın

### "pip: command not found" Hatası

**Çözüm:**
```bash
python -m ensurepip --upgrade
```

### Paket Kurulum Hataları

**Çözüm 1**: pip'i güncelleyin
```bash
python -m pip install --upgrade pip
```

**Çözüm 2**: Microsoft Visual C++ yükleyin
- https://aka.ms/vs/17/release/vc_redist.x64.exe

### PySide6 Kurulum Hatası

**Çözüm:**
```bash
pip install --upgrade pip setuptools wheel
pip install PySide6
```

### Uygulama Açılmıyor

**Kontrol Listesi:**
1. Python 3.8+ kurulu mu?
2. Sanal ortam etkinleştirildi mi?
3. Tüm bağımlılıklar yüklendi mi?
4. Komut satırında hata mesajı var mı?

**Detaylı Hata Kontrolü:**
```bash
python src/main.py 2>&1 | tee error.log
```

### Bildirimler Çalışmıyor

**Windows 10/11:**
1. **Ayarlar** > **Sistem** > **Bildirimler ve eylemler**
2. "Uygulama ve diğer gönderenlerden bildirim al" açık olmalı
3. Python'un bildirim izni olmalı

**Alternatif Çözüm:**
```bash
pip uninstall win10toast
pip install win10toast-ng
```

## Başlangıçta Otomatik Çalışma

### Yöntem 1: Task Scheduler (Önerilen)

1. **Task Scheduler** uygulamasını açın
2. **Create Basic Task** seçin
3. İsim: "Personal Assistant"
4. Trigger: "When I log on"
5. Action: "Start a program"
6. Program: `C:\...\windows-assistant\run.bat`
7. Finish

### Yöntem 2: Startup Klasörü

1. **Win + R** tuşlarına basın
2. `shell:startup` yazın ve Enter'a basın
3. `run.bat` dosyasının kısayolunu bu klasöre kopyalayın

## Güncelleme

### Git ile:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Manuel:
1. Yeni sürümü indirin
2. `data/` klasörünü yedekleyin
3. Eski dosyaları silin
4. Yeni dosyaları çıkarın
5. `data/` klasörünü geri kopyalayın
6. `install.bat` çalıştırın

## Kaldırma

1. Uygulama çalışıyorsa kapatın
2. Proje klasörünü silin
3. (Opsiyonel) Python'u kaldırın

## Destek

Sorun yaşıyorsanız:
1. Bu kılavuzu tekrar okuyun
2. [GitHub Issues](https://github.com/yourusername/windows-assistant/issues) sayfasına bakın
3. Yeni bir issue açın (hata mesajlarını ekleyin)
