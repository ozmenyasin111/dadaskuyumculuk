"use client";

import { MobileApp } from "@/components/mobile/MobileApp";
import { useNative } from "@/components/mobile/useNative";
import { WebHome } from "@/components/WebHome";

export default function HomePage() {
  const isNative = useNative();

  // Native (iOS/Android Capacitor) → tab bar'lı mobil uygulama.
  // Web (tarayıcı) → mevcut site AYNEN. İlk paint web; native'de splash
  // ekranı bu kısa anı örter, mount sonrası mobil UI'a geçilir.
  if (isNative) return <MobileApp />;
  return <WebHome />;
}
