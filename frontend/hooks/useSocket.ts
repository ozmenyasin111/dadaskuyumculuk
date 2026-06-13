"use client";

import { useCallback, useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";

import type { PricesPayload } from "@/lib/types";

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

    // İlk yüklemede REST'ten snapshot al — socket bağlanana kadar boş ekran olmasın
    fetch(`${apiUrl}/api/prices`)
      .then((r) => r.json())
      .then((d: PricesPayload) => {
        if (!cancelled) setState(d);
      })
      .catch(() => {});

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
  }, []);

  return { ...state, refresh };
}
