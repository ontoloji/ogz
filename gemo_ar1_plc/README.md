# GEMO AR1 - Kapak Açma/Kapama Test Cihazı

## 📖 Proje Tanımı

Bu proje, GEMO AR1 Akıllı Röle (Smart Relay) kullanarak otomatik kapak açma-kapama test sistemi yazılımıdır. Sistem, toggle (tek tuş) mantığıyla çalışan kapı motorlarını test etmek üzere tasarlanmıştır.

### Özellikler

- ✅ Otomatik açma-kapama döngüsü (20 saniye)
- ✅ Güvenlik sensörü entegrasyonu (sıkışma koruması)
- ✅ Açma sayacı (test döngüsü takibi)
- ✅ Manuel kontrol tuşları (Start/Stop/Reset)
- ✅ Tek pulse tetikleme sistemi (300ms)
- ✅ Otomatik döngü tekrarı

---

## 🔧 Donanım Gereksinimleri

### PLC Donanımı
- **Model:** GEMO AR1 Smart Relay
- **Giriş Sayısı:** Minimum 4 dijital giriş (F1, F2, F3, I3)
- **Çıkış Sayısı:** Minimum 1 dijital çıkış (DQ1)
- **Program Belleği:** Yeterli (16 network)

### Motor Sürücü
- **Tip:** Toggle (Tek Tuş) mantığı
- **Çalışma:** Bir darbe → Aç, İkinci darbe → Kapat
- **Pulse Süresi:** 300ms (0.3 saniye)
- **Tetikleme:** DQ1 çıkışı

### Sensör
- **I3 Sensörü:** Sıkışma/Safety sensörü
- **Tip:** Normally Open (NO) veya Normally Closed (NC)
- **Aktif Olma:** Sadece kapak kapanma fazında

---

## 🔌 Bağlantı Şeması

```
┌─────────────────────────────────────┐
│         GEMO AR1 PLC                │
├─────────────────────────────────────┤
│                                     │
│  F1 (Start)    ───┐                │
│  F2 (Stop)     ───┤  Girişler      │
│  F3 (Reset)    ───┤                │
│  I3 (Safety)   ───┘                │
│                                     │
│  DQ1 (Motor)   ────────────┐       │
│                             │       │
└─────────────────────────────┼───────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Motor Sürücü    │
                    │  (Toggle Mode)   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Kapak Motoru   │
                    └──────────────────┘
```

### Pin Bağlantıları

| Pin | İşlev | Bağlantı | Tip |
|-----|-------|----------|-----|
| **F1** | Start Tuşu | Push Button (NO) | Dijital Giriş |
| **F2** | Stop Tuşu | Push Button (NO) | Dijital Giriş |
| **F3** | Reset Tuşu | Push Button (NO) | Dijital Giriş |
| **I3** | Safety Sensörü | Fotosel/Switch | Dijital Giriş |
| **DQ1** | Motor Tetikleme | Motor Sürücü | Dijital Çıkış |
| **COM** | Ortak | GND/0V | - |

---

## 💾 Kurulum

### 1. Dosyaları İndirme
```bash
git clone <repository>
cd gemo_ar1_plc
```

### 2. Dosya Yapısı
```
gemo_ar1_plc/
├── README.md                      # Bu dosya
├── door_control_ladder.txt        # Ladder Logic programı
└── timer_counter_config.md        # Timer/Counter ayar tablosu
```

### 3. GEMO Lader Editör Kurulumu
1. GEMO Lader Editör yazılımını bilgisayara kurun
2. USB kablosu ile GEMO AR1'i bağlayın
3. Editörü açın ve PLC ile bağlantı kurun

### 4. Program Yükleme

#### Yöntem 1: Manuel Ladder Girişi
1. `door_control_ladder.txt` dosyasını açın
2. Her Network'ü sırasıyla Lader Editör'e girin
3. Timer/Counter ayarlarını `timer_counter_config.md` dosyasından yapın

#### Yöntem 2: Text Import (Varsa)
1. Lader Editör → Import → Text File
2. `door_control_ladder.txt` seçin
3. Timer/Counter ayarlarını kontrol edin

### 5. Timer/Counter Ayarları

**Timer Ayarları:**
| Timer | Mod | Time Base | Value | Toplam Süre |
|-------|-----|-----------|-------|-------------|
| T0 | TON | 100ms | 3 | 300ms |
| T1 | TON | 1s | 10 | 10s |
| T2 | TON | 1s | 10 | 10s |

**Counter Ayarları:**
| Counter | Mod | Preset | Reset |
|---------|-----|--------|-------|
| C0 | CTU | 9999 | F3 |

Detaylı ayar bilgisi için: `timer_counter_config.md`

### 6. Donanım Bağlantısı
1. Tüm girişleri (F1, F2, F3, I3) bağlayın
2. DQ1 çıkışını motor sürücüye bağlayın
3. Güç kaynağını bağlayın (24VDC)
4. Bağlantıları test edin

---

## 🎮 Kullanım

### Sistem Başlatma

1. **Hazırlık:**
   - PLC'ye güç verildiğinden emin olun
   - Tüm bağlantıları kontrol edin
   - Kapağın güvenli pozisyonda olduğunu doğrulayın

2. **Sayaç Sıfırlama (Opsiyonel):**
   - **F3** tuşuna basın → Sayaç sıfırlanır (C0 = 0)

3. **Test Başlatma:**
   - **F1** tuşuna basın → Sistem çalışmaya başlar
   - Sistem otomatik döngüye girer

4. **Test Durdurma:**
   - **F2** tuşuna basın → Sistem durur
   - Tüm fazlar ve timerlar sıfırlanır

### Otomatik Döngü

Sistem aşağıdaki sırayla çalışır:

```
┌──────────────────────────────────────────────┐
│  F1 Basıldı → Sistem Başladı                 │
└──────────────────┬───────────────────────────┘
                   ▼
         ┌─────────────────────┐
         │   FAZ 1: AÇMA       │ ← Safety'den dönüş
         │   Süre: 10 saniye   │
         └──────────┬──────────┘
                    │
                    │ ▶ Başlangıç: DQ1 = 300ms pulse
                    │ ▶ Kapak açılır
                    │ ▶ Sayaç +1 (C0++)
                    │ ▶ 10 saniye bekleme
                    ▼
         ┌─────────────────────┐
         │   FAZ 2: KAPAMA     │
         │   Süre: 10 saniye   │
         └──────────┬──────────┘
                    │
                    │ ▶ Başlangıç: DQ1 = 300ms pulse
                    │ ▶ Kapak kapanır
                    │ ▶ I3 sensörü izlenir
                    │ ▶ 10 saniye bekleme
                    │
                    ├─ I3 Aktif? ─┐
                    │ (Sıkışma)   │
                    ▼ Hayır       ▼ Evet
         ┌──────────────┐   ┌────────────────┐
         │ Döngü Tekrar │   │ Safety Tetikle │
         │ (Faz 1'e dön)│   │ ▶ DQ1 pulse    │
         └──────────────┘   │ ▶ Kapak geri aç│
                            │ ▶ Faz 1'e dön  │
                            └────────────────┘
```

### Güvenlik (Safety) Sistemi

**I3 Sensörü Aktif Olduğunda:**

1. Faz 2 (Kapama) anında iptal edilir
2. DQ1'den anında pulse gönderilir (Kapak geri açılır)
3. Timer sıfırlanır
4. Sistem Faz 1'e (Açma) geri döner
5. Normal döngü devam eder

**Örnek Senaryo:**
```
Kapak kapanıyor → Nesne algılandı (I3=1) →
Kapanma durdur → Kapağı geri aç →
Açma fazına dön → Normal döngü devam
```

---

## 📊 Çalışma Zamanlaması

### Normal Döngü (20 saniye)

```
Zaman     │ Durum          │ DQ1  │ Faz   │ Açıklama
──────────┼────────────────┼──────┼───────┼──────────────────────
0.0s      │ Başlangıç      │ 1    │ Faz 1 │ DQ1 pulse başladı
0.3s      │ Pulse bitti    │ 0    │ Faz 1 │ Kapak açılıyor
0.3-10s   │ Bekleme        │ 0    │ Faz 1 │ Açık pozisyon
──────────┼────────────────┼──────┼───────┼──────────────────────
10.0s     │ Faz geçişi     │ 1    │ Faz 2 │ DQ1 pulse başladı
10.3s     │ Pulse bitti    │ 0    │ Faz 2 │ Kapak kapanıyor
10.3-20s  │ Bekleme        │ 0    │ Faz 2 │ Kapalı pozisyon
──────────┼────────────────┼──────┼───────┼──────────────────────
20.0s     │ Döngü tekrar   │ 1    │ Faz 1 │ Yeni döngü başladı
```

### Safety Senaryosu

```
Zaman     │ Durum          │ I3   │ DQ1  │ Faz   │ Açıklama
──────────┼────────────────┼──────┼──────┼───────┼───────────────
10.0s     │ Kapanma başladı│ 0    │ 1    │ Faz 2 │ DQ1 pulse
10.3s     │ Kapanıyor      │ 0    │ 0    │ Faz 2 │ Normal
15.5s     │ Sıkışma!       │ 1    │ 0    │ Faz 2 │ I3 aktif
15.5s     │ Safety aktif   │ 1    │ 1    │ -     │ Acil pulse
15.8s     │ Geri açılıyor  │ 1    │ 0    │ Faz 1 │ Faz 1'e döndü
15.8-25.8s│ Açık bekleme   │ 0    │ 0    │ Faz 1 │ Normal devam
```

---

## 🔍 Test ve Doğrulama

### Ön Test (PLC Olmadan)

1. **Giriş Testi:**
   - F1, F2, F3 tuşlarını multimetre ile test edin
   - I3 sensörünü test edin (ON/OFF)

2. **Çıkış Testi:**
   - DQ1'i LED veya multimetre ile test edin

### Fonksiyonel Test

#### Test 1: Temel Döngü
```
1. F3 bas → Sayacı sıfırla
2. F1 bas → Sistem başlat
3. Gözlemle:
   ✓ DQ1 300ms aktif
   ✓ 10s Faz 1 bekleme
   ✓ DQ1 300ms aktif
   ✓ 10s Faz 2 bekleme
   ✓ Döngü tekrar
4. F2 bas → Sistem dur
```

#### Test 2: Sayaç
```
1. F3 bas → C0 = 0
2. F1 bas → Başlat
3. 5 döngü bekle (100s)
4. Kontrol: C0 = 5 olmalı
5. F3 bas → C0 = 0 olmalı
```

#### Test 3: Safety
```
1. F1 bas → Başlat
2. Faz 2'de (10s sonra) I3'ü manuel aktif et
3. Gözlemle:
   ✓ DQ1 hemen pulse
   ✓ Faz 1'e geçiş
   ✓ Normal döngü devam
```

#### Test 4: Stop/Start
```
1. F1 bas → Başlat
2. 5s bekle (Faz 1 ortasında)
3. F2 bas → Dur
4. Kontrol: Tüm çıkışlar 0
5. F1 bas → Tekrar başlat
6. Kontrol: Normal döngü
```

---

## 📈 Performans Metrikleri

### Zamanlama Toleransları

| Parametre | Hedef | Tolerans | Ölçüm |
|-----------|-------|----------|-------|
| Pulse Süresi | 300ms | ±10ms | DQ1 çıkışı |
| Faz 1 Süresi | 10s | ±100ms | T1 timer |
| Faz 2 Süresi | 10s | ±100ms | T2 timer |
| Toplam Döngü | 20s | ±200ms | Tam döngü |
| Safety Tepki | <50ms | - | I3 → DQ1 |

### Beklenen Sonuçlar

- **1 Saat Test:** ~180 döngü (C0 = 180)
- **8 Saat Test:** ~1440 döngü (C0 = 1440)
- **24 Saat Test:** ~4320 döngü (C0 = 4320)

---

## 🐛 Sorun Giderme

### PLC Programlanmıyor
- [ ] USB kablosu bağlı mı?
- [ ] GEMO Lader Editör açık mı?
- [ ] Doğru COM port seçili mi?
- [ ] PLC'ye güç var mı?

### F1 Basınca Sistem Başlamıyor
- [ ] F1 bağlantısı kontrol edin
- [ ] M0 marker'ı gözlemleyin
- [ ] Network 1 kodunu kontrol edin

### DQ1 Sürekli Açık Kalıyor
- [ ] T0 timer ayarını kontrol edin (300ms)
- [ ] M4 marker'ını gözlemleyin
- [ ] Network 12 kodunu kontrol edin

### Sayaç Artmıyor
- [ ] C0 preset değeri doldu mu? (9999)
- [ ] M3 marker'ını gözlemleyin
- [ ] Network 14 kodunu kontrol edin

### Safety Çalışmıyor
- [ ] I3 sensör bağlantısı
- [ ] Faz 2 aktif mi? (M2 = 1)
- [ ] Network 9-10-11 kodunu kontrol edin

### Döngü Tekrarlamıyor
- [ ] T2 timer ayarını kontrol edin
- [ ] Network 8 kodunu kontrol edin
- [ ] F2 basılı kalmış olabilir

---

## ⚙️ Gelişmiş Ayarlar

### Pulse Süresini Değiştirme

Farklı motor sürücüler için pulse süresini değiştirmek:

```
T0 Timer:
- 200ms için: Time Base=100ms, Value=2
- 300ms için: Time Base=100ms, Value=3 (Varsayılan)
- 500ms için: Time Base=100ms, Value=5
- 1s için:    Time Base=100ms, Value=10
```

### Faz Sürelerini Değiştirme

Test gereksinimlerine göre faz sürelerini ayarlama:

```
T1 ve T2:
- 5s için:  Time Base=1s, Value=5
- 10s için: Time Base=1s, Value=10 (Varsayılan)
- 15s için: Time Base=1s, Value=15
- 30s için: Time Base=1s, Value=30
- 60s için: Time Base=1s, Value=60
```

### Sayaç Limitini Değiştirme

```
C0 Counter:
- 1000 döngü için: Preset=1000
- 5000 döngü için: Preset=5000
- 9999 döngü için: Preset=9999 (Varsayılan)
```

---

## 📁 Dosya Açıklamaları

### `door_control_ladder.txt`
Text-based Ladder Logic programı. 16 Network içerir:
- Network 1-16: Tam sistem kontrolü
- Yorumlu ve açıklamalı

### `timer_counter_config.md`
Timer ve Counter ayar rehberi:
- Detaylı ayar tabloları
- Mod açıklamaları
- Test prosedürleri

### `README.md`
Ana dokümantasyon (bu dosya):
- Kurulum ve kullanım
- Çalışma prensibi
- Sorun giderme

---

## 🔒 Güvenlik Uyarıları

⚠️ **ÖNEMLI GÜVENLİK BİLGİLERİ**

1. **Acil Durdurma:** F2 tuşuna her zaman erişilebilir olmalı
2. **Güç Kesintisi:** Beklenmedik güç kesintilerinde sistem durur
3. **Mekanik Güvenlik:** Kapak hareketli parçalarına dikkat
4. **Sensör Kontrolü:** I3 sensörünü düzenli test edin
5. **Yük Sınırı:** Motor kapasitesini aşmayın
6. **Bakım:** Düzenli bakım programı uygulayın

---

## 📞 Teknik Destek

### Dokümantasyon
- GEMO AR1 Kullanım Kılavuzu
- Ladder Logic Programlama Rehberi
- Timer/Counter Konfigürasyon Dökümanı

### İletişim
- Email: support@example.com
- Telefon: +90 XXX XXX XX XX

---

## 📝 Revizyon Geçmişi

| Versiyon | Tarih | Değişiklik | Yazar |
|----------|-------|------------|-------|
| v1.0 | 2024-11-19 | İlk sürüm | Otomasyon Müh. |

---

## 📄 Lisans

Bu proje özel bir proje olup, tüm hakları saklıdır.

---

## 🎯 Hızlı Başlangıç Özeti

1. Donanımı bağlayın (F1, F2, F3, I3, DQ1)
2. Programı GEMO Lader Editör ile yükleyin
3. Timer/Counter ayarlarını yapın (T0=300ms, T1=10s, T2=10s)
4. F3 ile sayacı sıfırlayın
5. F1 ile başlatın
6. Test edin!

**İyi testler! 🚀**
