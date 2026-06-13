"use client";

import Image from "next/image";
import { Instagram, MapPin, Phone } from "lucide-react";

// Web ile aynı değerler (TopBar / FooterSection / HakkimizdaSection'dan).
const PHONE_DISPLAY = "0212 557 25 25";
const PHONE_TEL = "tel:02125572525";
const MAP_URL = "https://share.google/aYsPNr2zozwmhwt2O";
const INSTAGRAM_URL = "https://www.instagram.com/dadaskuyumculuk/";
// Metinsel açık adres istenirse buraya yazılır; şimdilik harita linki kullanılıyor.
const ADDRESS_TEXT = "";

export function IletisimTab() {
  return (
    <div className="px-5 pt-8 pb-6 flex flex-col items-center text-center">
      <Image
        src="/logo-figure.png"
        alt="Dadaş Kuyumculuk"
        width={1037}
        height={1024}
        priority
        className="h-28 w-auto"
      />
      <div className="mt-4 leading-none">
        <div className="font-brand font-bold text-black text-3xl tracking-[0.04em]">
          DADAŞ
        </div>
        <div className="font-brand font-bold text-gold-700 text-xs tracking-[0.28em] mt-1.5">
          KUYUMCULUK
        </div>
        <div className="font-brand font-bold text-gold-600 text-[11px] tracking-[0.28em] mt-1">
          1974
        </div>
      </div>

      <p className="mt-5 text-sm text-gray-600 leading-relaxed max-w-xs">
        1974&apos;ten bu yana güvenilir kuyumculuk hizmeti. Altın, döviz ve
        kıymetli madende köklü ve şeffaf bir marka.
      </p>

      <div className="mt-8 w-full max-w-sm flex flex-col gap-3">
        <a
          href={PHONE_TEL}
          className="flex items-center gap-3 bg-gray-50 active:bg-gold-50 border border-gray-200 rounded-xl px-4 py-3.5 transition-colors text-left"
        >
          <span className="w-10 h-10 rounded-full bg-gold-100 text-gold-700 flex items-center justify-center flex-shrink-0">
            <Phone className="w-5 h-5" />
          </span>
          <span>
            <span className="block text-[11px] text-gray-500 uppercase tracking-wide font-bold">
              Telefon
            </span>
            <span className="block font-bold text-black tabular-nums">
              {PHONE_DISPLAY}
            </span>
          </span>
        </a>

        <a
          href={MAP_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 bg-gray-50 active:bg-gold-50 border border-gray-200 rounded-xl px-4 py-3.5 transition-colors text-left"
        >
          <span className="w-10 h-10 rounded-full bg-gold-100 text-gold-700 flex items-center justify-center flex-shrink-0">
            <MapPin className="w-5 h-5" />
          </span>
          <span>
            <span className="block text-[11px] text-gray-500 uppercase tracking-wide font-bold">
              Adres
            </span>
            <span className="block font-bold text-black">
              {ADDRESS_TEXT || "Haritada Görüntüle →"}
            </span>
          </span>
        </a>

        <a
          href={INSTAGRAM_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 bg-gray-50 active:bg-gold-50 border border-gray-200 rounded-xl px-4 py-3.5 transition-colors text-left"
        >
          <span className="w-10 h-10 rounded-full bg-gold-100 text-gold-700 flex items-center justify-center flex-shrink-0">
            <Instagram className="w-5 h-5" />
          </span>
          <span>
            <span className="block text-[11px] text-gray-500 uppercase tracking-wide font-bold">
              Instagram
            </span>
            <span className="block font-bold text-black">@dadaskuyumculuk</span>
          </span>
        </a>
      </div>
    </div>
  );
}
