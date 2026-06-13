"use client";

import { ParitelerSection } from "@/components/ParitelerSection";
import { PriceColumn } from "@/components/PriceColumn";
import type { Parite, PriceRow } from "@/lib/types";

import { PullToRefresh } from "./PullToRefresh";

export function DovizTab({
  rows,
  pariteler,
  onRefresh,
}: {
  rows: PriceRow[];
  pariteler: Parite[];
  onRefresh: () => Promise<void>;
}) {
  return (
    <PullToRefresh onRefresh={onRefresh}>
      <div className="px-3 pt-3 pb-4 flex flex-col gap-8">
        <PriceColumn title="Döviz" rows={rows} />
        <ParitelerSection pariteler={pariteler} />
      </div>
    </PullToRefresh>
  );
}
