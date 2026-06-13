"use client";

import { useEffect, useState } from "react";
import { Capacitor } from "@capacitor/core";

/**
 * Capacitor native platform (iOS/Android) tespiti — SSR/prerender güvenli.
 *
 * Statik export sırasında sayfa build-time'da render edilir (native=false).
 * Bunu doğrudan render'da kullanırsak hydration mismatch olur. O yüzden
 * mount sonrası `useEffect`'te okuyup state'e yazıyoruz: ilk paint web,
 * mount sonrası native UI'a geçer.
 */
export function useNative(): boolean {
  const [isNative, setIsNative] = useState(false);

  useEffect(() => {
    setIsNative(Capacitor.isNativePlatform());
  }, []);

  return isNative;
}
