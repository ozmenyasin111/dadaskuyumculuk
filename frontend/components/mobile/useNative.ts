"use client";

import { useEffect, useState } from "react";
import { Capacitor } from "@capacitor/core";

/**
 * Capacitor native platform (iOS/Android) tespiti — SSR/prerender güvenli.
 *
 * Statik export'ta sayfa build-time'da render edilir (native=false). Doğrudan
 * render'da kullanırsak hydration mismatch olur; mount sonrası okuyup state'e
 * yazıyoruz: ilk paint web, mount sonrası native UI'a geçer.
 */
export function useNative(): boolean {
  const [isNative, setIsNative] = useState(false);

  useEffect(() => {
    setIsNative(Capacitor.isNativePlatform());
  }, []);

  return isNative;
}
