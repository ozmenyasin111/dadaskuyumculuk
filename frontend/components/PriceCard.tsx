"use client";

import clsx from "clsx";
import { ArrowDown, ArrowUp } from "lucide-react";

import { autoFractionDigits, formatTR } from "@/lib/format";
import type { PriceRow } from "@/lib/types";

export function PriceCard({ row }: { row: PriceRow }) {
  return (
    <div
      className={clsx(
        "grid items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 sm:py-2.5",
        "grid-cols-[minmax(0,1fr)_5.5rem_5.5rem_1.25rem] sm:grid-cols-[minmax(0,1fr)_11rem_11rem_1.75rem]",
        "bg-amber-50/60 border border-amber-100 rounded-lg shadow-[0_1px_2px_rgba(184,155,94,0.08)]",
        "transition-all duration-300 ease-soft",
        "hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(184,155,94,0.25)] hover:border-gold-300 hover:bg-amber-50",
        row.using_volatility && "bg-amber-100 border-amber-400",
      )}
      title={row.using_volatility ? "Yüksek fark — sistem override aktif" : undefined}
    >
      <div
        className="font-bold text-black uppercase truncate text-base sm:text-2xl"
        lang="tr"
      >
        {row.display_name}
      </div>
      <div className="text-right tabular-nums font-bold whitespace-nowrap text-base sm:text-2xl pr-3 sm:pr-10 text-blue-700">
        {formatTR(row.alis, autoFractionDigits(row.alis))}
      </div>
      <div className="text-right tabular-nums font-bold whitespace-nowrap text-base sm:text-2xl text-rise">
        {formatTR(row.satis, autoFractionDigits(row.satis))}
      </div>
      <TrendArrow trend={row.trend} />
    </div>
  );
}

function TrendArrow({ trend }: { trend: "up" | "down" | "flat" }) {
  if (trend === "up") {
    return (
      <ArrowUp
        className="w-4 h-4 sm:w-5 sm:h-5 text-rise justify-self-center"
        strokeWidth={3}
      />
    );
  }
  if (trend === "down") {
    return (
      <ArrowDown
        className="w-4 h-4 sm:w-5 sm:h-5 text-fall justify-self-center"
        strokeWidth={3}
      />
    );
  }
  return (
    <span className="text-gray-300 text-base sm:text-xl font-bold justify-self-center">
      —
    </span>
  );
}
