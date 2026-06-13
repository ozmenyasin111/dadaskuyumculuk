import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.dadaskuyumculuk.app',
  appName: 'Dadaş Kuyumculuk',
  webDir: 'out',
  // Statik export'ta dosyalar file:// üzerinden değil, Capacitor'ın
  // localhost şemasıyla servis edilir — Socket.io/HTTPS karışık içerik
  // sorunlarını önler. android scheme https → mixed content engellenir.
  server: {
    androidScheme: 'https',
  },
  plugins: {
    // Native fetch/XHR'ı OS katmanına taşır → backend CORS'unu baypas eder.
    // (Backend cors_origins'e capacitor origin'i eklenemiyor; dokunmuyoruz.)
    CapacitorHttp: {
      enabled: true,
    },
    SplashScreen: {
      launchShowDuration: 1200,
      backgroundColor: '#B89B5E',
      showSpinner: false,
      androidScaleType: 'CENTER_CROP',
    },
    StatusBar: {
      // Beyaz ikonlar + webview status bar'ın altına uzanır (edge-to-edge).
      // Renk, gold header'ın kendisinden gelir (targetSdk 36'da backgroundColor no-op).
      style: 'LIGHT',
      overlaysWebView: true,
    },
  },
};

export default config;
