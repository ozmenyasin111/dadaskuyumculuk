"use client";

import Image from "next/image";
import Link from "next/link";
import { Phone } from "lucide-react";

const NAV_BTN =
  "bg-gold-500 hover:bg-gold-600 text-white font-bold rounded px-3 py-1.5 text-sm transition-colors shadow-sm";

export function TopBar() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
        <Link
          href="/"
          className="flex items-center gap-4"
          aria-label="Dadaş Kuyumculuk anasayfa"
        >
          <Image
            src="/logo-figure.png"
            alt=""
            width={1024}
            height={1047}
            priority
            className="h-20 sm:h-24 w-auto"
          />
          <div className="text-center leading-none">
            <div className="font-brand font-bold text-black text-4xl sm:text-5xl tracking-[0.04em]">
              DADAŞ
            </div>
            <div className="font-brand font-bold text-gold-700 text-xs sm:text-sm tracking-[0.32em] mt-1.5">
              KUYUMCULUK
            </div>
            <div className="font-brand font-bold text-gold-600 text-[11px] sm:text-xs tracking-[0.32em] mt-1">
              1974
            </div>
          </div>
        </Link>
        <nav className="flex items-center gap-2 sm:gap-3">
          <a href="#pariteler" className={`${NAV_BTN} hidden sm:inline-flex`}>
            Pariteler
          </a>
          <a href="#hakkimizda" className={`${NAV_BTN} hidden sm:inline-flex`}>
            Hakkımızda
          </a>
          <a
            href="tel:02125534525"
            className={`${NAV_BTN} inline-flex items-center gap-2`}
          >
            <Phone className="w-4 h-4" />
            <span className="tabular-nums">0212 553 45 25</span>
          </a>
        </nav>
      </div>
    </header>
  );
}
