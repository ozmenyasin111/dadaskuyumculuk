import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.dadaskuyumculuk.app',
  appName: 'Dadaş Kuyumculuk',
  webDir: 'out',
  server: {
    androidScheme: 'https',
  },
  plugins: {
    // Native fetch/XHR'ı OS katmanına taşır → backend CORS'unu baypas eder
    // (backend cors_origins'e capacitor origin eklenmiyor; backend'e dokunmuyoruz).
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
      // Beyaz ikonlar + webview status bar altına uzanır (edge-to-edge).
      // Renk gold header'dan gelir (targetSdk 36'da backgroundColor no-op).
      style: 'LIGHT',
      overlaysWebView: true,
    },
  },
};

export default config;
