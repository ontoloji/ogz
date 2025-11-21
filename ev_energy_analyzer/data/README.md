# Veri Klasörü

Bu klasör test verilerinizi ve örnek verileri içerir.

## Örnek Veri Oluşturma

Windows'ta Python ortamında şu komutu çalıştırın:

```bash
python create_sample_data.py
```

Bu komut `ornek_test_verisi.xlsx` dosyasını bu klasörde oluşturacaktır.

## Excel Dosya Formatı

Test verileriniz şu formatta olmalıdır:

| Zaman | Hız | Akım | Voltaj | Sıcaklık |
|-------|-----|------|--------|----------|
| 0 | 0 | 0 | 400 | 25.0 |
| 1 | 0 | 0 | 400 | 25.1 |
| 2 | 5.2 | 45 | 398 | 25.2 |
| ... | ... | ... | ... | ... |

- **Zaman**: Saniye cinsinden
- **Hız**: km/h
- **Akım**: Amper (A)
- **Voltaj**: Volt (V)
- **Sıcaklık**: Celsius (°C) - opsiyonel

## Kendi Verilerinizi Kullanma

1. Excel dosyanızı bu klasöre kopyalayın
2. Uygulamada "Excel Dosyası Seç" ile dosyanızı seçin
3. Analiz başlatın
