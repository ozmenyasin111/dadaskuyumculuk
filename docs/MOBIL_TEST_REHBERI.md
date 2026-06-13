# Dadaş Kuyumculuk Mobil App — Test & Yayın Rehberi

Bu belge, Claude'un kurduğu mobil app'i **senin** Mac'inde test edip mağazaya
yüklemen için adım adım rehber. Kod tarafı (Capacitor + 3 sekme + splash/ikon)
**hazır ve Android debug APK başarıyla build edildi.**

> Tüm çalışma local. GitHub'a push YOK, Railway/canlı site etkilenmedi.

---

## 🔧 Kurulu olanlar (Claude kurdu)
- ✅ Node.js 26 + npm (Mac'inde hiç yoktu)
- ✅ CocoaPods (iOS için, brew)
- ✅ Android SDK (command-line, `~/Library/Android/sdk`)
- ✅ JDK 21 (Gradle build için — sistem Java 25/17 uyumsuzdu)
- ✅ Android platformu + debug APK

## ⏳ Senin kurman gerekenler
- **Android emulator testi için:** Android Studio (opsiyonel — gerçek telefonla APK testi Studio'suz da olur)
- **iOS için:** Xcode 16.4 (App Store değil, developer.apple.com) + ~20GB disk

---

## 🤖 ANDROID

### Yol 1 — EN HIZLI: Debug APK'yı gerçek telefona kur (Android Studio'suz)

Şu an hazır APK:
```
frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

**A) USB ile (kablo):**
1. Android telefonunda: Ayarlar → Telefon Hakkında → "Build number"a 7 kez dokun → Geliştirici modu açılır
2. Ayarlar → Geliştirici Seçenekleri → "USB Debugging" aç
3. Telefonu USB ile Mac'e bağla, "Trust" / "İzin ver" de
4. **Yeni bir terminal** aç (PATH yenilensin) ve:
   ```bash
   cd /Users/esmanurozmen/Desktop/dadaskuyumculuk/frontend
   adb install -r android/app/build/outputs/apk/debug/app-debug.apk
   ```
5. Telefonda "Dadaş Kuyumculuk" uygulaması açılır.

**B) Dosya göndererek (kablosuz):**
- `app-debug.apk` dosyasını WhatsApp/Drive/AirDroid ile telefona at
- Telefonda dosyayı aç → "Bilinmeyen kaynaklara izin ver" → kur

### Yol 2 — Android Studio ile emulator testi
1. https://developer.android.com/studio → indir → "Standard installation"
2. Projeyi aç:
   ```bash
   cd /Users/esmanurozmen/Desktop/dadaskuyumculuk/frontend
   npm run open:android      # = npx cap open android
   ```
3. Gradle sync biter (5-10 dk, ilk sefer)
4. Üst sağ "Device Manager" → Pixel emulator kur → yeşil ▶ Play

### Test kontrol listesi (her iki yolda)
- [ ] Açılışta gold splash + logo görünüyor mu?
- [ ] **Sarrafiye** sekmesi default açılıyor mu? (Gram Altın, Bilezik, Çeyrek… canlı fiyatlar)
- [ ] **Döviz** sekmesi: USD/EUR/GBP… + altta Pariteler
- [ ] **İletişim**: logo + telefon (tıkla → arama) + harita + Instagram
- [ ] Fiyatlar canlı güncelleniyor mu? (Socket.io, birkaç saniyede tik)
- [ ] Sarrafiye/Döviz'de aşağı çekince **pull-to-refresh** dönüyor mu?
- [ ] Alt tab bar 3 sekme arası geçiş yapıyor mu?
- [ ] ❌ Kuyumcu Paneli / Admin / KVKK GÖZÜKMÜYOR (olması gereken bu)

### Play Store'a yükleme (.aab)
> ⚠️ Önce gerçek cihaz/emulator testini bitir.

1. Android Studio → **Build → Generate Signed Bundle / APK** → "Android App Bundle"
2. İlk seferde **"Create new keystore"** → şifre + alias belirle
   - 🔴 **Bu keystore dosyasını ÇOK GÜVENLİ SAKLA + şifresini not al.**
     Kaybedersen aynı uygulamayı bir daha güncelleyemezsin.
3. Release build → `.aab` üretilir
4. https://play.google.com/console ($25 tek seferlik) → uygulama oluştur → `.aab` yükle
5. Google kontrolü ~birkaç saat

> Alternatif (CLI ile .aab): keystore oluşturduktan sonra Claude sana
> `./gradlew bundleRelease` komutuyla imzalı .aab üretmende yardımcı olabilir.

---

## 🍎 iOS (Xcode hazır olunca)

### Önce: Xcode 16.4 kur
- macOS 15.7'de App Store'daki Xcode 26 **çalışmaz**.
- https://developer.apple.com/download/all/ → "Xcode 16.4" ara → `.xip` indir
  (ücretsiz Apple ID gerekir) → çift tıkla → `/Applications`'a taşı
- ⚠️ ~20GB boş disk gerekir (şu an 27GB var ama Xcode kurulumu sırasında dolabilir)
- Kurulunca: `sudo xcodebuild -license accept`

### Sonra: bana "Xcode kuruldu" de — ben şunları yaparım
- `npx cap add ios`
- `npx capacitor-assets generate --ios` (ikon + splash)
- `ios/App/App/Info.plist`: CFBundleDisplayName, light status bar
- iOS build doğrulama

### Sen (Xcode'da)
1. `npm run open:ios` → Xcode açılır
2. **Signing & Capabilities** → Apple Developer hesabını ("Team") seç ($99/yıl)
3. Simulator seç → ▶ Play → test (yukarıdaki kontrol listesi)
4. Yayın: cihaz seçici → "Any iOS Device" → **Product → Archive** →
   "Distribute App" → "App Store Connect" → "Upload"
5. Apple kontrolü ~1-2 gün

---

## 🔁 Kod değişince ne yapmalı?
Web tarafında bir şey değişti ve mobile yansısın istiyorsan:
```bash
cd /Users/esmanurozmen/Desktop/dadaskuyumculuk/frontend
npm run sync:mobile        # = MOBILE_BUILD=1 next build && cap sync
```
Sonra Android Studio/Xcode'da tekrar build al.

---

## 🆘 Sık sorunlar
| Sorun | Çözüm |
|---|---|
| `adb: command not found` | Yeni terminal aç (PATH `~/.zshrc`'ye eklendi) |
| Gradle "Unsupported class version" | JDK 21 ayarı `android/gradle.properties`'te — dokunma |
| Emulator çok yavaş | Device Manager → emulator → "Cold Boot Now" |
| iOS "No signing certificate" | Xcode → Settings → Accounts → Apple ID ekle |

**Doküman:** Claude tarafından üretildi · 2026-06-13
