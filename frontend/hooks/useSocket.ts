"use client";

import { useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";

import type { PricesPayload } from "@/lib/types";

const initial: PricesPayload = {
  fiyatlar: [],
  pariteler: [],
  guncellendi: 0,
  healthy: false,
};

export function usePrices(): PricesPayload {
  const [state, setState] = useState<PricesPayload>(initial);

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

  return state;
}
