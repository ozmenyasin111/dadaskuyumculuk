"use client";

import { Calculator, Info } from "lucide-react";
import { useMemo, useState } from "react";

import { usePrices } from "@/hooks/useSocket";
import { formatTR } from "@/lib/format";

// Nisap miktarı: 80.18 gr altın (klasik fıkıh ölçüsü)
const NISAP_ALTIN_GRAM = 80.18;
const ZEKAT_ORANI = 0.025; // %2.5

export default function ZekatPage() {
  const { fiyatlar } = usePrices();

  const hasAltinTL = useMemo(
    () =>
      fiyatlar.find((r) => r.symbol_key === "MADEN.ALTIN")?.alis ?? 0,
    [fiyatlar]
  );
  const gumusTL = useMemo(
    () =>
      fiyatlar.find((r) => r.symbol_key === "SARRAFIYE.GUMUSTRY")?.alis ?? 0,
    [fiyatlar]
  );

  const [altinGram, setAltinGram] = useState("");
  const [gumusGram, setGumusGram] = useState("");
  const [nakitTL, setNakitTL] = useState("");

  const altinDeger = (parseFloat(altinGram) || 0) * hasAltinTL;
  const gumusDeger = (parseFloat(gumusGram) || 0) * gumusTL;
  const nakitDeger = parseFloat(nakitTL) || 0;
  const toplam = altinDeger + gumusDeger + nakitDeger;

  const nisapTL = NISAP_ALTIN_GRAM * hasAltinTL;
  const nisapAsildiMi = toplam >= nisapTL && nisapTL > 0;
  const zekat = nisapAsildiMi ? toplam * ZEKAT_ORANI : 0;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gold-700 flex items-center gap-2">
          <Calculator className="w-6 h-6" /> Zekat Hesaplama
        </h1>
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
              Bu sayfa <b>altın, gümüş ve nakit</b> varlıklarınıza düşen zekat
              miktarını hesaplar. Hesaplamada güncel Harem Altın fiyatları
              kullanılır.
            </p>
            <p className="text-xs text-gray-700">
              Zekatı hesaplanması gereken diğer mallarınızın (ticari mallar,
              gayrimenkul gelirleri, alacak/borç durumu vb.) zekatını <b>ehil
              kişilere sorarak</b> hesaplayıp aşağıda çıkan sonuca eklemeniz
              gerekir.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-bold text-black text-lg mb-4">Varlıklarınız</h2>

          <div className="space-y-4">
            <AssetInput
              label="Altın"
              unit="gram"
              value={altinGram}
              onChange={setAltinGram}
              hint={
                hasAltinTL > 0
                  ? `Güncel: ${formatTR(hasAltinTL, 2)} TL/gr`
                  : "Fiyat yükleniyor…"
              }
              computed={altinDeger}
            />
            <AssetInput
              label="Gümüş"
              unit="gram"
              value={gumusGram}
              onChange={setGumusGram}
              hint={
                gumusTL > 0
                  ? `Güncel: ${formatTR(gumusTL, 2)} TL/gr`
                  : "Fiyat yükleniyor…"
              }
              computed={gumusDeger}
            />
            <AssetInput
              label="Nakit"
              unit="TL"
              value={nakitTL}
              onChange={setNakitTL}
              hint="TL cinsinden elinizdeki nakit"
              computed={nakitDeger}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-bold text-black text-lg mb-4">Sonuç</h2>

          <div className="space-y-3">
            <SummaryRow label="Altın değeri" value={altinDeger} />
            <SummaryRow label="Gümüş değeri" value={gumusDeger} />
            <SummaryRow label="Nakit" value={nakitDeger} />
            <div className="border-t border-gray-200 pt-3">
              <SummaryRow label="Toplam varlık" value={toplam} bold />
            </div>
            <SummaryRow
              label={`Nisap (${NISAP_ALTIN_GRAM} gr altın)`}
              value={nisapTL}
              muted
            />

            <div
              className={`mt-4 rounded-lg p-4 ${
                nisapAsildiMi
                  ? "bg-rise/10 border border-rise/30"
                  : "bg-gray-100 border border-gray-300"
              }`}
            >
              <div className="text-xs uppercase tracking-wide font-bold text-gray-600 mb-1">
                {nisapAsildiMi
                  ? "Zekât Yükümlüsünüz"
                  : "Nisap miktarının altında"}
              </div>
              <div
                className={`text-3xl font-bold tabular-nums ${
                  nisapAsildiMi ? "text-rise" : "text-gray-500"
                }`}
              >
                {formatTR(zekat, 2)} ₺
              </div>
              <div className="text-xs text-gray-600 mt-2">
                {nisapAsildiMi
                  ? "Toplam varlığınızın %2,5'i kadar zekât yükümlülüğünüz hesaplandı."
                  : "Toplam varlığınız nisap miktarına ulaşmadığı için bu varlıklar üzerinden zekât yükümlülüğünüz yoktur."}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AssetInput({
  label,
  unit,
  value,
  onChange,
  hint,
  computed,
}: {
  label: string;
  unit: string;
  value: string;
  onChange: (v: string) => void;
  hint?: string;
  computed: number;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-sm font-bold text-gray-800">{label}</label>
        <span className="text-xs text-gray-500">{hint}</span>
      </div>
      <div className="flex gap-2 items-stretch">
        <input
          type="number"
          step="any"
          min="0"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="0"
          className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none tabular-nums text-right"
        />
        <span className="flex items-center px-3 bg-gray-50 border border-gray-300 rounded text-sm text-gray-700 font-semibold">
          {unit}
        </span>
      </div>
      {computed > 0 && (
        <div className="text-xs text-gray-500 mt-1 text-right tabular-nums">
          = {formatTR(computed, 2)} ₺
        </div>
      )}
    </div>
  );
}

function SummaryRow({
  label,
  value,
  bold,
  muted,
}: {
  label: string;
  value: number;
  bold?: boolean;
  muted?: boolean;
}) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span
        className={
          muted ? "text-gray-500" : bold ? "font-bold text-black" : "text-gray-700"
        }
      >
        {label}
      </span>
      <span
        className={`tabular-nums ${
          muted ? "text-gray-500" : bold ? "font-bold text-black" : "text-gray-800"
        }`}
      >
        {formatTR(value, 2)} ₺
      </span>
    </div>
  );
}
