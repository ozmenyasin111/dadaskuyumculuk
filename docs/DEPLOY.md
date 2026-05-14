# Railway + Hostinger Deploy Rehberi

Bu doküman canlı yayını (`https://dadaskuyumculuk.com`) ayağa kaldırmak için adım adım yönergeleri içerir.

## 1. GitHub repo

Bu projeyi GitHub'a (örn. `ozmenyasin111/dadaskuyumculuk`) `git push` ile yüklediğinizi varsayıyoruz.

## 2. Railway projesini oluştur

1. https://railway.com → "New Project" → "Deploy from GitHub repo" → repository'yi seç.
2. Railway repo kökünde `Dockerfile` aramaz; her servisi ayrı root path ile ekleyeceğiz.

### 2.1 Backend servisi

- "New service" → "GitHub repo" → aynı repo
- **Root directory:** `backend`
- **Watch path:** `backend`
- Variables (env):
  - `DATABASE_URL` → Postgres add-on tarafından otomatik bağlanır (aşağıda)
  - `FINANSVERI_API_KEY` → `802ba08a...` (apidocs.txt'deki)
  - `FINANSVERI_BASE_URL` → `https://api.finansveri.com`
  - `JWT_SECRET` → en az 32 karakterli rastgele string (`openssl rand -hex 32`)
  - `JWT_EXPIRES_HOURS` → `168`
  - `ADMIN_BOOTSTRAP_USERNAME` → `admin` (ilk admin)
  - `ADMIN_BOOTSTRAP_PASSWORD` → güçlü bir şifre (ilk girişten sonra panelden değiştirin)
  - `POLL_INTERVAL_SECONDS` → `1`
  - `CORS_ORIGINS` → `https://dadaskuyumculuk.com,https://www.dadaskuyumculuk.com`
  - `ENV` → `prod`
- **Public Networking:** Railway otomatik bir `*.up.railway.app` URL'si verir; bu URL'yi frontend env'inde kullanacağız.

### 2.2 PostgreSQL add-on

- "New" → "Database" → "Add PostgreSQL"
- Backend servisinde "Reference Variable" ekleyerek `DATABASE_URL`'i Postgres'ten al.
- **Önemli:** Railway Postgres URL'si `postgresql://` ile başlar; SQLAlchemy async için `postgresql+asyncpg://` gerekir. Backend env'inde `DATABASE_URL` değeri olarak referansı şu pattern ile ayarlayın:
  - Variable: `DATABASE_URL` = `postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}`

### 2.3 Frontend servisi

- "New service" → "GitHub repo" → aynı repo
- **Root directory:** `frontend`
- Variables (env):
  - `NEXT_PUBLIC_API_URL` → backend Railway URL'si (ör. `https://dadas-backend-production.up.railway.app`)
  - `NEXT_PUBLIC_SOCKET_URL` → aynı backend URL'si
- Build target prod için `runner` (default) — `frontend/Dockerfile` çok aşamalı; Railway son aşamayı (runner) kullanır.
- Public networking aç, otomatik *.up.railway.app URL'si al.

## 3. Custom domain (Hostinger ↔ Railway)

### 3.1 Railway tarafı

- Frontend servisi → Settings → Domains → "Custom Domain" → `dadaskuyumculuk.com` ekle.
- Railway size bir DNS hedefi gösterecek (ör. `cname.up.railway.app` veya bir IP). Bu değerleri not alın.
- Aynı işlemi `www.dadaskuyumculuk.com` için tekrarlayın.

### 3.2 Hostinger DNS

- hpanel.hostinger.com → "Domains" → "dadaskuyumculuk.com" → "DNS / Nameservers" → "DNS Zone".
- **DNS Zone Editor**'da:
  - `A` kaydı: `@` → Railway IP'si (Railway gösterdiği değer)
  - `CNAME` kaydı: `www` → Railway'in `cname.up.railway.app` hedefi
- Mevcut `cosmos.dns-parking.com` / `nova.dns-parking.com` nameserver'lar dursun — sadece zone içindeki kayıtları güncelliyoruz.
- DNS yayılması ~5-30 dk.

### 3.3 SSL

- Railway Let's Encrypt sertifikasını DNS doğrulamadan sonra otomatik düzenler. "Domains" sayfasında yeşil onay görünene kadar bekleyin.

## 4. İlk giriş ve smoke test

- `https://dadaskuyumculuk.com` açılır → canlı fiyatlar gözükmeli.
- `https://dadaskuyumculuk.com/admin/login` → `admin` / belirlediğiniz şifre.
- `/admin/marjlar` → bir satırda offset değiştir, "Kaydet" → ana sayfada saniyeler içinde yansımalı.
- `/admin/volatilite` → ALTIN için threshold geçici olarak 1 yap → ana sayfada Has Altın'da override aktif olmalı (sarımsı arka plan).
- `/admin/kullanicilar` → yeni admin ekle, eski şifreyi değiştir.

## 5. Maliyet izleme

- Railway dashboard → Usage → ay sonu tahmini ~$7-15 olmalı (Hobby planı dahil).
- Aşırı kullanım için: backend `replica = 1` (zaten), frontend `replica = 1`, Postgres en küçük plan.
