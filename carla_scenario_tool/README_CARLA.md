# CARLA Otonom Araç Test Senaryosu Oluşturma Aracı

CARLA simülatöründe otonom araç algoritmasını test etmek için senaryo oluşturma, kaydetme ve çalıştırma aracı.

## Özellikler

### 🎯 Ana Özellikler

- **Grafik Arayüz (GUI)**: Tkinter tabanlı kullanıcı dostu arayüz
- **Senaryo Yönetimi**: JSON formatında kaydetme/yükleme
- **Ego Vehicle Kontrolü**: Test edilen otonom aracın spawn konumu, hızı ve rotası
- **Çoklu NPC Desteği**: Sınırsız sayıda araç ve yaya ekleme
- **Waypoint Sistemi**: Her aktör için detaylı hareket rotası
- **Çevre Kontrolü**:
  - 14 farklı hava durumu preset'i
  - Özel hava ayarları (bulut, yağmur, sis, rüzgar)
  - Gündüz/gece modu
- **CARLA Entegrasyonu**: Senaryoları doğrudan CARLA'da çalıştırma

### 🚗 Test Senaryoları

- Düz yol takip testleri
- Kavşak geçiş senaryoları
- Yaya geçidi testleri
- Şerit değiştirme testleri
- Acil fren testleri
- Karmaşık trafik senaryoları

## Gereksinimler

### Sistem Gereksinimleri

- **İşletim Sistemi**: Ubuntu 22.04 (veya 20.04, 18.04)
- **Python**: 3.7 veya üzeri
- **CARLA Simulator**: 0.9.x sürümü
- **RAM**: Minimum 8GB (16GB önerilir)
- **GPU**: NVIDIA GPU önerilir (CARLA için)

### Yazılım Gereksinimleri

```bash
# Python 3.7+
python3 --version

# Tkinter (genelde Python ile gelir)
sudo apt-get install python3-tk

# CARLA Simulator (indirme)
# https://carla.org/
```

## Kurulum

### 1. CARLA Simulator Kurulumu

```bash
# CARLA'yı indirin (örnek: 0.9.13)
cd ~/Downloads
wget https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.13.tar.gz

# Çıkartın
mkdir -p ~/CARLA
cd ~/CARLA
tar -xvzf ~/Downloads/CARLA_0.9.13.tar.gz

# Test edin
cd ~/CARLA
./CarlaUE4.sh
# CARLA açılırsa başarılı (kapatmak için Ctrl+C)
```

### 2. CARLA Python API Kurulumu

```bash
# CARLA Python API'yi PYTHONPATH'e ekleyin
echo 'export PYTHONPATH=$PYTHONPATH:~/CARLA/PythonAPI/carla' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:~/CARLA/PythonAPI/carla/dist/carla-*-py3.7-linux-x86_64.egg' >> ~/.bashrc
source ~/.bashrc

# Test edin
python3 -c "import carla; print('CARLA API OK:', carla.__version__)"
```

### 3. Senaryo Oluşturma Aracını Kurma

```bash
# Projeyi klonlayın veya dizine gidin
cd /path/to/carla_scenario_tool

# Bağımlılıkları kurun (varsa)
pip3 install -r requirements.txt

# Executable yapın
chmod +x scenario_generator_gui.py
chmod +x carla_runner.py
```

## Kullanım

### 1. Senaryo Oluşturma (GUI)

```bash
# GUI'yi başlatın
python3 scenario_generator_gui.py
```

#### GUI Kullanım Adımları:

1. **Senaryo Bilgileri**:
   - Senaryo adı girin
   - Açıklama yazın
   - CARLA haritası seçin (Town01-07, Town10HD)
   - Senaryo süresini belirleyin

2. **Ego Vehicle (Test Aracı) Ayarları**:
   - Araç modelini seçin
   - Spawn konumunu ayarlayın (X, Y, Z koordinatları)
   - Spawn yönünü belirleyin (Yaw: 0-360°)
   - Hedef hızı ayarlayın
   - İsterseniz CARLA Autopilot'u aktif edin
   - "Waypoint Rotası Düzenle" ile hareket rotası ekleyin

3. **NPC Aktörler Ekleme**:
   - **Araç eklemek için**: "+ Araç Ekle" butonuna tıklayın
   - **Yaya eklemek için**: "+ Yaya Ekle" butonuna tıklayın
   - Her aktör için:
     - Benzersiz ID verin
     - Model seçin
     - Spawn konumu ve yönü belirleyin
     - Davranış tipi seçin (normal, aggressive, cautious, stopped)
     - Waypoint rotası ekleyin

4. **Çevre Koşulları**:
   - Hava durumu preset'i seçin (clear_noon, hard_rain_noon, vb.)
   - Veya "custom" seçip özel ayarlar yapın:
     - Bulutluluk (0-100%)
     - Yağmur (0-100%)
     - Sis yoğunluğu (0-100%)
     - Rüzgar şiddeti (0-100%)
   - Saat ve dakika ayarlayın (gündüz/gece)

5. **Kaydetme**:
   - "Kaydet" veya "Farklı Kaydet" butonuna tıklayın
   - Senaryo `scenarios/` dizinine JSON olarak kaydedilir

### 2. Senaryoyu CARLA'da Çalıştırma

```bash
# Terminal 1: CARLA sunucusunu başlatın
cd ~/CARLA
./CarlaUE4.sh

# Terminal 2: Senaryoyu çalıştırın
cd /path/to/carla_scenario_tool
python3 carla_runner.py scenarios/my_scenario.json

# Farklı host/port için
python3 carla_runner.py scenarios/my_scenario.json --host 192.168.1.100 --port 2000
```

#### Çalıştırma Sırasında:

- CARLA penceresinde senaryoyu izleyebilirsiniz
- Kamera ego vehicle'ı takip eder
- Durdurmak için `Ctrl+C` basın
- Senaryo süresi dolduğunda otomatik durur

### 3. Örnek Senaryolar

Projeyle birlikte 3 örnek senaryo gelir:

```bash
# Örnek senaryoları oluşturmak için
python3 scenario_io.py

# Örnek senaryoları çalıştırın
python3 carla_runner.py scenarios/example_basic.json
python3 carla_runner.py scenarios/example_intersection.json
python3 carla_runner.py scenarios/example_pedestrian.json
```

#### Örnek 1: Basit Düz Yol
- Ego vehicle düz yolda gider
- Önünde yavaş giden bir araç var
- Aşma veya takip testi

#### Örnek 2: Kavşak Geçiş
- Ego vehicle kavşağa yaklaşır
- Sağdan bir araç geliyor
- Öncelik ve karar verme testi

#### Örnek 3: Yaya Geçidi
- Ego vehicle yaya geçidine yaklaşır
- 2 yaya karşıdan karşıya geçiyor
- Yaya algılama ve durma testi

## Dosya Yapısı

```
carla_scenario_tool/
├── scenario_config.py           # Senaryo veri yapıları ve modeller
├── scenario_io.py               # JSON kaydetme/yükleme
├── scenario_generator_gui.py    # Tkinter GUI arayüzü
├── carla_runner.py              # CARLA'da senaryo çalıştırıcı
├── requirements.txt             # Python bağımlılıkları
├── README_CARLA.md             # Bu dosya
└── scenarios/                   # Kaydedilmiş senaryolar
    ├── example_basic.json
    ├── example_intersection.json
    └── example_pedestrian.json
```

## Senaryo JSON Formatı

```json
{
  "name": "Test Senaryosu",
  "description": "Örnek senaryo açıklaması",
  "carla_map": "Town01",
  "duration": 60.0,
  "ego_vehicle": {
    "blueprint": "vehicle.tesla.model3",
    "spawn_point": {
      "location": {"x": 100.0, "y": 50.0, "z": 0.5},
      "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
    },
    "target_speed": 50.0,
    "route_waypoints": [
      {
        "location": {"x": 200.0, "y": 50.0, "z": 0.5},
        "speed": 50.0,
        "wait_time": 0.0
      }
    ],
    "enable_autopilot": false,
    "enable_sensors": true
  },
  "npc_actors": [
    {
      "actor_id": "npc_vehicle_01",
      "actor_type": "vehicle",
      "blueprint": "vehicle.audi.a2",
      "spawn_point": {
        "location": {"x": 150.0, "y": 50.0, "z": 0.5},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
      },
      "route_waypoints": [],
      "behavior": "normal",
      "auto_destroy": true
    }
  ],
  "weather": {
    "preset": "clear_noon"
  },
  "time": {
    "hour": 12,
    "minute": 0
  }
}
```

## Koordinat Sistemi

CARLA koordinat sistemi:
- **X**: İleri/geri (pozitif = ileri)
- **Y**: Sağ/sol (pozitif = sağ)
- **Z**: Yukarı/aşağı (pozitif = yukarı)
- **Yaw**: Yön (0° = kuzey, 90° = doğu, 180° = güney, 270° = batı)

### Koordinatları Bulma

```python
# CARLA'da spawn noktalarını görmek için
cd ~/CARLA/PythonAPI/examples
python3 spawn_npc.py --number-of-vehicles 0 --number-of-walkers 0
# Haritadaki spawn noktalarını konsola yazdırır
```

Veya CARLA penceresinde:
1. `F1` tuşuna basın (koordinatları gösterir)
2. Spectator modda gezinin
3. İstediğiniz konumun koordinatlarını okuyun

## Hava Durumu Preset'leri

| Preset | Açıklama |
|--------|----------|
| `clear_noon` | Açık hava, öğlen |
| `clear_sunset` | Açık hava, gün batımı |
| `cloudy_noon` | Bulutlu, öğlen |
| `cloudy_sunset` | Bulutlu, gün batımı |
| `wet_noon` | Islak zemin, öğlen |
| `wet_sunset` | Islak zemin, gün batımı |
| `wet_cloudy_noon` | Islak + bulutlu, öğlen |
| `wet_cloudy_sunset` | Islak + bulutlu, gün batımı |
| `soft_rain_noon` | Hafif yağmur, öğlen |
| `soft_rain_sunset` | Hafif yağmur, gün batımı |
| `mid_rain_noon` | Orta yağmur, öğlen |
| `mid_rain_sunset` | Orta yağmur, gün batımı |
| `hard_rain_noon` | Şiddetli yağmur, öğlen |
| `hard_rain_sunset` | Şiddetli yağmur, gün batımı |
| `custom` | Özel ayarlar |

## Araç ve Yaya Modelleri

### Popüler Araç Modelleri

- `vehicle.tesla.model3` - Tesla Model 3
- `vehicle.audi.a2` - Audi A2 (kompakt)
- `vehicle.bmw.grandtourer` - BMW Grand Tourer
- `vehicle.mercedes.coupe` - Mercedes Coupe
- `vehicle.toyota.prius` - Toyota Prius
- `vehicle.dodge.charger_police` - Polis arabası

### Yaya Modelleri

- `walker.pedestrian.0001` - `walker.pedestrian.0010`
- Her biri farklı yaş, cinsiyet ve kıyafet

Tam liste için:
```bash
cd ~/CARLA/PythonAPI/examples
python3 -c "import carla; client = carla.Client('localhost', 2000); \
blueprints = client.get_world().get_blueprint_library(); \
[print(bp.id) for bp in blueprints.filter('vehicle.*')]"
```

## Sorun Giderme

### CARLA'ya bağlanamıyor

```
HATA: CARLA bağlantı hatası: timeout exceeded
```

**Çözüm**:
1. CARLA sunucusu çalışıyor mu kontrol edin:
   ```bash
   ps aux | grep CarlaUE4
   ```
2. CARLA'yı başlatın:
   ```bash
   cd ~/CARLA
   ./CarlaUE4.sh
   ```
3. Firewall kontrolü:
   ```bash
   sudo ufw allow 2000/tcp
   ```

### CARLA Python API bulunamadı

```
ImportError: No module named 'carla'
```

**Çözüm**:
```bash
# PYTHONPATH'i kontrol edin
echo $PYTHONPATH

# Eksikse ekleyin
export PYTHONPATH=$PYTHONPATH:~/CARLA/PythonAPI/carla
export PYTHONPATH=$PYTHONPATH:~/CARLA/PythonAPI/carla/dist/carla-*-py3.7-linux-x86_64.egg

# Kalıcı yapmak için
echo 'export PYTHONPATH=$PYTHONPATH:~/CARLA/PythonAPI/carla' >> ~/.bashrc
source ~/.bashrc
```

### Tkinter bulunamadı

```
ModuleNotFoundError: No module named '_tkinter'
```

**Çözüm**:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

### Spawn hatası

```
RuntimeError: tried to spawn actor but failed
```

**Çözüm**:
- Spawn konumu başka bir objeyle çakışıyor olabilir
- Z koordinatını 0.5-1.0 arası deneyin
- X, Y koordinatlarını değiştirin
- Haritada geçerli bir konum olduğundan emin olun

### Düşük FPS / Yavaş çalışma

**Çözüm**:
```bash
# CARLA'yı düşük kalitede başlatın
cd ~/CARLA
./CarlaUE4.sh -quality-level=Low

# Veya no-rendering mode (sadece simülasyon)
./CarlaUE4.sh -RenderOffScreen
```

## İleri Seviye Kullanım

### Kendi Otonom Aracınızı Entegre Etme

`carla_runner.py` dosyasını düzenleyerek kendi otonom araç algoritmanızı ekleyebilirsiniz:

```python
# carla_runner.py içinde, main loop'ta:

while True:
    # Ego vehicle sensör verilerini alın
    # (kamera, LiDAR, vb. ekleyebilirsiniz)

    # Otonom algoritmanızı çalıştırın
    control = your_autonomous_algorithm(sensor_data)

    # Aracı kontrol edin
    self.ego_vehicle.apply_control(control)

    self.world.tick()
```

### Sensör Ekleme

Ego vehicle'a kamera, LiDAR, radar gibi sensörler ekleyebilirsiniz. CARLA dokümantasyonuna bakın:
- https://carla.readthedocs.io/en/latest/ref_sensors/

### Batch Senaryo Çalıştırma

Birden fazla senaryoyu sırayla çalıştırmak için:

```bash
#!/bin/bash
# run_all_scenarios.sh

for scenario in scenarios/*.json; do
    echo "Running: $scenario"
    python3 carla_runner.py "$scenario"
    sleep 5
done
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermekten çekinmeyin.

## Destek

Sorularınız için:
- CARLA Dokümantasyon: https://carla.readthedocs.io/
- CARLA GitHub: https://github.com/carla-simulator/carla
- CARLA Discord: https://discord.gg/8kqACuC

## Sürüm Geçmişi

### v1.0.0 (2024-11-18)
- İlk sürüm
- Tkinter GUI arayüzü
- JSON senaryo formatı
- CARLA entegrasyonu
- Örnek senaryolar
- Waypoint sistemi
- Çoklu NPC desteği
- Hava durumu kontrolü

## Önerilen Test Senaryoları

### 1. Acil Fren Testi
- Ego vehicle hızla gider
- Önündeki araç aniden durur
- Çarpışma önleme algoritması testi

### 2. Şerit Değiştirme Testi
- Ego vehicle yavaş giden aracın arkasında
- Yan şeritte boşluk var
- Aşma kararı ve güvenli şerit değiştirme

### 3. Kör Nokta Testi
- Ego vehicle şerit değiştirmeye çalışır
- Kör noktada başka bir araç var
- Sensör füzyonu ve güvenlik testi

### 4. Trafik Işığı Testi
- Kavşakta trafik ışığı (manuel CARLA ayarı gerekli)
- Kırmızı ışıkta durma
- Yeşil ışıkta geçiş

### 5. Çoklu Yaya Testi
- Yoğun yaya trafiği
- Beklenmedik yaya hareketleri
- Yaya önceliği testi

### 6. Hava Koşulları Testi
- Aynı senaryoyu farklı hava koşullarında test edin:
  - Açık hava
  - Yağmurlu
  - Sisli
  - Gece
- Algoritmanın dayanıklılığını test edin

## Gelecek Özellikler (Roadmap)

- [ ] Trafik ışığı desteği
- [ ] Stop/Yield işaret desteği
- [ ] Sensör konfigürasyonu (kamera, LiDAR, vb.)
- [ ] Senaryo karşılaştırma aracı
- [ ] Otomatik test raporu oluşturma
- [ ] Video kayıt desteği
- [ ] ROS entegrasyonu
- [ ] Harita üzerinde görsel senaryo düzenleme
- [ ] Senaryo şablonları kütüphanesi
