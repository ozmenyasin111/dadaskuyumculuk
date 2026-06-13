# 📁 Yeni Müşteri Dosyaları — Harita

Bu klasör, **yeni bir kuyumcu müşteri** için web sitesi + backend + mobil uygulama
üretip yayınlamanın tüm rehberlerini içerir.

## Hangi dosya ne işe yarar?

| Dosya | İçinde ne var | Ne zaman aç |
|---|---|---|
| **yeni_musteri_tam_app_promptu.md** | Claude'a yapıştırılan hazır prompt → web+backend+mobil tüm app'i üretir | **1.** En başta. Doldur, yeni Claude'a at |
| **YENI_MUSTERI_REHBERI.md** | Web sitesi + backend'i canlıya alma (Hostinger domain, Railway, DNS, admin) | **2.** Kod hazır olunca, siteyi yayınla |
| **MAGAZA_HESAP_VE_YAYIN_REHBERI.md** | App Store + Google Play hesabı açma + uygulamayı yayınlama | **3.** App'i mağazaya koyarken |
| **MOBIL_TEST_REHBERI.md** | Mobil app'i test etme + build alma (APK/iOS) | Gerekirse 2-3 arasında, test için |

## Sıra (örnek: "Ensar Kuyumculuk" geldi)

```
1. yeni_musteri_tam_app_promptu.md   → doldur, Claude'a at        (KOD)
2. YENI_MUSTERI_REHBERI.md           → web + backend canlıya       (WEB/BACKEND)
3. MAGAZA_HESAP_VE_YAYIN_REHBERI.md  → App Store + Play Store       (MAĞAZA)
   (test gerekirse → MOBIL_TEST_REHBERI.md)
```

## Tek cümle
- **prompt** = kodu üret · **YENI_MUSTERI_REHBERI** = web/backend yayınla ·
  **MAGAZA** = telefon uygulamasını mağazaya koy · **MOBIL_TEST** = test/build
