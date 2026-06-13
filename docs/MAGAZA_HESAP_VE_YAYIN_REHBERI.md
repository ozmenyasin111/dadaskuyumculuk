# Mağaza Hesabı Açma & Uygulama Yayınlama Rehberi (App Store + Google Play)

> Her yeni müşteri için **App Store** (Apple) ve **Google Play** (Google) hesabı açıp
> uygulamayı yayınlama. Hesaplar **müşterinin kendi adına** açılır (Apple'ın 4.3
> "template app" reddini önlemek + sahiplik müşteride kalsın diye), sen operasyonu
> yaparsın. Hepsi **tek MacBook**'tan yönetilebilir.

---

## 0. BAŞLAMADAN — Müşteriden İste (her iki mağaza için ortak)

- [ ] **İşletme yasal adı** (vergi levhasındaki tam ad)
- [ ] **Vergi no / TC** (kimlik doğrulama için)
- [ ] **İşletme adresi + telefon**
- [ ] **Resmi e-posta** (yoksa müşteriye özel aç: `ensarkuyumculuk.app@gmail.com`)
- [ ] **Ödeme kartı** (Apple $99/yıl, Google $25 tek sefer — müşteriye fatura et)
- [ ] **Logo** (1024×1024 PNG, köşesiz, şeffaf değil — tam dolu)
- [ ] **Web sitesi/gizlilik (KVKK) sayfası URL'si** (`https://{{DOMAIN}}/kvkk` kullanılabilir)
- [ ] **Kısa + uzun açıklama metni** (mağaza listesi için)
- [ ] **Apple için organizasyon hesabı:** **D-U-N-S numarası** (ücretsiz, dnb.com'dan; yoksa başvur, 3-10 gün sürebilir)

> 🔐 **2FA/şifre yönetimi:** Her hesabın kendi e-posta + telefon + 2 adımlı doğrulaması olur.
> Hepsini bir **şifre yöneticisinde** (1Password/Bitwarden) sakla. 2FA kodu için müşterinin
> telefonu veya senin kontrolündeki bir numara hesaba ekli olsun. Asıl iş yükü budur (Mac değil).

---

## 🍎 BÖLÜM A — APPLE (App Store)

### A1. Apple Developer Program'a kayıt ($99/yıl)
1. Müşteriye özel **Apple ID** oluştur (appleid.apple.com) — resmi e-posta ile, 2FA aç.
2. https://developer.apple.com/programs/enroll aç → bu Apple ID ile giriş.
3. Hesap tipi:
   - **Organization (önerilen, işletme için):** D-U-N-S numarası + yasal işletme adı ister.
     Satıcı adı işletme adı olarak görünür (daha profesyonel).
   - **Individual:** D-U-N-S gerekmez, hızlı; ama satıcı adı kişi adı olur.
4. Bilgileri gir (yasal ad, adres, telefon, website).
5. $99 yıllık ödemeyi yap.
6. Apple doğrulaması: Individual genelde saatler, Organization birkaç gün sürebilir
   (Apple telefonla arayıp teyit edebilir).

### A2. App Store Connect'te uygulama oluştur
1. https://appstoreconnect.apple.com → "My Apps" → "+" → "New App"
2. Doldur:
   - Platform: iOS
   - İsim: **{{BRAND_NAME}}** (mağazada görünen, benzersiz olmalı)
   - Birincil dil: Türkçe
   - Bundle ID: **{{BUNDLE_ID}}** (Xcode'da kullandığınla AYNI — listede çıkar)
   - SKU: serbest bir kod (örn. `ensar001`)

### A3. Xcode'dan yükle (Mac'te)
1. `cd {{NEW_DIR}}/frontend && npm run open:ios`
2. Xcode → proje → **Signing & Capabilities**:
   - Team: müşterinin Apple Developer hesabı
   - "Automatically manage signing" ✅
3. Üst cihaz seçici → **"Any iOS Device (arm64)"**
4. **Product → Archive** (5-10 dk)
5. Organizer açılır → **"Distribute App"** → **"App Store Connect"** → **"Upload"**
6. Yükleme bitince App Store Connect'te "Build" birkaç dk içinde görünür.

### A4. Mağaza listesi + gönderim
App Store Connect'te uygulama sayfasında doldur:
- **Ekran görüntüleri:** 6.7" iPhone (1290×2796) zorunlu — en az 3 adet
  (simülatörde `xcrun simctl io booted screenshot` ile alabilirsin)
- **Açıklama, anahtar kelimeler, destek URL'si** (`https://{{DOMAIN}}`)
- **Gizlilik politikası URL'si:** `https://{{DOMAIN}}/kvkk`
- **App Privacy (veri toplama):** Uygulama sadece fiyat gösteriyor, kişisel veri toplamıyorsa
  "Data Not Collected" işaretle (doğruysa)
- **Yaş sınırı:** 4+ (finans/bilgi içeriği)
- **Fiyat:** Ücretsiz
- "Add for Review" → **Submit for Review**
- Apple incelemesi: **genelde 1-3 gün** → onaylanınca yayında.

---

## 🤖 BÖLÜM B — GOOGLE (Play Store)

### B1. Play Console hesabı ($25 tek sefer)
1. Müşteriye özel **Google hesabı** (yoksa aç), 2FA aç.
2. https://play.google.com/console → bu hesapla giriş → **$25 tek seferlik** öde.
3. Hesap tipi: **Organization** (işletme) veya Personal.
4. **Kimlik doğrulama:** Google, ad/adres/telefon + (işletme için) D-U-N-S benzeri belge
   isteyebilir. Doğrulama birkaç gün sürebilir — erken başlat.

### B2. Uygulama oluştur
1. Play Console → "Create app"
2. Uygulama adı: **{{BRAND_NAME}}**, dil: Türkçe, tip: App, Ücretsiz.

### B3. İmzalı .aab üret (Mac'te)
1. `cd {{NEW_DIR}}/frontend && npm run open:android` (Android Studio açılır)
2. **Build → Generate Signed Bundle / APK → Android App Bundle**
3. İlk seferde **"Create new keystore"**:
   - Konum: güvenli bir yer (örn. `~/keystores/{{BRAND_NAME}}.jks`)
   - Şifre + alias belirle
   - 🔴 **Bu keystore + şifreyi GÜVENLİ SAKLA (şifre yöneticisi).**
     Kaybedersen uygulamayı bir daha GÜNCELLEYEMEZSİN.
4. Release build → `.aab` dosyası oluşur (`frontend/android/app/release/`)

### B4. Mağaza listesi + yayın
Play Console'da doldur:
- **App icon** (512×512), **Feature graphic** (1024×500)
- **Ekran görüntüleri:** en az 2 telefon görüntüsü (emülatör/cihazdan)
- **Kısa + uzun açıklama**
- **Gizlilik politikası URL:** `https://{{DOMAIN}}/kvkk`
- **Data safety formu:** veri toplama durumunu işaretle (sadece fiyat gösteriyorsa minimal)
- **Content rating** anketini doldur
- **Production** → "Create new release" → `.aab` yükle → "Review release" → "Start rollout"
- Google incelemesi: **birkaç saat – birkaç gün** → onaylanınca yayında.

---

## 📋 Hızlı Checklist (her müşteri)

**Apple**
- [ ] Müşteriye özel Apple ID + 2FA
- [ ] (Org için) D-U-N-S numarası
- [ ] Developer Program $99 ödendi + doğrulandı
- [ ] App Store Connect'te app oluşturuldu (bundle id eşleşti)
- [ ] Xcode Archive → Upload
- [ ] Ekran görüntüleri + açıklama + gizlilik URL + privacy formu
- [ ] Submit for Review → onay

**Google**
- [ ] Müşteriye özel Google hesabı + 2FA
- [ ] Play Console $25 + kimlik doğrulama
- [ ] App oluşturuldu
- [ ] **Keystore üretildi + GÜVENLİ saklandı**
- [ ] İmzalı .aab üretildi + yüklendi
- [ ] İkon + görseller + açıklama + gizlilik + data safety + content rating
- [ ] Production rollout → onay

---

## ⏱️ Süre beklentileri
- Apple hesap doğrulama: saatler (Individual) – günler (Organization)
- D-U-N-S başvurusu: 3-10 iş günü (erken başla)
- Apple app incelemesi: 1-3 gün
- Google hesap doğrulama: 1-3 gün
- Google app incelemesi: saatler – birkaç gün

## 💡 Notlar
- **Tek MacBook yeter** — Xcode birden çok Apple hesabını tutar (Settings → Accounts),
  Play Console web tabanlı. Sınırlayıcı donanım değil, **hesap/2FA yönetimidir.**
- Her müşterinin **kendi keystore'u, bundle id'si, hesapları** olur — karıştırma.
- App ret yerse Apple/Google sebebi yazar; düzelt + tekrar gönder (normal süreç).

**Doküman:** Claude · dadaskuyumculuk müşteri çoğaltma seti
