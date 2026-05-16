"use client";

import clsx from "clsx";

import { autoFractionDigits, formatTR } from "@/lib/format";
import type { Parite } from "@/lib/types";

export function ParitelerSection({ pariteler }: { pariteler: Parite[] }) {
  return (
    <section>
      <div className="px-1 mb-3 flex items-center justify-between">
        <h2 className="font-brand font-bold uppercase tracking-wider text-base sm:text-lg text-black">
          Pariteler
        </h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {pariteler.map((p) => (
          <ParityCard key={p.symbol} parite={p} />
        ))}
        {pariteler.length === 0 && (
          <div className="col-span-full px-4 py-6 text-center text-sm text-gray-400 bg-amber-50/60 border border-amber-100 rounded-lg">
            Yükleniyor…
          </div>
        )}
      </div>
    </section>
  );
}

function ParityCard({ parite: p }: { parite: Parite }) {
  return (
    <div
      className={clsx(
        "grid items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 sm:py-2.5",
        "grid-cols-[minmax(0,1fr)_5.5rem_5.5rem] sm:grid-cols-[minmax(0,1fr)_7rem_7rem]",
        "bg-amber-50/60 border border-amber-100 rounded-lg shadow-[0_1px_2px_rgba(184,155,94,0.08)]",
        "transition-all duration-300 ease-soft",
        "hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(184,155,94,0.25)] hover:border-gold-300 hover:bg-amber-50",
      )}
    >
      <div className="font-bold text-black uppercase truncate text-base sm:text-2xl" lang="tr">
        {p.symbol}
      </div>
      <div className="text-right tabular-nums font-bold whitespace-nowrap text-base sm:text-2xl pr-3 sm:pr-6 text-blue-700">
        {formatTR(p.bid, autoFractionDigits(p.bid))}
      </div>
      <div className="text-right tabular-nums font-bold whitespace-nowrap text-base sm:text-2xl text-rise">
        {formatTR(p.ask, autoFractionDigits(p.ask))}
      </div>
    </div>
  );
}
