# 🚀 Hızlı Başlangıç Rehberi

## Windows Kullanıcıları

### Adım 1: Python Kurulumu
1. https://www.python.org/downloads/ adresine gidin
2. "Download Python" butonuna tıklayın
3. İndirdiğiniz dosyayı çalıştırın
4. **ÖNEMLİ**: "Add Python to PATH" kutucuğunu işaretleyin
5. "Install Now" tıklayın

### Adım 2: Uygulamayı Başlatma
1. `wealth_tracker` klasörüne gidin
2. `run.bat` dosyasına çift tıklayın

**VEYA**

Komut istemcisinde:
```cmd
cd wealth_tracker
python main.py
```

---

## macOS Kullanıcıları

### Adım 1: Python Kontrolü
Terminal'i açın ve şu komutu çalıştırın:
```bash
python3 --version
```

Eğer Python yüklü değilse:
```bash
# Homebrew ile yükleme (önerilir)
brew install python3

# VEYA https://www.python.org/downloads/ adresinden indirin
```

### Adım 2: Uygulamayı Başlatma
Terminal'de:
```bash
cd wealth_tracker
./run.sh
```

**VEYA**

```bash
cd wealth_tracker
python3 main.py
```

---

## İlk Kullanım

### 1️⃣ Kullanıcı Oluşturma
- Uygulama açıldığında **"Yeni Kullanıcı"** butonuna tıklayın
- Kullanıcı adı ve şifre belirleyin
- Şifrenizi unutmayın! (veritabanında hash'li olarak saklanır)

### 2️⃣ Giriş Yapma
- Oluşturduğunuz kullanıcı adı ve şifreyi girin
- **"Giriş"** butonuna tıklayın

### 3️⃣ İlk Birikinizi Ekleyin
1. **"Yeni Birikim Ekle"** butonuna tıklayın
2. Örnek birikim:
   ```
   Varlık Tipi: Değerli Maden
   Varlık Adı: Altın
   Miktar: 10
   Alış Fiyatı: 2500
   Alış Tarihi: 2025-01-15
   Notlar: 24 ayar külçe altın
   ```
3. **"Kaydet"** tıklayın

### 4️⃣ Fiyatları Güncelle
- **"Fiyatları Güncelle"** butonuna tıklayın
- Sistem otomatik olarak güncel altın, gümüş ve döviz fiyatlarını çeker
- Toplam portföy değeriniz hesaplanır

---

## Örnek Kullanım Senaryoları

### 📊 Senaryo 1: Altın Takibi
```
10 gram altın aldınız
Gram fiyatı: 2,500 TL
Toplam: 25,000 TL

Uygulamaya kaydedin:
- Varlık Tipi: Değerli Maden
- Varlık Adı: Altın
- Miktar: 10
- Alış Fiyatı: 2500

Fiyatlar güncellendiğinde:
Güncel Gram Fiyatı: 2,850 TL
Toplam Değer: 28,500 TL
Kazanç: 3,500 TL
```

### 💵 Senaryo 2: Döviz Takibi
```
1000 USD aldınız
Kur: 34.50 TL/USD
Toplam: 34,500 TL

Uygulamaya kaydedin:
- Varlık Tipi: Döviz
- Varlık Adı: Dolar
- Miktar: 1000
- Alış Fiyatı: 34.50

Kur güncellendiğinde:
Güncel Kur: 35.20 TL/USD
Toplam Değer: 35,200 TL
Kazanç: 700 TL
```

### 🏦 Senaryo 3: Vadeli Mevduat
```
50,000 TL vadeli mevduat
Faiz Oranı: %45 (yıllık)
Vade: 90 gün

Uygulamaya kaydedin:
- Varlık Tipi: Vadeli Yatırım
- Varlık Adı: Mevduat
- Miktar: 50000
- Alış Fiyatı: 1 (veya faiz dahil gelecek değer)
- Notlar: %45 faiz, 90 gün vade
```

---

## Sık Sorulan Sorular

### ❓ Şifremi unuttum, ne yapmalıyım?
Veritabanı dosyasını (`wealth_tracker.db`) silip yeni kullanıcı oluşturabilirsiniz. **UYARI**: Bu işlem tüm verilerinizi siler!

### ❓ Verilerim güvenli mi?
Evet! Tüm veriler bilgisayarınızda yerel olarak saklanır. İnternet bağlantısı sadece fiyat güncellemeleri için kullanılır.

### ❓ İnternet olmadan çalışır mı?
Evet, ama fiyatlar güncellenemez. Mevcut verilerinizi görüntülemeye devam edebilirsiniz.

### ❓ Birden fazla kullanıcı olabilir mi?
Evet! Her kullanıcı kendi hesabı ve birikimlerini ayrı tutabilir.

### ❓ Verisetimi nasıl yedeklerim?
`wealth_tracker.db` dosyasını kopyalayın. Bu dosya tüm verilerinizi içerir.

---

## Klavye Kısayolları

- **Enter** (Giriş ekranında): Giriş yap
- **Tab**: Alanlar arası geçiş
- **Escape**: Pencereyi kapat

---

## İletişim ve Destek

- Hata bildirimi için: GitHub Issues
- Özellik önerileri için: GitHub Discussions

---

**Keyifli kullanımlar! 💰📈**
