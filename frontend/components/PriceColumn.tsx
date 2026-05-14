import clsx from "clsx";

import { PriceCard } from "./PriceCard";
import type { PriceRow } from "@/lib/types";

export function PriceColumn({
  title,
  rows,
  hideTrend = false,
}: {
  title: string;
  rows: PriceRow[];
  hideTrend?: boolean;
}) {
  const gridCols = hideTrend
    ? "grid-cols-[minmax(0,1fr)_5rem_5rem] sm:grid-cols-[minmax(0,1fr)_7rem_7rem]"
    : "grid-cols-[minmax(0,1fr)_4.5rem_4.5rem_3rem] sm:grid-cols-[minmax(0,1fr)_7rem_7rem_5rem]";

  return (
    <section>
      <div className="px-1 mb-3 flex items-center justify-between">
        <h2 className="font-brand font-bold uppercase tracking-wider text-sm sm:text-base text-black">
          {title}
        </h2>
      </div>
      <div
        className={clsx(
          "grid gap-1.5 sm:gap-2 px-3 sm:px-4 mb-2 text-[10px] uppercase font-bold tracking-wider text-gray-500",
          gridCols,
        )}
      >
        <div>Birim</div>
        <div className="text-right">Alış</div>
        <div className="text-right">Satış</div>
        {!hideTrend && <div className="text-right hidden sm:block">Değişim</div>}
        {!hideTrend && <div className="block sm:hidden" />}
      </div>
      <div className="flex flex-col gap-2">
        {rows.map((r) => (
          <PriceCard key={r.symbol_key} row={r} hideTrend={hideTrend} />
        ))}
        {rows.length === 0 && (
          <div className="px-4 py-8 text-center text-sm text-gray-400 bg-amber-50/60 border border-amber-100 rounded-lg">
            Yükleniyor…
          </div>
        )}
      </div>
    </section>
  );
}
