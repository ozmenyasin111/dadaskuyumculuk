# Yeni Müşteri — TAM Uygulama (Web + Backend + Mobil) Çoğaltma Promptu

> `dadaskuyumculuk` projesini şablon alıp **yeni bir kuyumcu** için HER ŞEYİ üretmek:
> dükkanda gösterilecek **canlı web sitesi**, **backend** (fiyat motoru + admin), ve
> **App Store + Google Play mobil uygulaması**. Mevcut Dadaş projesine/canlısına dokunulmaz.
>
> **Önemli:** Şablon kaynağı `mobileappdadas` branch'idir — içinde backend + web + mobil
> HEPSİ var. `mobile-app` branch'ini ALMA (eski/silinecek). `main`'deki backend+frontend
> zaten `mobileappdadas` içinde mevcut (oradan dallandı).

---

## 🛠️ ÖN HAZIRLIK (promptu atmadan önce)

1. **GitHub'da yeni boş private repo** aç (örn. `ensarkuyumculuk`), locale clone'la.
   - Alternatif: Dadaş repo'sunu "template" yapıp "Use this template" — ama o `main`'i kopyalar (mobil yok). Mobil de istiyorsan bu prompt yöntemi (workspace'ten kopya) daha iyi.
2. VS Code'da: `dadaskuyumculuk` klasörünü **workspace olarak ekle** (şablon), yeni müşteri klasörünü de aç.
3. Müşteri **logosu** (kare PNG, tercihen şeffaf ~1024px) hazır olsun.
4. Araçlar (Node, Android SDK, JDK 21, Xcode 16.4, CocoaPods) bu Mac'te kurulu — tekrar gerekmez.
5. Web/backend yayını + mağaza hesapları için yanına bu iki dokümanı al:
   - `docs/YENI_MUSTERI/YENI_MUSTERI_REHBERI.md` → Hostinger domain + Railway (backend/web) + DNS + admin (adım adım)
   - `docs/YENI_MUSTERI/MAGAZA_HESAP_VE_YAYIN_REHBERI.md` → App Store + Google Play hesap açma + yayınlama

---

## ✍️ DOLDUR — Yeni Müşteri Bilgileri

| Alan | Örnek | Senin değerin |
|---|---|---|
| Marka adı | Ensar Kuyumculuk | `{{BRAND_NAME}}` |
| Web domaini | ensarkuyumculuk.com | `{{DOMAIN}}` |
| Backend (API) domaini | api.ensarkuyumculuk.com | `{{API_URL}}` |
| Mobil Bundle ID (benzersiz!) | com.ensarkuyumculuk.app | `{{BUNDLE_ID}}` |
| Yeni proje klasörü | /Users/.../Desktop/ensarkuyumculuk | `{{NEW_DIR}}` |
| Marka rengi (hex) | #B89B5E (farklıysa değiştir) | `{{BRAND_COLOR}}` |
| Logo dosyası | ~/Desktop/ensar_logo.png | `{{LOGO_PATH}}` |
| Telefon (görünen / tel:) | 0212 000 00 00 / tel:02120000000 | `{{PHONE}}` / `{{PHONE_TEL}}` |
| Harita linki | https://maps.google.com/... | `{{MAP_URL}}` |
| Instagram | https://instagram.com/ensarkuyumculuk | `{{INSTAGRAM}}` |
| Kuruluş yılı / hakkımızda | 1990 / kısa metin | `{{ABOUT}}` |
| finansveri API anahtarı | (mevcut anahtar paylaşılabilir veya müşteriye yeni) | `{{FINANSVERI_KEY}}` |

---

## 📋 Prompt (kopyala ↓)

```
Selam Claude. Workspace'te iki klasör var: şablon "dadaskuyumculuk" ve yeni/boş
"{{NEW_DIR}}". Dadaş projesini ŞABLON alıp yeni bir kuyumcu için TAM uygulama
üreteceğiz: (1) canlı web sitesi, (2) backend (fiyat motoru + admin), (3) App Store
+ Google Play mobil uygulaması.

═══════════════════════════════════════════════════════════════
⚠️ KRİTİK KURALLAR
═══════════════════════════════════════════════════════════════
1. dadaskuyumculuk klasörüne / canlı sitesine / Railway'ine DOKUNMA. Sadece OKU.
   Tüm yazma işlemi {{NEW_DIR}} içinde.
2. ŞABLON KAYNAĞI: dadaskuyumculuk'un "mobileappdadas" branch'i (backend + web +
   mobil HEPSİ burada). "mobile-app" branch'ini KULLANMA.
3. PUSH'u ben söylemeden yapma. {{NEW_DIR}} kendi repo'su; oraya commit/push serbest
   ama önce bana plan sun.
4. Build local; .apk/.aab/iOS doğrudan müşterinin mağaza hesabına yüklenecek.

═══════════════════════════════════════════════════════════════
🎯 YENİ MÜŞTERİ DEĞERLERİ
═══════════════════════════════════════════════════════════════
- Marka: {{BRAND_NAME}}        - Web domain: {{DOMAIN}}
- Backend API/Socket: {{API_URL}}   - Bundle ID: {{BUNDLE_ID}}
- Marka rengi: {{BRAND_COLOR}}  - Logo: {{LOGO_PATH}}
- Telefon: {{PHONE}} ({{PHONE_TEL}})  - Harita: {{MAP_URL}}  - Instagram: {{INSTAGRAM}}
- Hakkımızda/yıl: {{ABOUT}}     - finansveri key: {{FINANSVERI_KEY}}

═══════════════════════════════════════════════════════════════
🔧 YAPILACAKLAR
═══════════════════════════════════════════════════════════════
1. dadaskuyumculuk'un mobileappdadas branch içeriğini {{NEW_DIR}}'e kopyala.
   HARİÇ tut / sıfırdan üret: node_modules, .next, out, frontend/android,
   frontend/ios (bundle id'ye gömülü → sıfırdan), .git. Şunlar GELSİN:
   backend/ (tüm fiyat motoru + admin + alembic), frontend/ (web + mobil kaynak kod),
   docker-compose, railway.json, config dosyaları.

2. MARKA ÖZELLEŞTİRME (web + mobil ortak):
   a. Global metin değişimi: "Dadaş Kuyumculuk" → "{{BRAND_NAME}}",
      "dadaskuyumculuk" → yeni kısa ad. (VS Code global replace, sonra elle kontrol)
   b. Renk: frontend/tailwind.config.ts "gold" paletini {{BRAND_COLOR}} tonuna çevir
      (uicolors.app ile 50-900 scale üret). Mobil header + status bar bu renge döner.
   c. Logo: frontend/public/logo-figure.png → {{LOGO_PATH}} ile değiştir (aynı isim).
   d. İletişim: TopBar, FooterSection, HakkimizdaSection (web) + components/mobile/
      IletisimTab.tsx (mobil) → {{PHONE}}/{{PHONE_TEL}}, {{MAP_URL}}, {{INSTAGRAM}}, {{ABOUT}}
   e. app/layout.tsx → title/description + viewport themeColor {{BRAND_COLOR}}
   f. KVKK / aydınlatma metinleri (app/kvkk, iletisim-aydinlatma, musteri-aydinlatma)
      → marka adını güncelle

3. MOBİL'E ÖZEL:
   a. capacitor.config.ts → appId: {{BUNDLE_ID}}, appName: "{{BRAND_NAME}}",
      Splash/StatusBar rengi {{BRAND_COLOR}}
   b. package.json "build:mobile" → NEXT_PUBLIC_API_URL & NEXT_PUBLIC_SOCKET_URL = {{API_URL}}

4. KORU (Dadaş'ta öğrenilen, çalışan kritik ayarlar — DEĞİŞTİRME):
   - next.config.mjs koşullu (MOBILE_BUILD → export, yoksa standalone)
   - capacitor.config: CapacitorHttp.enabled=true (CORS baypas),
     StatusBar.overlaysWebView=true
   - hooks/useSocket.ts: native'de 3sn REST polling, web socket.io
   - app/layout.tsx: viewport-fit=cover
   - Sarrafiye=ALTIN, Döviz=DOVIZ+Pariteler, İletişim 3. sekme
   - android/gradle.properties → org.gradle.java.home =
     /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home

5. KUR + NATIVE'İ SIFIRDAN ÜRET:
   - cd {{NEW_DIR}}/frontend && npm install
   - npm run build:mobile
   - npx cap add android && npx cap add ios
   - android/gradle.properties'e JDK21 satırını ekle
   - assets/logo.png üret ({{LOGO_PATH}} → 1024x1024 şeffaf kare, sharp ile)
   - npx capacitor-assets generate --android --ios
       --iconBackgroundColor '{{BRAND_COLOR}}' --splashBackgroundColor '{{BRAND_COLOR}}'
   - AndroidManifest.xml: usesCleartextTraffic=false

6. DOĞRULA (build):
   - Web: cd {{NEW_DIR}}/frontend && npm run build (standalone hatasız mı)
   - Backend: derleme/import hatası var mı (mümkünse lokalde docker-compose ile dene)
   - Android APK: cd frontend/android && ./gradlew assembleDebug →
     ~/Desktop/{{BRAND_NAME}}-v1.apk olarak kopyala
   - iOS: xcodebuild simülatör build (CODE_SIGNING_ALLOWED=NO) → BUILD SUCCEEDED;
     istersen simülatörde çalıştır + screenshot

7. Web/backend YAYINI (deploy): docs/YENI_MUSTERI/YENI_MUSTERI_REHBERI.md'yi takip et —
   Hostinger domain ({{DOMAIN}}), Railway backend+frontend+Postgres, env vars
   (CORS_ORIGINS'e {{DOMAIN}} + mobil için capacitor origin'i isteğe bağlı; biz mobilde
   CapacitorHttp kullandığımız için CORS'a mobil eklemek ZORUNLU değil), DNS, admin.

8. MAĞAZA YAYINI: docs/YENI_MUSTERI/MAGAZA_HESAP_VE_YAYIN_REHBERI.md'yi takip et —
   müşterinin Apple Developer + Google Play hesapları, .aab/iOS upload.

═══════════════════════════════════════════════════════════════
✅ ÖNCE PLAN, SONRA UYGULA
═══════════════════════════════════════════════════════════════
Önce kısa plan (hangi dosyalar değişecek, hangileri korunacak, fazlar),
sonra fazlara böl ve uygula. Native prereq hatası olursa bana söyle.
```

---

## 🎬 Sıra (büyük resim)
1. **Kod** (bu prompt) → web + backend + mobil hazır, build doğrulandı
2. **Web/backend yayını** → `YENI_MUSTERI_REHBERI.md` (Hostinger + Railway + DNS)
3. **Mağaza yayını** → `MAGAZA_HESAP_VE_YAYIN_REHBERI.md` (Apple + Google hesap + upload)

## ⚠️ Müşteri başına ayrı olması gerekenler
- Kendi **domaini** + **backend'i** (Railway projesi/Postgres) + **finansveri** kullanımı
- Mobil **bundle id** + **keystore** (Android) — keystore'u GÜVENLİ sakla
- **Apple Developer + Google Play hesapları** → müşterinin kendi adına (Apple 4.3 reddi için şart)

**Doküman:** Claude · dadaskuyumculuk (mobileappdadas) şablonundan tam çoğaltma
