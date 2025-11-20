# Multi-AI Question Tool

Windows için PyQt6 tabanlı çoklu yapay zeka soru-cevap uygulaması. Soracağınız soruları birden fazla yapay zekaya aynı anda gönderin ve cevapları karşılaştırın.

## Özellikler

- 🤖 **Çoklu AI Desteği**: OpenAI GPT, Anthropic Claude, Google Gemini, Cohere
- ⚡ **Paralel İşlem**: Tüm AI'lara aynı anda soru gönderme
- 📊 **Karşılaştırmalı Görünüm**: Tüm cevapları alt alta listeleme
- 💾 **Kayıt Özelliği**: Cevapları metin dosyası olarak kaydetme
- ⚙️ **Kolay Konfigürasyon**: GUI üzerinden API key yönetimi
- 🎨 **Modern Arayüz**: PyQt6 tabanlı kullanıcı dostu tasarım

## Desteklenen AI Platformları

| Platform | Model | API Key Gerekli |
|----------|-------|----------------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | ✅ Evet |
| **Anthropic** | Claude-3.5-Sonnet, Claude-3-Opus | ✅ Evet |
| **Google** | Gemini-Pro | ✅ Evet |
| **Cohere** | Command | ✅ Evet (Opsiyonel) |

## Kurulum

### 1. Python Kurulumu

Python 3.10 veya üzeri gereklidir.

```bash
python --version  # 3.10+ olmalı
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements_ai.txt
```

Alternatif olarak, sadece ihtiyacınız olan AI provider'ları yükleyebilirsiniz:

```bash
# Temel GUI için
pip install PyQt6

# OpenAI için
pip install openai

# Anthropic Claude için
pip install anthropic

# Google Gemini için
pip install google-generativeai

# Cohere için (opsiyonel)
pip install cohere
```

### 3. API Key'lerini Alın

Her AI platformu için API key almanız gerekir:

#### OpenAI
1. [OpenAI Platform](https://platform.openai.com/) hesabı oluşturun
2. [API Keys](https://platform.openai.com/api-keys) sayfasından yeni key oluşturun
3. Ücretli plan gerekebilir (GPT-4 için)

#### Anthropic Claude
1. [Anthropic Console](https://console.anthropic.com/) hesabı oluşturun
2. [API Keys](https://console.anthropic.com/settings/keys) sayfasından key alın
3. Credits satın almanız gerekebilir

#### Google Gemini
1. [Google AI Studio](https://makersuite.google.com/app/apikey) sayfasına gidin
2. "Get API Key" butonuna tıklayın
3. Ücretsiz kullanım limiti vardır

#### Cohere (Opsiyonel)
1. [Cohere Dashboard](https://dashboard.cohere.ai/) hesabı oluşturun
2. [API Keys](https://dashboard.cohere.ai/api-keys) sayfasından key alın

## Kullanım

### Uygulamayı Başlatma

```bash
python multi_ai_question_tool.py
```

### İlk Kurulum

1. **Ayarları Açın**: "⚙️ API Key Ayarları" butonuna tıklayın

2. **API Key'leri Girin**:
   - Her AI platformu için:
     - "Etkin" checkbox'ını işaretleyin
     - API Key'inizi girin
     - Model adını kontrol edin (varsayılanlar genelde iyidir)

3. **Kaydedin**: "Kaydet" butonuna tıklayın

4. **Uygulamayı Yeniden Başlatın**: Ayarların etkili olması için uygulamayı kapatıp yeniden açın

### Soru Sorma

1. **Soru Yazın**: Üst kısımdaki metin kutusuna sorunuzu yazın

2. **AI Seçin**: Kullanmak istediğiniz AI'ları işaretleyin
   - OpenAI GPT
   - Anthropic Claude
   - Google Gemini
   - Cohere (opsiyonel)

3. **Gönder**: "Soruyu Gönder" butonuna tıklayın

4. **Bekleyin**: Tüm AI'ların cevap vermesini bekleyin
   - İlerleme durum çubuğunda gösterilir
   - Her AI'ın durumu alt kısımda görünür

5. **Sonuçları İnceleyin**: Cevaplar alt alta listelenir:
   ```
   ================================================================================
   SORU: [Sorunuz]
   ================================================================================

   ────────────────────────────────────────────────────────────────────────────────
   🤖 OpenAI (gpt-4)
   ────────────────────────────────────────────────────────────────────────────────
   [OpenAI'ın cevabı]

   ────────────────────────────────────────────────────────────────────────────────
   🤖 Anthropic Claude (claude-3-5-sonnet-20241022)
   ────────────────────────────────────────────────────────────────────────────────
   [Claude'un cevabı]

   ... (diğer AI'lar)
   ```

### Cevapları Kaydetme

1. "Cevapları Kaydet" butonuna tıklayın
2. Dosya adı ve konum seçin
3. Cevaplar `.txt` formatında kaydedilir

### Temizleme

"Temizle" butonuna tıklayarak hem soruyu hem de cevapları temizleyebilirsiniz.

## Konfigürasyon Dosyası

Ayarlar `config_ai.json` dosyasında saklanır:

```json
{
    "openai": {
        "enabled": true,
        "api_key": "sk-...",
        "model": "gpt-4"
    },
    "anthropic": {
        "enabled": true,
        "api_key": "sk-ant-...",
        "model": "claude-3-5-sonnet-20241022"
    },
    "google": {
        "enabled": true,
        "api_key": "AIza...",
        "model": "gemini-pro"
    },
    "cohere": {
        "enabled": false,
        "api_key": "",
        "model": "command"
    }
}
```

⚠️ **GÜVENLİK UYARISI**: Bu dosyayı paylaşmayın! API key'leriniz gizli kalmalıdır.

## Model Seçenekleri

### OpenAI Modelleri
- `gpt-4` - En güçlü, en pahalı
- `gpt-4-turbo-preview` - GPT-4 daha hızlı
- `gpt-3.5-turbo` - Daha hızlı, daha ucuz

### Anthropic Modelleri
- `claude-3-5-sonnet-20241022` - En güncel (önerilen)
- `claude-3-opus-20240229` - En güçlü
- `claude-3-sonnet-20240229` - Dengeli
- `claude-3-haiku-20240307` - Hızlı ve ucuz

### Google Modelleri
- `gemini-pro` - Genel amaçlı (önerilen)
- `gemini-pro-vision` - Görüntü analizi için

### Cohere Modelleri
- `command` - Genel amaçlı
- `command-light` - Daha hızlı

## Dosya Yapısı

```
project/
├── multi_ai_question_tool.py   # Ana GUI uygulaması
├── ai_providers.py             # AI provider entegrasyonları
├── config_ai.json              # API key ve ayarlar
├── requirements_ai.txt         # Python bağımlılıkları
├── README_AI_TOOL.md           # Bu dosya
└── logs/                       # Log dosyaları
    └── multi_ai_tool_*.log
```

## Özellikler ve İpuçları

### Paralel İşleme
- Tüm AI'lara aynı anda istek gönderilir
- Bu sayede bekleme süresi minimize edilir
- En yavaş AI cevap verene kadar beklersiniz

### Hata Yönetimi
- API key hataları otomatik algılanır
- Network hataları yakalanır ve gösterilir
- Her AI'ın hatası ayrı gösterilir, diğerlerini etkilemez

### Maliyet Kontrolü
- Sadece kullanmak istediğiniz AI'ları seçin
- Bazı modeller ücretsiz kullanım limiti sunar:
  - Google Gemini: Dakikada 60 istek (ücretsiz)
  - OpenAI: Pay-as-you-go (GPT-4: ~$0.03/1K token)
  - Anthropic: Pay-as-you-go (Claude-3: ~$0.003-0.015/1K token)

### Kullanım Senaryoları

1. **Kod İncelemesi**: Kodunuzu farklı AI'lara gösterin, her birinin önerisini alın
2. **Araştırma**: Karmaşık konular hakkında farklı perspektifler edinin
3. **Yaratıcı Yazım**: Farklı yazım stilleri ve öneriler alın
4. **Teknik Sorular**: Çeşitli kaynaklardan teknik cevaplar karşılaştırın
5. **Çeviri**: Farklı AI'ların çeviri kalitesini karşılaştırın

## Sorun Giderme

### "Provider kullanılamıyor" hatası
- API key'in doğru girildiğinden emin olun
- İlgili Python paketinin yüklü olduğunu kontrol edin
- Uygulamayı yeniden başlatın

### "API hatası" mesajı
- API key'inizin geçerli olduğundan emin olun
- Hesabınızda yeterli kredi olduğunu kontrol edin
- İnternet bağlantınızı kontrol edin
- API limitlerinizi aşmamış olduğunuzu kontrol edin

### Yavaş yanıt
- Normal: AI'lar cevap vermesi 5-30 saniye sürebilir
- GPT-4 ve Claude-3-Opus daha yavaş olabilir
- Daha hızlı modeller kullanmayı deneyin (GPT-3.5, Claude-Haiku)

### Python paketi bulunamadı
```bash
# Tüm paketleri yükleyin
pip install -r requirements_ai.txt

# Veya tekrar deneyin
pip install --upgrade openai anthropic google-generativeai
```

## Güvenlik

⚠️ **ÖNEMLİ GÜVENLİK KURALLARI**

1. **API Key'leri Koruyun**:
   - `config_ai.json` dosyasını asla paylaşmayın
   - Git'e commit etmeyin (`.gitignore`'a eklenmiştir)
   - Başkalarıyla paylaşmayın

2. **Hassas Bilgiler**:
   - Kişisel bilgileri AI'lara göndermekten kaçının
   - Şirket sırlarını paylaşmayın
   - Gizli verileri sormayın

3. **Rate Limiting**:
   - Her platformun limit kurallarına uyun
   - Çok fazla istek göndermekten kaçının

## Lisans

Bu proje özel bir proje olup, tüm hakları saklıdır.

## Sürüm Geçmişi

### v1.0.0 (2024-11-20)
- İlk sürüm
- OpenAI, Anthropic, Google Gemini, Cohere desteği
- Paralel soru gönderme
- GUI tabanlı API key yönetimi
- Sonuç kaydetme özelliği

## Destek ve Katkı

Sorularınız veya önerileriniz için issue açabilirsiniz.

## Teşekkürler

Bu uygulama şu teknolojileri kullanmaktadır:
- PyQt6 - GUI framework
- OpenAI API - GPT modelleri
- Anthropic API - Claude modelleri
- Google Generative AI - Gemini modelleri
- Cohere API - Command modelleri
