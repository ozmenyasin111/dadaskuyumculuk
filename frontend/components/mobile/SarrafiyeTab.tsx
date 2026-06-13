"use client";

import { PriceColumn } from "@/components/PriceColumn";
import type { PriceRow } from "@/lib/types";

export function SarrafiyeTab({ rows }: { rows: PriceRow[] }) {
  return (
    <div className="px-3 pt-3 pb-4">
      <PriceColumn title="Sarrafiye" rows={rows} />
    </div>
  );
}
