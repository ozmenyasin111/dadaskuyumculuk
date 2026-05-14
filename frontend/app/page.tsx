"use client";

import { useMemo } from "react";
import { Clock } from "lucide-react";

import { AvantajlarSection } from "@/components/AvantajlarSection";
import { FooterSection } from "@/components/FooterSection";
import { HakkimizdaSection } from "@/components/HakkimizdaSection";
import { ParitelerSection } from "@/components/ParitelerSection";
import { PriceColumn } from "@/components/PriceColumn";
import { PriceNotice } from "@/components/PriceNotice";
import { TopBar } from "@/components/TopBar";
import { usePrices } from "@/hooks/useSocket";
import { formatTime } from "@/lib/format";
import type { PriceRow } from "@/lib/types";

export default function HomePage() {
  const { fiyatlar, pariteler, guncellendi, healthy } = usePrices();

  const { sol, sag, ro } = useMemo(() => {
    const sol: PriceRow[] = [];
    const sag: PriceRow[] = [];
    const ro: PriceRow[] = [];
    for (const r of fiyatlar) {
      if (r.category === "ALTIN") sol.push(r);
      else if (r.category === "DOVIZ") sag.push(r);
      else if (r.category === "READONLY") ro.push(r);
    }
    return { sol, sag, ro };
  }, [fiyatlar]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <TopBar />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PriceColumn title="Sarrafiye & Gram Altın" rows={sol} />
          <div className="flex flex-col gap-6">
            <PriceColumn title="Döviz" rows={sag} />
            <PriceColumn title="Kuyumcu Paneli" rows={ro} />
          </div>
        </div>

        <div className="mt-4 flex items-center justify-end gap-2 text-xs text-gray-500">
          <span
            className={healthy ? "text-rise" : "text-fall"}
            title={healthy ? "Canlı veri akıyor" : "Veri akışı kesik"}
          >
            ●
          </span>
          <Clock className="w-3 h-3" />
          <span className="tabular-nums">{formatTime(guncellendi)}</span>
        </div>

        <section id="pariteler" className="scroll-mt-24 mt-12">
          <ParitelerSection pariteler={pariteler} />
        </section>

        <section className="mt-12">
          <AvantajlarSection />
        </section>

        <section id="hakkimizda" className="scroll-mt-24 mt-12 mb-12">
          <HakkimizdaSection />
        </section>
      </main>
      <FooterSection />
      <PriceNotice />
    </div>
  );
}
