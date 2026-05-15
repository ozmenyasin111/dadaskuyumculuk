"use client";

import { Info } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

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

  const { tlAltin, milyemAltin, doviz } = useMemo(() => {
    const tlAltin: Margin[] = [];
    const milyemAltin: Margin[] = [];
    const doviz: Margin[] = [];
    for (const r of rows) {
      if (r.is_readonly) continue;
      if (r.category === "DOVIZ") doviz.push(r);
      else if (r.is_multiplier) milyemAltin.push(r);
      else tlAltin.push(r);
    }
    const sortBy = (a: Margin, b: Margin) => a.sort_order - b.sort_order;
    tlAltin.sort(sortBy);
    milyemAltin.sort(sortBy);
    doviz.sort(sortBy);
    return { tlAltin, milyemAltin, doviz };
  }, [rows]);

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
            <div className="font-bold text-black text-base mb-2">Önemli Not</div>
            <p className="mb-2">
              Müşteriye gösterilen fiyatlar <b>Harem Altın&apos;ın veri sağlayıcısından</b>{" "}
              çekilir ve aşağıdaki ekranda girilecek değerlere göre hesaplama
              yapılarak gösterilir. İki tür hesaplama vardır:
            </p>
            <ul className="list-disc pl-5 space-y-1 text-xs">
              <li>
                <b>Gram Altın &amp; Gümüş Kg (TL bazlı):</b> Girdiğiniz miktar Harem alışından
                <b className="text-fall"> çıkarılır</b>, satışına <b className="text-rise">eklenir</b>.
              </li>
              <li>
                <b>Diğer altınlar (milyem):</b> <b>Bizim Gram Altın fiyatımız × girdiğiniz milyem</b> ile hesaplanır.
                Gram Altın volatiliteden etkilenirse bu ürünler de <b>otomatik olarak</b> aynı korumadan faydalanır.
              </li>
              <li>
                <b>Döviz (TL bazlı):</b> Gram Altın gibi alış&apos;tan çıkarılır, satış&apos;a eklenir.
              </li>
            </ul>
            <p className="text-xs text-gray-600 mt-2">
              Örnek: Harem Gram Altın 6.800/6.840 + sizin offset -15/+40 → bizim Gram Altın 6.785/6.880.
              Yeni Çeyrek milyemleri 1.62/1.6540 → ekrana çıkar: <b className="tabular-nums">11.000 / 11.380</b>.
            </p>
          </div>
        </div>
      </div>

      <Group title="Gram Altın & Gümüş Kg (TL bazlı kâr)">
        <TableHeader mode="tl" />
        {tlAltin.map((row) => (
          <RowEditor
            key={row.id}
            row={row}
            mode="tl"
            saving={savingId === row.id}
            onChange={(patch) =>
              setRows((prev) => prev.map((r) => (r.id === row.id ? { ...r, ...patch } : r)))
            }
            onSave={() => save(row)}
          />
        ))}
      </Group>

      <Group title="Diğer Altınlar (milyem)">
        <TableHeader mode="milyem" />
        {milyemAltin.map((row) => (
          <RowEditor
            key={row.id}
            row={row}
            mode="milyem"
            saving={savingId === row.id}
            onChange={(patch) =>
              setRows((prev) => prev.map((r) => (r.id === row.id ? { ...r, ...patch } : r)))
            }
            onSave={() => save(row)}
          />
        ))}
      </Group>

      <Group title="Döviz (TL bazlı kâr)">
        <TableHeader mode="tl" />
        {doviz.map((row) => (
          <RowEditor
            key={row.id}
            row={row}
            mode="tl"
            saving={savingId === row.id}
            onChange={(patch) =>
              setRows((prev) => prev.map((r) => (r.id === row.id ? { ...r, ...patch } : r)))
            }
            onSave={() => save(row)}
          />
        ))}
      </Group>
    </div>
  );
}

function Group({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="text-sm uppercase text-gray-500 mb-2 tracking-wider font-bold">{title}</h2>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">{children}</div>
    </section>
  );
}

function TableHeader({ mode }: { mode: "tl" | "milyem" }) {
  return (
    <div className="hidden sm:grid sm:grid-cols-12 sm:gap-2 bg-gray-50 px-4 py-2 text-xs uppercase font-bold text-gray-500">
      <div className="col-span-5">Ürün</div>
      <div className="col-span-3 text-right">
        {mode === "tl" ? "Alıştan çıkarılacak" : "Alış Milyemi"}
      </div>
      <div className="col-span-3 text-right">
        {mode === "tl" ? "Satışa eklenecek" : "Satış Milyemi"}
      </div>
      <div className="col-span-1 text-right">Kaydet</div>
    </div>
  );
}

function RowEditor({
  row,
  mode,
  saving,
  onChange,
  onSave,
}: {
  row: Margin;
  mode: "tl" | "milyem";
  saving: boolean;
  onChange: (p: Partial<Margin>) => void;
  onSave: () => void;
}) {
  return (
    <div className="flex flex-col gap-2 sm:grid sm:grid-cols-12 sm:gap-2 sm:items-center px-4 py-3 border-b border-gray-100">
      <div className="sm:col-span-5 text-gray-800 font-semibold">{row.display_name}</div>
      <div className="grid grid-cols-2 gap-2 sm:contents">
        <div className="sm:col-span-3">
          <span className="block sm:hidden text-[10px] uppercase font-bold text-gray-500 mb-1">
            {mode === "tl" ? "Alıştan çıkarılacak" : "Alış Milyemi"}
          </span>
          {mode === "tl" ? (
            <PrefixInput
              prefix="−"
              prefixColor="text-fall"
              value={absValue(row.alis_offset)}
              onChange={(v) => onChange({ alis_offset: negative(v) })}
            />
          ) : (
            <PlainInput
              value={row.alis_offset}
              onChange={(v) => onChange({ alis_offset: v })}
            />
          )}
        </div>
        <div className="sm:col-span-3">
          <span className="block sm:hidden text-[10px] uppercase font-bold text-gray-500 mb-1">
            {mode === "tl" ? "Satışa eklenecek" : "Satış Milyemi"}
          </span>
          {mode === "tl" ? (
            <PrefixInput
              prefix="+"
              prefixColor="text-rise"
              value={absValue(row.satis_offset)}
              onChange={(v) => onChange({ satis_offset: positive(v) })}
            />
          ) : (
            <PlainInput
              value={row.satis_offset}
              onChange={(v) => onChange({ satis_offset: v })}
            />
          )}
        </div>
      </div>
      <div className="sm:col-span-1 sm:text-right">
        <button
          onClick={onSave}
          disabled={saving}
          className="w-full sm:w-auto px-3 py-2 sm:py-1.5 bg-gold-500 hover:bg-gold-600 text-white text-xs rounded font-bold transition-colors disabled:opacity-50"
        >
          {saving ? "…" : "Kaydet"}
        </button>
      </div>
    </div>
  );
}

function PrefixInput({
  prefix,
  prefixColor,
  value,
  onChange,
}: {
  prefix: string;
  prefixColor: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="relative">
      <span
        className={`absolute left-2 top-1/2 -translate-y-1/2 font-bold pointer-events-none ${prefixColor}`}
      >
        {prefix}
      </span>
      <input
        type="number"
        step="any"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full pl-6 pr-2 py-1.5 text-right tabular-nums border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none"
      />
    </div>
  );
}

function PlainInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <input
      type="number"
      step="any"
      min="0"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-2 py-1.5 text-right tabular-nums border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none"
    />
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
