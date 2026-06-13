"use client";

import { useCallback, useEffect, useState } from "react";
import { Capacitor } from "@capacitor/core";
import { io, Socket } from "socket.io-client";

import type { PricesPayload } from "@/lib/types";

// Native'de socket yerine polling — webview origin'i (https://localhost)
// backend CORS listesinde olmadığından socket.io handshake'i reddedilir.
// CapacitorHttp REST fetch'i OS katmanına taşıyıp CORS'u baypas eder.
const NATIVE_POLL_MS = 3000;

const initial: PricesPayload = {
  fiyatlar: [],
  pariteler: [],
  guncellendi: 0,
  healthy: false,
};

export type UsePricesResult = PricesPayload & {
  /** REST snapshot'ı yeniden çeker (mobil pull-to-refresh için). */
  refresh: () => Promise<void>;
};

export function usePrices(): UsePricesResult {
  const [state, setState] = useState<PricesPayload>(initial);

  // Pull-to-refresh: socket zaten canlı güncelliyor ama kullanıcı manuel
  // çekince anında REST snapshot'ı tazeleriz.
  const refresh = useCallback(async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";
    try {
      const r = await fetch(`${apiUrl}/api/prices`, { cache: "no-store" });
      const d: PricesPayload = await r.json();
      setState(d);
    } catch {
      // sessizce yut — socket bir sonraki tick'te güncelleyecek
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

    // İlk yüklemede REST'ten snapshot al — boş ekran olmasın
    refresh();

    // Native (iOS/Android): socket CORS'a takılır → 3 sn'de bir REST polling
    if (Capacitor.isNativePlatform()) {
      const id = setInterval(() => {
        if (!cancelled) refresh();
      }, NATIVE_POLL_MS);
      return () => {
        cancelled = true;
        clearInterval(id);
      };
    }

    // Web (tarayıcı): mevcut canlı socket.io akışı — aynen
    const socketUrl = process.env.NEXT_PUBLIC_SOCKET_URL || apiUrl;
    const socket: Socket = io(socketUrl, {
      path: "/socket.io",
      transports: ["websocket", "polling"],
    });
    socket.on("prices", (payload: PricesPayload) => {
      if (!cancelled) setState(payload);
    });

    return () => {
      cancelled = true;
      socket.disconnect();
    };
  }, [refresh]);

  return { ...state, refresh };
}
