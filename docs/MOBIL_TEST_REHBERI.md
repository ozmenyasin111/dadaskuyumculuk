# Dadaş Kuyumculuk Mobil App — Test & Yayın Rehberi

Mobil app `mobileappdadas` branch'inde, Capacitor ile paketlendi. Android debug
APK başarıyla build edildi. Tüm çalışma local — push/merge yok, Railway/canlı
site ve backend etkilenmedi.

## 🔧 Kurulu olanlar (Claude kurdu — bilgisayar geneli, branch'e bağlı değil)
- Node.js + npm, CocoaPods, Android SDK (`~/Library/Android/sdk`), JDK 21

## ⏳ Senin kurman gerekenler
- **Android emulator testi:** Android Studio (opsiyonel — gerçek telefonla APK testi Studio'suz olur)
- **iOS:** Xcode 16.4 (App Store değil, developer.apple.com) + ~20GB disk

---

## 🤖 ANDROID

### Yol 1 — EN HIZLI: APK'yı telefona kur (Android Studio'suz)
Hazır APK: `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
(ayrıca Masaüstünde `dadaskuyumculuk-v4.apk`).

**Drive ile:**
1. APK'yı Google Drive'a yükle
2. Telefonda Drive → indir
3. Dosyaya dokun → "Bilinmeyen kaynaklara izin ver" → Yükle → aç

**USB ile (adb):**
```bash
cd /Users/esmanurozmen/Desktop/dadaskuyumculuk/frontend
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
```

### Yol 2 — Android Studio ile emulator
1. https://developer.android.com/studio → "Standard installation"
2. `cd frontend && npm run open:android`
3. Gradle sync (5-10 dk) → Device Manager → emulator → ▶ Play

### Test kontrol listesi
- [ ] Gold splash + logo
- [ ] **Sarrafiye** default açılıyor (canlı fiyatlar)
- [ ] **Döviz** + altta Pariteler
- [ ] **İletişim**: telefon (tıkla→arama), harita, Instagram
- [ ] Fiyatlar 3 sn'de güncelleniyor, yeşil/kırmızı oklar oynuyor
- [ ] Pull-to-refresh çalışıyor
- [ ] Üst gold şerit status bar'ın arkasına kadar uzanıyor (siyah yok)
- [ ] ❌ Admin / KVKK / Kuyumcu Paneli görünmüyor

### Play Store (.aab)
1. Android Studio → Build → Generate Signed Bundle → "Android App Bundle"
2. İlk sefer "Create new keystore" → şifre+alias → 🔴 **keystore'u GÜVENLİ SAKLA**
3. https://play.google.com/console ($25) → app oluştur → .aab yükle

---

## 🍎 iOS (Xcode hazır olunca)
1. developer.apple.com/download/all → "Xcode 16.4" .xip → /Applications (~20GB disk)
2. `sudo xcodebuild -license accept`
3. Bana "Xcode kuruldu" de → ben `cap add ios` + ikon/splash + Info.plist yaparım
4. `npm run open:ios` → Signing & Capabilities → Team seç → ▶ → test
5. Product → Archive → Distribute → App Store Connect → Upload

---

## 🔁 Kod değişince
```bash
cd frontend && npm run sync:mobile   # build:mobile + cap sync
```
Sonra Android Studio/Xcode'da tekrar build.

**Doküman:** Claude · branch mobileappdadas
