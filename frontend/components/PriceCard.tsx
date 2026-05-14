"use client";

import clsx from "clsx";
import { ArrowDown, ArrowUp } from "lucide-react";

import { autoFractionDigits, formatPct, formatTR } from "@/lib/format";
import type { PriceRow } from "@/lib/types";

export function PriceCard({
  row,
  hideTrend = false,
}: {
  row: PriceRow;
  hideTrend?: boolean;
}) {
  const gridCols = hideTrend
    ? "grid-cols-[minmax(0,1fr)_7rem_7rem]"
    : "grid-cols-[minmax(0,1fr)_7rem_7rem_5rem]";

  return (
    <div
      className={clsx(
        "grid items-center gap-2 px-4 py-3",
        "bg-amber-50/60 border border-amber-100 rounded-lg shadow-[0_1px_2px_rgba(184,155,94,0.08)]",
        "transition-all duration-300 ease-soft",
        "hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(184,155,94,0.25)] hover:border-gold-300 hover:bg-amber-50",
        row.using_volatility && "bg-amber-100 border-amber-400",
        gridCols,
      )}
      title={row.using_volatility ? "Yüksek fark — sistem override aktif" : undefined}
    >
      <div className="font-bold text-black uppercase truncate" lang="tr">
        {row.display_name}
      </div>
      <div
        className={clsx(
          "text-right tabular-nums font-bold whitespace-nowrap",
          row.trend === "up" && "text-rise",
          row.trend === "down" && "text-fall",
          row.trend === "flat" && "text-black",
        )}
      >
        {formatTR(row.alis, autoFractionDigits(row.alis))}
      </div>
      <div
        className={clsx(
          "text-right tabular-nums font-bold whitespace-nowrap",
          row.trend === "up" && "text-rise",
          row.trend === "down" && "text-fall",
          row.trend === "flat" && "text-black",
        )}
      >
        {formatTR(row.satis, autoFractionDigits(row.satis))}
      </div>
      {!hideTrend && (
        <div
          className={clsx(
            "flex items-center justify-end gap-1 text-xs font-bold whitespace-nowrap",
            row.trend === "up" && "text-rise",
            row.trend === "down" && "text-fall",
            row.trend === "flat" && "text-gray-400",
          )}
        >
          {row.trend === "up" && <ArrowUp className="w-3.5 h-3.5" strokeWidth={3} />}
          {row.trend === "down" && <ArrowDown className="w-3.5 h-3.5" strokeWidth={3} />}
          <span className="tabular-nums">
            {row.trend === "flat" ? "—" : formatPct(row.pct_change)}
          </span>
        </div>
      )}
    </div>
  );
}
