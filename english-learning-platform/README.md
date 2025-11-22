# English Learning Platform

Open English benzeri modern bir İngilizce öğrenme platformu.

## Özellikler

- 📝 **Boşluk Doldurma Alıştırmaları**: Cümlelerdeki boşlukları doğru kelimelerle tamamlama
- 🎯 **Kelime Anlamı Eşleştirme**: Kelimeleri doğru anlamlarıyla eşleştirme
- 📊 **Günlük Hedefler**: Kişiselleştirilmiş günlük kelime öğrenme hedefleri
- 📈 **İlerleme Takibi**: Detaylı performans ve öğrenme istatistikleri
- 🏆 **Seviye Sistemi**: Beginner, Intermediate, Advanced seviyeleri
- 📚 **Kategori Bazlı Öğrenme**: İş İngilizcesi, Günlük Konuşma, Akademik vs.

## Teknoloji Stack

### Backend
- Node.js + Express.js
- SQLite (geliştirme için kolay başlangıç)
- RESTful API

### Frontend
- React
- Tailwind CSS
- Axios (API iletişimi)
- React Router (sayfa yönlendirme)

## Kurulum

### Backend
```bash
cd backend
npm install
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Proje Yapısı

```
english-learning-platform/
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   └── server.js
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   └── package.json
└── database/
    └── schema.sql
```

## API Endpoints

- `GET /api/words` - Kelime listesi
- `GET /api/exercises/fill-blank` - Boşluk doldurma alıştırması
- `GET /api/exercises/match-meaning` - Kelime eşleştirme alıştırması
- `GET /api/user/progress` - Kullanıcı ilerlemesi
- `POST /api/user/goals` - Günlük hedef belirleme
- `POST /api/exercises/submit` - Alıştırma cevaplarını gönder

## Lisans

MIT
