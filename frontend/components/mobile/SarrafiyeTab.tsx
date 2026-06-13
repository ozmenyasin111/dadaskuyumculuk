"use client";

import { PriceColumn } from "@/components/PriceColumn";
import type { PriceRow } from "@/lib/types";

import { PullToRefresh } from "./PullToRefresh";

export function SarrafiyeTab({
  rows,
  onRefresh,
}: {
  rows: PriceRow[];
  onRefresh: () => Promise<void>;
}) {
  return (
    <PullToRefresh onRefresh={onRefresh}>
      <div className="px-3 pt-3 pb-4">
        <PriceColumn title="Sarrafiye" rows={rows} />
      </div>
    </PullToRefresh>
  );
}
