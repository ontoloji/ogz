# CARLA Senaryo Aracı - Hızlı Başlangıç

## 5 Dakikada Başlayın

### 1. Önkoşul: CARLA Kurulumu

```bash
# CARLA Python API'yi PYTHONPATH'e ekleyin
export PYTHONPATH=$PYTHONPATH:~/CARLA/PythonAPI/carla
export PYTHONPATH=$PYTHONPATH:~/CARLA/PythonAPI/carla/dist/carla-*-py3.7-linux-x86_64.egg

# Test edin
python3 -c "import carla; print('CARLA API OK')"
```

### 2. GUI ile Senaryo Oluşturma

```bash
cd carla_scenario_tool
python3 scenario_generator_gui.py
```

**İlk Senaryonuzu Oluşturun:**
1. Senaryo adı: "İlk Testim"
2. Harita: Town01 (varsayılan)
3. "+ Araç Ekle" butonuna tıklayın
4. "Kaydet" butonuna tıklayın → `scenarios/ilk_testim.json`

### 3. Senaryoyu CARLA'da Çalıştırma

```bash
# Terminal 1: CARLA başlat
cd ~/CARLA
./CarlaUE4.sh

# Terminal 2: Senaryoyu çalıştır
cd carla_scenario_tool
python3 carla_runner.py scenarios/ilk_testim.json
```

### 4. Örnek Senaryoları Deneyin

```bash
# Basit düz yol
python3 carla_runner.py scenarios/example_basic.json

# Kavşak senaryosu
python3 carla_runner.py scenarios/example_intersection.json

# Yaya geçidi
python3 carla_runner.py scenarios/example_pedestrian.json
```

## Temel Kavramlar

### Koordinat Sistemi
- **X**: İleri(+) / Geri(-)
- **Y**: Sağ(+) / Sol(-)
- **Z**: Yukarı(+) / Aşağı(-)
- **Yaw**: 0°=Kuzey, 90°=Doğu, 180°=Güney, 270°=Batı

### Waypoint Nedir?
Aktörün hareket rotasındaki ara noktalar. Her waypoint için:
- Konum (X, Y, Z)
- Hız (km/h)
- Bekleme süresi (saniye)

### Ego Vehicle vs NPC
- **Ego Vehicle**: Test ettiğiniz otonom araç
- **NPC**: Senaryodaki diğer araçlar ve yayalar

## Örnek: Basit Aşma Senaryosu

```
Ego Vehicle (hızlı, 50 km/h)
    ↓
    |  Yavaş araç (30 km/h)
    |      ↓
====|======|=========== Düz Yol
```

**Adımlar:**
1. GUI'de yeni senaryo
2. Ego vehicle: X=100, Y=50, Z=0.5, Hız=50 km/h
3. "+ Araç Ekle": X=150, Y=50, Z=0.5, Hız=30 km/h
4. Her ikisine de waypoint ekleyin (X değerini artırarak)
5. Kaydet ve çalıştır

## İleri Seviye

### Karmaşık Hava Koşulları

GUI'de "Hava Durumu" → "custom" seçin:
- **Sis**: 80% (düşük görüş)
- **Yağmur**: 60% (ıslak yol)
- **Saat**: 20:00 (gece)

### Çoklu NPC

Tek senaryoda:
- 5 araç (farklı hızlar, farklı şeritler)
- 3 yaya (yaya geçidinde)
- 2 durmuş araç (yol kenarında)

## Sorun Giderme

### CARLA bağlanamıyor
```bash
# CARLA çalışıyor mu?
ps aux | grep CarlaUE4

# Yoksa başlat
cd ~/CARLA && ./CarlaUE4.sh
```

### Tkinter hatası
```bash
sudo apt-get install python3-tk
```

### Spawn hatası
- Z koordinatını 0.5-1.0 yapın
- X, Y'yi değiştirin (çakışma olabilir)

## Daha Fazla Bilgi

Detaylı kullanım için `README_CARLA.md` dosyasına bakın.

## Yararlı Komutlar

```bash
# Tüm senaryoları listele
ls -lh scenarios/*.json

# Senaryo özetini göster
python3 -c "from scenario_io import ScenarioIO; \
print(ScenarioIO.export_scenario_summary(ScenarioIO.load_scenario('scenarios/example_basic.json')))"

# Örnek senaryoları yeniden oluştur
python3 scenario_io.py
```

## İletişim

Sorularınız için README_CARLA.md'ye bakın veya CARLA topluluğuna katılın:
- https://carla.readthedocs.io/
- https://discord.gg/8kqACuC
