"use client";

import clsx from "clsx";
import { ArrowDown, ArrowUp } from "lucide-react";

import { autoFractionDigits, formatPct, formatTR } from "@/lib/format";
import type { Parite } from "@/lib/types";

export function ParitelerSection({ pariteler }: { pariteler: Parite[] }) {
  return (
    <div>
      <div className="px-1 mb-3">
        <h2 className="font-brand font-bold uppercase tracking-wider text-base text-black">
          Pariteler
        </h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {pariteler.map((p) => (
          <div
            key={p.symbol}
            className="grid grid-cols-[minmax(0,1fr)_4.5rem_4.5rem_4.5rem] gap-2 items-center px-4 py-3 bg-amber-50/60 border border-amber-100 rounded-lg shadow-[0_1px_2px_rgba(184,155,94,0.08)] transition-all duration-300 ease-soft hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(184,155,94,0.25)] hover:border-gold-300 hover:bg-amber-50"
          >
            <div className="font-bold text-black uppercase truncate" lang="tr">
              {p.symbol}
            </div>
            <div
              className={clsx(
                "text-right tabular-nums font-bold whitespace-nowrap",
                p.trend === "up" && "text-rise",
                p.trend === "down" && "text-fall",
                p.trend === "flat" && "text-black",
              )}
            >
              {formatTR(p.bid, autoFractionDigits(p.bid))}
            </div>
            <div
              className={clsx(
                "text-right tabular-nums font-bold whitespace-nowrap",
                p.trend === "up" && "text-rise",
                p.trend === "down" && "text-fall",
                p.trend === "flat" && "text-black",
              )}
            >
              {formatTR(p.ask, autoFractionDigits(p.ask))}
            </div>
            <div
              className={clsx(
                "flex items-center justify-end gap-1 text-sm font-bold whitespace-nowrap",
                p.trend === "up" && "text-rise",
                p.trend === "down" && "text-fall",
                p.trend === "flat" && "text-gray-400",
              )}
            >
              {p.trend === "up" && <ArrowUp className="w-4 h-4" strokeWidth={3} />}
              {p.trend === "down" && <ArrowDown className="w-4 h-4" strokeWidth={3} />}
              <span className="tabular-nums">
                {p.trend === "flat" ? "—" : formatPct(p.pct_change)}
              </span>
            </div>
          </div>
        ))}
        {pariteler.length === 0 && (
          <div className="col-span-full px-4 py-6 text-center text-sm text-gray-400 bg-amber-50/60 border border-amber-100 rounded-lg">
            Yükleniyor…
          </div>
        )}
      </div>
    </div>
  );
}
