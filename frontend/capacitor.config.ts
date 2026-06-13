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
    SplashScreen: {
      launchShowDuration: 1200,
      backgroundColor: '#B89B5E',
      showSpinner: false,
      androidScaleType: 'CENTER_CROP',
    },
    StatusBar: {
      style: 'LIGHT',
      backgroundColor: '#B89B5E',
    },
  },
};

export default config;
