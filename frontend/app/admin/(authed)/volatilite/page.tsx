"use client";

import { AlertTriangle } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { Volatility } from "@/lib/types";

export default function VolatilitePage() {
  const [rows, setRows] = useState<Volatility[]>([]);
  const [savingCat, setSavingCat] = useState<string | null>(null);
  const [flash, setFlash] = useState<string | null>(null);

  useEffect(() => {
    api<Volatility[]>("/api/admin/volatility").then(setRows);
  }, []);

  async function save(row: Volatility) {
    setSavingCat(row.category);
    try {
      const updated = await api<Volatility>(
        `/api/admin/volatility/${row.category}`,
        {
          method: "PUT",
          body: JSON.stringify({
            threshold: row.threshold,
            alis_override: row.alis_override,
            satis_override: row.satis_override,
            enabled: row.enabled,
          }),
        }
      );
      setRows((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
      setFlash(`${labelFor(updated.category)} güncellendi`);
      setTimeout(() => setFlash(null), 2000);
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "hata");
    } finally {
      setSavingCat(null);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gold-700">
          Volatilite{" "}
          <span className="text-gray-500 font-semibold text-lg">
            (Piyasa Sarsıntısı)
          </span>
        </h1>
        {flash && <span className="text-sm text-rise">{flash}</span>}
      </div>

      <div className="bg-amber-50 border-l-4 border-gold-500 rounded-lg p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-gold-500 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="text-sm text-gray-800 leading-relaxed">
            <div className="font-bold text-black text-base mb-2">
              Bu ekran ne işe yarar?
            </div>
            <p className="mb-2">
              Piyasa aniden hareketlenirse Harem Altın&apos;ın alış-satış makası
              geniş açılır. Bu durumda <b>Kâr Marjları</b> ekranında Has Altın
              için girdiğiniz değerler <b>geçici olarak geçersiz olur</b> ve{" "}
              <b>bu sayfada girdiğiniz değerler aktif olur</b>. Diğer altın
              ürünleri Has Altın fiyatımız × milyem ile hesaplandığı için
              <b> bütün altın fiyatlarınız otomatik olarak</b> bu güvenli
              değerlerle güncellenir; ayrıca tek tek düzeltmeniz gerekmez. Bu
              sistem işletmenizi anlık fiyat değişimlerinde zarar etmekten korur.
            </p>
            <p className="mb-1 font-semibold">Her alanın anlamı:</p>
            <ul className="list-disc pl-5 space-y-1 text-xs">
              <li>
                <b>Eşik (fark):</b> Harem Altın&apos;da alış-satış farkı bu
                değeri geçince güvenli mod devreye girer.
              </li>
              <li>
                <b className="text-fall">Alış (−):</b> Mod devredeyken Harem
                Altın alış fiyatından bu kadar çıkarılır.
              </li>
              <li>
                <b className="text-rise">Satış (+):</b> Mod devredeyken Harem
                Altın satış fiyatına bu kadar eklenir.
              </li>
              <li>
                <b>Aktif/Kapalı:</b> Bu güvenlik mekanizmasını tamamen kapatmak
                isterseniz.
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {rows.map((row) => (
          <div
            key={row.id}
            className="bg-white rounded-lg border border-gray-200 p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-black text-lg">
                {labelFor(row.category)}
              </h2>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={row.enabled}
                  onChange={(e) =>
                    setRows((prev) =>
                      prev.map((r) =>
                        r.id === row.id ? { ...r, enabled: e.target.checked } : r
                      )
                    )
                  }
                  className="accent-gold-500 w-4 h-4"
                />
                <span className="text-sm font-semibold text-gray-700">
                  {row.enabled ? "Aktif" : "Kapalı"}
                </span>
              </label>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <NumField
                label="Eşik (fark)"
                value={row.threshold}
                onChange={(v) =>
                  setRows((prev) =>
                    prev.map((r) =>
                      r.id === row.id ? { ...r, threshold: v } : r
                    )
                  )
                }
              />
              <NumField
                label="Alış (−)"
                value={row.alis_override}
                onChange={(v) =>
                  setRows((prev) =>
                    prev.map((r) =>
                      r.id === row.id ? { ...r, alis_override: v } : r
                    )
                  )
                }
                hint="Negatif değer girin (ör. -200)"
              />
              <NumField
                label="Satış (+)"
                value={row.satis_override}
                onChange={(v) =>
                  setRows((prev) =>
                    prev.map((r) =>
                      r.id === row.id ? { ...r, satis_override: v } : r
                    )
                  )
                }
                hint="Pozitif değer girin (ör. 300)"
              />
            </div>
            <div className="mt-4 text-right">
              <button
                onClick={() => save(row)}
                disabled={savingCat === row.category}
                className="px-4 py-2 bg-gold-500 hover:bg-gold-600 text-white rounded font-bold transition-colors disabled:opacity-50"
              >
                {savingCat === row.category ? "Kaydediliyor…" : "Kaydet"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function labelFor(cat: string): string {
  if (cat === "ALTIN") return "Has Altın";
  if (cat === "DOVIZ") return "Döviz";
  return cat;
}

function NumField({
  label,
  value,
  onChange,
  hint,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  hint?: string;
}) {
  return (
    <label className="block">
      <span className="text-xs font-bold text-gray-700 mb-1 block">{label}</span>
      <input
        type="number"
        step="any"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none tabular-nums"
      />
      {hint && <span className="text-[10px] text-gray-400">{hint}</span>}
    </label>
  );
}
