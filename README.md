# Dadaş Kuyumculuk — Canlı Fiyat Panosu

Mağaza ekranı için canlı altın ve döviz fiyatları + admin yönetimli kâr marjları.

## Stack

- **Backend:** Python 3.12, FastAPI, python-socketio, SQLAlchemy 2.0 (async), Alembic
- **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS, socket.io-client
- **DB:** PostgreSQL
- **Deploy:** Railway + Hostinger (domain)

## Lokal geliştirme

```bash
cp backend/.env.example backend/.env       # FINANSVERI_API_KEY ekleyin
cp frontend/.env.example frontend/.env.local
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin paneli: http://localhost:3000/admin/login (default: `admin` / `admin123` — ilk girişten sonra değiştirin)

## Yapı

```
backend/   FastAPI uygulaması (worker + REST + Socket.io)
frontend/  Next.js fiyat panosu + admin paneli
docs/      Tasarım referansları, ekran görüntüleri
```

Detaylı plan: `.claude/plans/` altında.
