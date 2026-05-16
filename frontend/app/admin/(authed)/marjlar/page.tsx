"use client";

import { Check, Info } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api } from "@/lib/api";
import type { Margin, PricingMode } from "@/lib/types";

export default function MarjlarPage() {
  const [rows, setRows] = useState<Margin[]>([]);
  const [pricingMode, setPricingMode] = useState<PricingMode>("milyem");
  const [activeTab, setActiveTab] = useState<PricingMode>("milyem");
  const [savingId, setSavingId] = useState<number | null>(null);
  const [modeBusy, setModeBusy] = useState(false);
  const [flash, setFlash] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api<Margin[]>("/api/admin/margins"),
      api<{ mode: PricingMode }>("/api/admin/pricing-mode"),
    ]).then(([margins, cfg]) => {
      setRows(margins);
      setPricingMode(cfg.mode);
      setActiveTab(cfg.mode);
    });
  }, []);

  async function saveRow(row: Margin) {
    setSavingId(row.id);
    try {
      const updated = await api<Margin>(`/api/admin/margins/${row.id}`, {
        method: "PUT",
        body: JSON.stringify({
          alis_offset: row.alis_offset,
          satis_offset: row.satis_offset,
          classic_alis_offset: row.classic_alis_offset,
          classic_satis_offset: row.classic_satis_offset,
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

  async function activateMode(mode: PricingMode) {
    setModeBusy(true);
    try {
      await api<{ mode: PricingMode }>("/api/admin/pricing-mode", {
        method: "PUT",
        body: JSON.stringify({ mode }),
      });
      setPricingMode(mode);
      setFlash(
        mode === "milyem"
          ? "Milyem Hesabı aktif edildi"
          : "Fiyat Ekle/Çıkar aktif edildi",
      );
      setTimeout(() => setFlash(null), 2200);
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "hata");
    } finally {
      setModeBusy(false);
    }
  }

  const { tlAltin, multiplierAltin, doviz } = useMemo(() => {
    const tlAltin: Margin[] = [];
    const multiplierAltin: Margin[] = [];
    const doviz: Margin[] = [];
    for (const r of rows) {
      if (r.is_readonly) continue;
      if (r.category === "DOVIZ") doviz.push(r);
      else if (r.is_multiplier) multiplierAltin.push(r);
      else tlAltin.push(r);
    }
    const sortBy = (a: Margin, b: Margin) => a.sort_order - b.sort_order;
    tlAltin.sort(sortBy);
    multiplierAltin.sort(sortBy);
    doviz.sort(sortBy);
    return { tlAltin, multiplierAltin, doviz };
  }, [rows]);

  return (
    <div>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h1 className="text-2xl font-bold text-gold-700">Kâr Marjları</h1>
        {flash && <span className="text-sm text-rise">{flash}</span>}
      </div>

      <TabBar
        active={activeTab}
        current={pricingMode}
        onSelect={setActiveTab}
        onActivate={activateMode}
        busy={modeBusy}
      />

      <div className="bg-amber-50 border-l-4 border-gold-500 rounded-lg p-4 sm:p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-gold-500 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
            <Info className="w-4 h-4" />
          </div>
          <div className="text-sm text-gray-800 leading-relaxed">
            <div className="font-bold text-black text-base mb-2">
              {activeTab === "milyem" ? "Milyem Hesabı" : "Fiyat Ekle/Çıkar (TL)"}
            </div>
            {activeTab === "milyem" ? (
              <p className="text-xs">
                Diğer altın ürünleri <b>Gram Altın fiyatımız × girdiğiniz milyem</b> ile
                hesaplanır. Gram Altın volatiliteden etkilenirse bu ürünler de{" "}
                <b>otomatik</b> aynı korumadan faydalanır.
              </p>
            ) : (
              <p className="text-xs">
                Her altın ürünü için Harem&apos;den gelen kendi alış/satış değerine{" "}
                <b className="text-fall">alıştan çıkarılacak</b> ve{" "}
                <b className="text-rise">satışa eklenecek</b> TL miktarı eklenir.
                Milyem hesabı kullanılmaz.
              </p>
            )}
          </div>
        </div>
      </div>

      <Group title="Diğer Altınlar">
        <TableHeader mode={activeTab === "milyem" ? "milyem" : "tl"} />
        {multiplierAltin.map((row) => (
          <RowEditor
            key={`${activeTab}-${row.id}`}
            row={row}
            mode={activeTab === "milyem" ? "milyem" : "tl-classic"}
            saving={savingId === row.id}
            onChange={(patch) =>
              setRows((prev) =>
                prev.map((r) => (r.id === row.id ? { ...r, ...patch } : r)),
              )
            }
            onSave={() => saveRow(row)}
          />
        ))}
      </Group>

      <Group title="Gram Altın & Gümüş Kg (TL bazlı kâr)">
        <TableHeader mode="tl" />
        {tlAltin.map((row) => (
          <RowEditor
            key={row.id}
            row={row}
            mode="tl"
            saving={savingId === row.id}
            onChange={(patch) =>
              setRows((prev) =>
                prev.map((r) => (r.id === row.id ? { ...r, ...patch } : r)),
              )
            }
            onSave={() => saveRow(row)}
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
              setRows((prev) =>
                prev.map((r) => (r.id === row.id ? { ...r, ...patch } : r)),
              )
            }
            onSave={() => saveRow(row)}
          />
        ))}
      </Group>
    </div>
  );
}

function TabBar({
  active,
  current,
  onSelect,
  onActivate,
  busy,
}: {
  active: PricingMode;
  current: PricingMode;
  onSelect: (m: PricingMode) => void;
  onActivate: (m: PricingMode) => void;
  busy: boolean;
}) {
  return (
    <div className="mb-4">
      <div className="flex gap-2 mb-2 flex-wrap">
        <TabButton
          label="Milyem Hesabı"
          active={active === "milyem"}
          current={current === "milyem"}
          onClick={() => onSelect("milyem")}
        />
        <TabButton
          label="Fiyat Ekle/Çıkar"
          active={active === "classic"}
          current={current === "classic"}
          onClick={() => onSelect("classic")}
        />
      </div>
      {active !== current && (
        <button
          onClick={() => onActivate(active)}
          disabled={busy}
          className="text-xs bg-gold-500 hover:bg-gold-600 text-white font-bold rounded px-3 py-1.5 disabled:opacity-50"
        >
          {busy ? "…" : "Bu sistemi aktif et"}
        </button>
      )}
    </div>
  );
}

function TabButton({
  label,
  active,
  current,
  onClick,
}: {
  label: string;
  active: boolean;
  current: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors border ${
        active
          ? "bg-gold-500 text-white border-gold-500 shadow-sm"
          : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
      }`}
    >
      {label}
      {current && (
        <span className="ml-2 inline-flex items-center gap-1 bg-rise/10 text-rise text-[10px] uppercase font-bold rounded px-1.5 py-0.5">
          <Check className="w-3 h-3" strokeWidth={3} /> Aktif
        </span>
      )}
    </button>
  );
}

function Group({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="text-sm uppercase text-gray-500 mb-2 tracking-wider font-bold">
        {title}
      </h2>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {children}
      </div>
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
  mode: "tl" | "milyem" | "tl-classic";
  saving: boolean;
  onChange: (p: Partial<Margin>) => void;
  onSave: () => void;
}) {
  const isTL = mode === "tl" || mode === "tl-classic";
  const isClassic = mode === "tl-classic";
  const alisVal = isClassic ? row.classic_alis_offset : row.alis_offset;
  const satisVal = isClassic ? row.classic_satis_offset : row.satis_offset;
  const setAlis = (v: string) =>
    onChange(
      isClassic ? { classic_alis_offset: v } : { alis_offset: v },
    );
  const setSatis = (v: string) =>
    onChange(
      isClassic ? { classic_satis_offset: v } : { satis_offset: v },
    );

  return (
    <div className="flex flex-col gap-2 sm:grid sm:grid-cols-12 sm:gap-2 sm:items-center px-4 py-3 border-b border-gray-100">
      <div className="sm:col-span-5 text-gray-800 font-semibold">{row.display_name}</div>
      <div className="grid grid-cols-2 gap-2 sm:contents">
        <div className="sm:col-span-3">
          <span className="block sm:hidden text-[10px] uppercase font-bold text-gray-500 mb-1">
            {isTL ? "Alıştan çıkarılacak" : "Alış Milyemi"}
          </span>
          {isTL ? (
            <PrefixInput
              prefix="−"
              prefixColor="text-fall"
              value={absValue(alisVal)}
              onChange={(v) => setAlis(negative(v))}
            />
          ) : (
            <PlainInput value={alisVal} onChange={setAlis} />
          )}
        </div>
        <div className="sm:col-span-3">
          <span className="block sm:hidden text-[10px] uppercase font-bold text-gray-500 mb-1">
            {isTL ? "Satışa eklenecek" : "Satış Milyemi"}
          </span>
          {isTL ? (
            <PrefixInput
              prefix="+"
              prefixColor="text-rise"
              value={absValue(satisVal)}
              onChange={(v) => setSatis(positive(v))}
            />
          ) : (
            <PlainInput value={satisVal} onChange={setSatis} />
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
