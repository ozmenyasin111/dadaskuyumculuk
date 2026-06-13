"use client";

import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { Clock } from "lucide-react";

import { usePrices } from "@/hooks/useSocket";
import { formatTime } from "@/lib/format";
import type { PriceRow } from "@/lib/types";

import { DovizTab } from "./DovizTab";
import { IletisimTab } from "./IletisimTab";
import { MobileTab, MobileTabBar } from "./MobileTabBar";
import { SarrafiyeTab } from "./SarrafiyeTab";

// Sarrafiye sekmesinde GÖSTERİLMEYECEK editable satırlar (Kuyumcu Paneli'ndeki
// readonly referanslar zaten "READONLY" kategorisinde, otomatik dışarıda).
// Has Altın ham referansı editable kalmışsa diye savunma amaçlı eleniyor.
const SARRAFIYE_EXCLUDE = new Set<string>(["MADEN.ALTIN"]);

export function MobileApp() {
  const { fiyatlar, pariteler, guncellendi, healthy, refresh } = usePrices();
  const [tab, setTab] = useState<MobileTab>("sarrafiye");

  const { sarrafiye, doviz } = useMemo(() => {
    const sarrafiye: PriceRow[] = [];
    const doviz: PriceRow[] = [];
    for (const r of fiyatlar) {
      if (r.category === "ALTIN" && !SARRAFIYE_EXCLUDE.has(r.symbol_key)) {
        sarrafiye.push(r);
      } else if (r.category === "DOVIZ") {
        doviz.push(r);
      }
      // READONLY (Kuyumcu Paneli) mobilde hiç gösterilmez.
    }
    return { sarrafiye, doviz };
  }, [fiyatlar]);

  // Native kurulum: status bar stili + splash gizle + Android geri tuşu.
  useEffect(() => {
    let cleanup: (() => void) | undefined;
    (async () => {
      const { Capacitor } = await import("@capacitor/core");
      if (!Capacitor.isNativePlatform()) return;

      const { StatusBar, Style } = await import("@capacitor/status-bar");
      const { SplashScreen } = await import("@capacitor/splash-screen");
      const { App } = await import("@capacitor/app");

      // Beyaz ikonlar + webview status bar altına uzanır → gold header oraya basar
      StatusBar.setStyle({ style: Style.Light }).catch(() => {});
      StatusBar.setOverlaysWebView({ overlay: true }).catch(() => {});
      SplashScreen.hide().catch(() => {});

      // Android donanım geri tuşu: kök sekmedeyse uygulamadan çık, değilse
      // Sarrafiye'ye dön.
      const handle = await App.addListener("backButton", () => {
        setTab((cur) => {
          if (cur === "sarrafiye") {
            App.exitApp();
            return cur;
          }
          return "sarrafiye";
        });
      });
      cleanup = () => handle.remove();
    })();
    return () => cleanup?.();
  }, []);

  return (
    <div className="flex flex-col h-[100dvh] bg-gray-50">
      {/* Marka başlığı — gold, status bar'ın altına uzanır (Harem tarzı, beyaz ikon).
          Hamburger/menü YOK. */}
      <header
        className="flex-shrink-0 bg-gradient-to-b from-gold-600 to-gold-500 flex items-center justify-between px-4 py-2.5"
        style={{ paddingTop: "calc(env(safe-area-inset-top) + 0.6rem)" }}
      >
        <div className="flex items-center gap-2 min-w-0">
          <Image
            src="/logo-figure.png"
            alt=""
            width={1037}
            height={1024}
            priority
            className="h-8 w-auto flex-shrink-0"
            style={{ filter: "brightness(0) invert(1)" }}
          />
          <div className="leading-none">
            <div className="font-brand font-bold text-white text-lg tracking-[0.04em]">
              DADAŞ
            </div>
            <div className="font-brand font-bold text-gold-100 text-[8px] tracking-[0.24em] mt-0.5">
              KUYUMCULUK
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-white/90">
          <span
            className={healthy ? "text-green-300" : "text-red-300"}
            title={healthy ? "Canlı veri akıyor" : "Veri akışı kesik"}
          >
            ●
          </span>
          <Clock className="w-3 h-3" />
          <span className="tabular-nums">{formatTime(guncellendi)}</span>
        </div>
      </header>

      {/* İçerik alanı — scroll'u her sekme kendi içinde yönetir
          (Sarrafiye/Döviz pull-to-refresh, İletişim düz scroll). */}
      <main className="flex-1 overflow-hidden">
        {tab === "sarrafiye" && (
          <SarrafiyeTab rows={sarrafiye} onRefresh={refresh} />
        )}
        {tab === "doviz" && (
          <DovizTab rows={doviz} pariteler={pariteler} onRefresh={refresh} />
        )}
        {tab === "iletisim" && (
          <div className="h-full overflow-y-auto overscroll-contain">
            <IletisimTab />
          </div>
        )}
      </main>

      <MobileTabBar active={tab} onChange={setTab} />
    </div>
  );
}
