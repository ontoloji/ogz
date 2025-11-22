# Kurulum Talimatları

## Gereksinimler

- Node.js (v14 veya üzeri)
- npm veya yarn

## Kurulum Adımları

### 1. Backend Kurulumu

```bash
cd backend
npm install
```

### 2. Veritabanını Başlat ve Test Verileri Ekle

```bash
# Veritabanını otomatik olarak oluştur ve test verilerini ekle
npm run init-db

# Veya manuel olarak seed script'ini çalıştır
node src/database/seed.js
```

### 3. Backend'i Başlat

```bash
# Development modu (otomatik yeniden başlatma ile)
npm run dev

# Veya production modu
npm start
```

Backend şu adreste çalışacak: `http://localhost:3001`

### 4. Frontend Kurulumu

Yeni bir terminal penceresi açın:

```bash
cd frontend
npm install
```

### 5. Environment Dosyasını Ayarla

```bash
# .env.example dosyasını .env olarak kopyalayın
cp .env.example .env
```

### 6. Frontend'i Başlat

```bash
npm start
```

Frontend şu adreste çalışacak: `http://localhost:3000`

## Kullanım

1. Tarayıcınızda `http://localhost:3000` adresine gidin
2. Ana sayfada günlük hedeflerinizi ve ilerlemenizi görebilirsiniz
3. Farklı alıştırma türlerini deneyin:
   - **Boşluk Doldurma**: Cümlelerdeki boşlukları doğru kelimelerle doldurun
   - **Kelime Eşleştirme**: Kelimeleri Türkçe anlamlarıyla eşleştirin
4. **Kelimeler** sayfasından tüm kelimeleri görüntüleyebilir ve filtreleyebilirsiniz
5. **İlerleme** sayfasından performansınızı takip edebilirsiniz

## Demo Kullanıcı

Sistem demo kullanıcı ile gelir:
- User ID: 1
- Username: demo

## API Endpoints

Backend API dokümantasyonu için README.md dosyasına bakın.

### Temel Endpoints:

- `GET /api/health` - Sistem sağlık kontrolü
- `GET /api/words` - Kelime listesi
- `GET /api/exercises/fill-blank` - Boşluk doldurma alıştırmaları
- `GET /api/exercises/match-meaning` - Kelime eşleştirme alıştırması
- `GET /api/user/:id/progress` - Kullanıcı ilerlemesi
- `POST /api/exercises/submit` - Alıştırma cevabı gönder

## Veritabanı Yönetimi

Veritabanı SQLite kullanır ve `backend/data/learning.db` konumunda saklanır.

### Veritabanını Sıfırla

```bash
cd backend
rm -rf data/learning.db
node src/database/seed.js
```

## Sorun Giderme

### Backend başlamıyor
- Port 3001'in kullanılmadığından emin olun
- `node_modules` klasörünü silip tekrar `npm install` yapın

### Frontend başlamıyor
- Port 3000'in kullanılmadığından emin olun
- `.env` dosyasının doğru yapılandırıldığından emin olun

### API çağrıları başarısız
- Backend'in çalıştığından emin olun
- CORS ayarlarını kontrol edin
- Browser console'da hata mesajlarını kontrol edin

## Geliştirme

### Yeni Kelime Ekleme

API üzerinden:

```bash
curl -X POST http://localhost:3001/api/words \
  -H "Content-Type: application/json" \
  -d '{
    "word": "example",
    "meaning_tr": "örnek",
    "meaning_en": "a sample",
    "example_sentence": "This is an example.",
    "level_id": 1,
    "category_id": 1
  }'
```

### Yeni Alıştırma Ekleme

```bash
curl -X POST http://localhost:3001/api/exercises/fill-blank \
  -H "Content-Type: application/json" \
  -d '{
    "sentence": "This is an ____ sentence.",
    "correct_answer": "example",
    "options": ["example", "sample", "test", "demo"],
    "blank_position": 11,
    "level_id": 1,
    "category_id": 1
  }'
```

## Üretim (Production) Deployment

### Backend

```bash
cd backend
npm install --production
NODE_ENV=production npm start
```

### Frontend

```bash
cd frontend
npm run build
# build/ klasörünü web sunucunuza deploy edin
```

## Lisans

MIT
