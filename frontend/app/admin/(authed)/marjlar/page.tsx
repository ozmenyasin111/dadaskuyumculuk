"use client";

import { Info } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { Margin } from "@/lib/types";

export default function MarjlarPage() {
  const [rows, setRows] = useState<Margin[]>([]);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [flash, setFlash] = useState<string | null>(null);

  useEffect(() => {
    api<Margin[]>("/api/admin/margins").then(setRows);
  }, []);

  async function save(row: Margin) {
    setSavingId(row.id);
    try {
      const updated = await api<Margin>(`/api/admin/margins/${row.id}`, {
        method: "PUT",
        body: JSON.stringify({
          alis_offset: row.alis_offset,
          satis_offset: row.satis_offset,
        }),
      });
      setRows((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
      setFlash(`${updated.display_name} güncellendi`);
      setTimeout(() => setFlash(null), 2000);
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "hata");
    } finally {
      setSavingId(null);
    }
  }

  const groups = group(rows);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gold-700">Kâr Marjları</h1>
        {flash && <span className="text-sm text-rise">{flash}</span>}
      </div>

      <div className="bg-amber-50 border-l-4 border-gold-500 rounded-lg p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-gold-500 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
            <Info className="w-4 h-4" />
          </div>
          <div className="text-sm text-gray-800 leading-relaxed">
            <div className="font-bold text-black text-base mb-2">
              Önemli Not
            </div>
            <p className="mb-2">
              Müşteriye gösterilen fiyatlar <b>Harem Altın</b>&apos;dan canlı olarak çekilir.
              Aşağıda her ürün için girdiğiniz değerler, Harem Altın fiyatlarının
              üzerine otomatik olarak uygulanır. Piyasa aniden hareketlenirse bu
              değerler <b>geçici olarak geçersiz olur</b> ve <b>Volatilite</b> ekranındaki
              güvenli değerler devreye girer.
            </p>
            <ul className="list-disc pl-5 space-y-1 mb-2">
              <li>
                <b className="text-fall">Alış kutusu</b>: Harem Altın alış fiyatından
                <b> bu miktar çıkarılır</b> (otomatik − işareti).
              </li>
              <li>
                <b className="text-rise">Satış kutusu</b>: Harem Altın satış fiyatına
                <b> bu miktar eklenir</b> (otomatik + işareti).
              </li>
            </ul>
            <p className="text-xs text-gray-600">
              Örnek: Harem Altın&apos;da Has Altın alış 6.800 / satış 6.840 ise;
              alış kutusuna 20, satış kutusuna 20 yazarsanız müşteri ekranında
              <b className="tabular-nums"> 6.780 / 6.860</b> görür.
            </p>
          </div>
        </div>
      </div>

      {Object.entries(groups).map(([category, items]) => (
        <section key={category} className="mb-8">
          <h2 className="text-sm uppercase text-gray-500 mb-2 tracking-wider font-bold">
            {labelFor(category)}
          </h2>
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="grid grid-cols-12 gap-2 bg-gray-50 px-4 py-2 text-xs uppercase font-bold text-gray-500">
              <div className="col-span-5">Ürün</div>
              <div className="col-span-3 text-right">Alıştan çıkarılacak</div>
              <div className="col-span-3 text-right">Satışa eklenecek</div>
              <div className="col-span-1 text-right">Kaydet</div>
            </div>
            {items.map((row) => (
              <MarginRow
                key={row.id}
                row={row}
                saving={savingId === row.id}
                onChange={(patch) =>
                  setRows((prev) =>
                    prev.map((r) => (r.id === row.id ? { ...r, ...patch } : r))
                  )
                }
                onSave={() => save(row)}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function group(rows: Margin[]): Record<string, Margin[]> {
  const g: Record<string, Margin[]> = {};
  for (const r of rows) {
    if (r.is_readonly) continue;
    (g[r.category] ||= []).push(r);
  }
  for (const k of Object.keys(g)) g[k].sort((a, b) => a.sort_order - b.sort_order);
  return g;
}

function labelFor(cat: string): string {
  if (cat === "ALTIN") return "Sarrafiye & Gram Altın";
  if (cat === "DOVIZ") return "Döviz";
  return cat;
}

function MarginRow({
  row,
  saving,
  onChange,
  onSave,
}: {
  row: Margin;
  saving: boolean;
  onChange: (p: Partial<Margin>) => void;
  onSave: () => void;
}) {
  return (
    <div className="grid grid-cols-12 gap-2 items-center px-4 py-2.5 border-b border-gray-100">
      <div className="col-span-5 text-gray-800 font-semibold">{row.display_name}</div>
      <div className="col-span-3">
        <div className="relative">
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-fall font-bold pointer-events-none">
            −
          </span>
          <input
            type="number"
            step="any"
            value={absValue(row.alis_offset)}
            onChange={(e) =>
              onChange({ alis_offset: negative(e.target.value) })
            }
            className="w-full pl-6 pr-2 py-1.5 text-right tabular-nums border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none"
          />
        </div>
      </div>
      <div className="col-span-3">
        <div className="relative">
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-rise font-bold pointer-events-none">
            +
          </span>
          <input
            type="number"
            step="any"
            value={absValue(row.satis_offset)}
            onChange={(e) =>
              onChange({ satis_offset: positive(e.target.value) })
            }
            className="w-full pl-6 pr-2 py-1.5 text-right tabular-nums border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none"
          />
        </div>
      </div>
      <div className="col-span-1 text-right">
        <button
          onClick={onSave}
          disabled={saving}
          className="px-3 py-1.5 bg-gold-500 hover:bg-gold-600 text-white text-xs rounded font-bold transition-colors disabled:opacity-50"
        >
          {saving ? "…" : "Kaydet"}
        </button>
      </div>
    </div>
  );
}

function absValue(v: string): string {
  const n = parseFloat(v);
  if (Number.isNaN(n)) return "";
  return Math.abs(n).toString();
}

function negative(s: string): string {
  const n = parseFloat(s);
  if (Number.isNaN(n)) return "0";
  return (-Math.abs(n)).toString();
}

function positive(s: string): string {
  const n = parseFloat(s);
  if (Number.isNaN(n)) return "0";
  return Math.abs(n).toString();
}
