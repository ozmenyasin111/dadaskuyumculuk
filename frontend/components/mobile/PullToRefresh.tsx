"use client";

import { Loader2 } from "lucide-react";
import { ReactNode, useRef, useState } from "react";

const THRESHOLD = 70; // px — bu kadar çekilince yenilenir
const MAX_PULL = 110; // görsel tavan
const RESISTANCE = 0.5; // çekme direnci (lastik hissi)

/**
 * Kendi kaydırılabilir alanı olan, dokunma tabanlı pull-to-refresh sarmalayıcı.
 * Ekstra bağımlılık yok; yalnızca scroll'un en üstündeyken aşağı çekince tetikler.
 */
export function PullToRefresh({
  onRefresh,
  children,
}: {
  onRefresh: () => Promise<void>;
  children: ReactNode;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const startY = useRef<number | null>(null);
  const [pull, setPull] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  const onTouchStart = (e: React.TouchEvent) => {
    if (refreshing) return;
    // Sadece en üstteyken çekmeyi yakala
    if ((scrollRef.current?.scrollTop ?? 0) <= 0) {
      startY.current = e.touches[0].clientY;
    } else {
      startY.current = null;
    }
  };

  const onTouchMove = (e: React.TouchEvent) => {
    if (startY.current === null || refreshing) return;
    const delta = e.touches[0].clientY - startY.current;
    if (delta > 0 && (scrollRef.current?.scrollTop ?? 0) <= 0) {
      setPull(Math.min(delta * RESISTANCE, MAX_PULL));
    }
  };

  const onTouchEnd = async () => {
    if (startY.current === null || refreshing) {
      startY.current = null;
      return;
    }
    startY.current = null;
    if (pull >= THRESHOLD) {
      setRefreshing(true);
      setPull(THRESHOLD);
      try {
        await onRefresh();
      } finally {
        setRefreshing(false);
        setPull(0);
      }
    } else {
      setPull(0);
    }
  };

  const ready = pull >= THRESHOLD;

  return (
    <div className="relative h-full overflow-hidden">
      {/* Yenileme göstergesi */}
      <div
        className="absolute top-0 left-0 right-0 flex items-end justify-center pointer-events-none"
        style={{ height: pull, opacity: pull > 4 ? 1 : 0 }}
      >
        <Loader2
          className={
            "w-6 h-6 mb-2 text-gold-600 " +
            (refreshing ? "animate-spin" : ready ? "rotate-180 transition-transform" : "transition-transform")
          }
        />
      </div>

      <div
        ref={scrollRef}
        className="h-full overflow-y-auto overscroll-contain"
        style={{
          transform: pull ? `translateY(${pull}px)` : undefined,
          transition: startY.current === null ? "transform 0.2s ease-out" : undefined,
        }}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        {children}
      </div>
    </div>
  );
}
