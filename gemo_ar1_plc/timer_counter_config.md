# GEMO AR1 - Timer ve Counter Yapılandırma Tablosu

## 📋 Timer Ayarları

| Timer | Adı | Mod | Time Base | Value | Toplam Süre | Açıklama |
|-------|-----|-----|-----------|-------|-------------|----------|
| **T0** | Pulse Timer | TON | 100ms | 3 | **300ms** | Motor tetikleme pulse süresi (0.3 saniye) |
| **T1** | Faz 1 Timer | TON | 1s | 10 | **10 saniye** | Açma fazı bekleme süresi |
| **T2** | Faz 2 Timer | TON | 1s | 10 | **10 saniye** | Kapama fazı bekleme süresi |

---

## 📊 Counter Ayarları

| Counter | Adı | Mod | Preset Value | Reset Koşulu | Açıklama |
|---------|-----|-----|--------------|--------------|----------|
| **C0** | Açma Sayacı | CTU | 9999 | F3 tuşu | Toplam açma sayısını tutar |

**Not:** Counter preset değeri 9999 olarak ayarlanmıştır. Bu değere ulaşıldığında sayaç durur. Gerekirse bu değer değiştirilebilir.

---

## ⚙️ Timer Mod Açıklamaları

### TON (On-Delay Timer)
- **Çalışma:** Giriş aktif olduğunda sayar
- **Çıkış:** Süre dolduğunda aktif olur
- **Kullanım:** T0, T1, T2

**Çalışma Diyagramı:**
```
Giriş:    ────┐           ┌────
              └───────────┘
Timer:    ────────┐       ┌────
                  └───────┘
              <-Değer->
```

### CTU (Count Up Counter)
- **Çalışma:** Her yükselen kenarda +1
- **Reset:** Reset girişi aktif olduğunda 0
- **Kullanım:** C0

---

## 🔧 GEMO Lader Editör'de Ayarlama

### Timer Ayarlama Adımları:

1. **Timer Seçimi:** T0, T1 veya T2
2. **Mod Seçimi:** TON
3. **Time Base Ayarı:**
   - T0 için: **100ms**
   - T1 için: **1s**
   - T2 için: **1s**
4. **Value Ayarı:**
   - T0 için: **3** (3 × 100ms = 300ms)
   - T1 için: **10** (10 × 1s = 10s)
   - T2 için: **10** (10 × 1s = 10s)

---

### Counter Ayarlama Adımları:

1. **Counter Seçimi:** C0
2. **Mod Seçimi:** CTU (Count Up)
3. **Preset Value:** **9999**
4. **Reset Input:** F3

---

## 📝 Örnek Konfigürasyon Ekran Görüntüsü

```
┌─────────────────────────────────────┐
│ TIMER CONFIGURATION - T0            │
├─────────────────────────────────────┤
│ Timer Number:    T0                 │
│ Timer Mode:      TON (On-Delay)     │
│ Time Base:       100ms              │
│ Preset Value:    3                  │
│ Current Value:   0                  │
│ Total Time:      300ms              │
└─────────────────────────────────────┘
```

```
┌─────────────────────────────────────┐
│ TIMER CONFIGURATION - T1            │
├─────────────────────────────────────┤
│ Timer Number:    T1                 │
│ Timer Mode:      TON (On-Delay)     │
│ Time Base:       1s                 │
│ Preset Value:    10                 │
│ Current Value:   0                  │
│ Total Time:      10s                │
└─────────────────────────────────────┘
```

```
┌─────────────────────────────────────┐
│ TIMER CONFIGURATION - T2            │
├─────────────────────────────────────┤
│ Timer Number:    T2                 │
│ Timer Mode:      TON (On-Delay)     │
│ Time Base:       1s                 │
│ Preset Value:    10                 │
│ Current Value:   0                  │
│ Total Time:      10s                │
└─────────────────────────────────────┘
```

```
┌─────────────────────────────────────┐
│ COUNTER CONFIGURATION - C0          │
├─────────────────────────────────────┤
│ Counter Number:  C0                 │
│ Counter Mode:    CTU (Count Up)     │
│ Preset Value:    9999               │
│ Current Value:   0                  │
│ Count Input:     M3 (Rising Edge)   │
│ Reset Input:     F3                 │
└─────────────────────────────────────┘
```

---

## 🎯 Özet Tablo (Hızlı Referans)

| Eleman | Mod | Time Base | Value | Toplam |
|--------|-----|-----------|-------|---------|
| **T0** | TON | 100ms | 3 | **300ms** |
| **T1** | TON | 1s | 10 | **10s** |
| **T2** | TON | 1s | 10 | **10s** |
| **C0** | CTU | - | 9999 | - |

---

## ⚠️ Önemli Notlar

1. **Time Base Seçimi:** Doğru time base çok önemlidir. Yanlış seçim sürelerin hatalı olmasına neden olur.

2. **Value Hesaplama:**
   ```
   Toplam Süre = Time Base × Value
   Örnek: T0 = 100ms × 3 = 300ms
   ```

3. **Timer Reset:** Program içinde F2 (Stop) tuşu T1 ve T2'yi resetler. Manuel reset gerekli değildir.

4. **Counter Overflow:** C0 sayacı 9999'a ulaştığında durar. Daha fazla sayım için preset değerini artırın.

5. **Safety Timer:** Safety (M5) aktif olduğunda T2 otomatik resetlenir (Network 9).

---

## 🔍 Test ve Doğrulama

### Timer Test Prosedürü:

1. **T0 Test (300ms):**
   - F1 ile sistemi başlat
   - DQ1 çıkışının 300ms süreyle aktif olduğunu ölçün
   - Osiloskopta veya lojik analizörde kontrol edin

2. **T1 Test (10s):**
   - Sistem başladıktan sonra kronometre başlat
   - T1 bitene kadar (10s) bekle
   - Faz 2'ye geçişi gözlemle

3. **T2 Test (10s):**
   - Faz 2 başladığında kronometre başlat
   - T2 bitene kadar (10s) bekle
   - Döngünün başa dönüşünü gözlemle

### Counter Test Prosedürü:

1. **C0 Test:**
   - F3 ile sayacı sıfırla (C0 = 0)
   - F1 ile sistemi başlat
   - Her döngüde C0'ın +1 arttığını kontrol et
   - 5 döngü sonrası C0 = 5 olmalı

---

## 📞 Destek

Timer/Counter ayarlarıyla ilgili sorunlar için GEMO AR1 kullanım kılavuzuna bakınız.

---

**Revizyon:** v1.0
**Tarih:** 2024-11-19
**Hazırlayan:** Otomasyon Mühendisliği Birimi
