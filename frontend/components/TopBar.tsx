"use client";

import { Menu, Phone, X } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const NAV_BTN =
  "bg-gold-500 hover:bg-gold-600 text-white font-bold rounded px-3 py-1.5 text-sm transition-colors shadow-sm";

export function TopBar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

  // Sayfa değişince menüyü kapat
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  // Menü açıkken arka plan kaydırmayı engelle
  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
        <Link
          href="/"
          className="flex items-center gap-3 sm:gap-4 min-w-0"
          aria-label="Dadaş Kuyumculuk anasayfa"
        >
          <Image
            src="/logo-figure.png"
            alt=""
            width={1037}
            height={1024}
            priority
            className="h-14 sm:h-20 md:h-24 w-auto flex-shrink-0"
          />
          <div className="text-center leading-none">
            <div className="font-brand font-bold text-black text-2xl sm:text-4xl md:text-5xl tracking-[0.04em]">
              DADAŞ
            </div>
            <div className="font-brand font-bold text-gold-700 text-[10px] sm:text-xs md:text-sm tracking-[0.24em] sm:tracking-[0.32em] mt-1 sm:mt-1.5">
              KUYUMCULUK
            </div>
            <div className="font-brand font-bold text-gold-600 text-[10px] sm:text-[11px] md:text-xs tracking-[0.24em] sm:tracking-[0.32em] mt-0.5 sm:mt-1">
              1974
            </div>
          </div>
        </Link>

        {/* Masaüstü navigasyon */}
        <nav className="hidden sm:flex items-center gap-2 sm:gap-3">
          <a href="/#pariteler" className={NAV_BTN}>
            Pariteler
          </a>
          <Link href="/zekat" className={NAV_BTN}>
            Zekat Hesapla
          </Link>
          <a href="/#hakkimizda" className={NAV_BTN}>
            Hakkımızda
          </a>
          <a
            href="tel:02125572525"
            className={`${NAV_BTN} inline-flex items-center gap-2`}
          >
            <Phone className="w-4 h-4" />
            <span className="tabular-nums">0212 557 25 25</span>
          </a>
        </nav>

        {/* Mobil — telefon ikonu + hamburger */}
        <div className="flex sm:hidden items-center gap-2">
          <a
            href="tel:02125572525"
            aria-label="Ara"
            className="w-10 h-10 rounded bg-gold-500 hover:bg-gold-600 text-white flex items-center justify-center"
          >
            <Phone className="w-4 h-4" />
          </a>
          <button
            onClick={() => setMenuOpen((o) => !o)}
            aria-label={menuOpen ? "Menüyü kapat" : "Menüyü aç"}
            className="w-10 h-10 rounded bg-gold-500 hover:bg-gold-600 text-white flex items-center justify-center"
          >
            {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobil menü paneli */}
      {menuOpen && (
        <>
          <button
            aria-label="Menüyü kapat"
            onClick={() => setMenuOpen(false)}
            className="fixed inset-0 top-[72px] bg-black/40 z-20 sm:hidden"
          />
          <nav className="absolute left-0 right-0 top-full bg-white border-b border-gray-200 shadow-lg z-30 sm:hidden">
            <div className="flex flex-col p-4 gap-2">
              <a
                href="/#pariteler"
                onClick={() => setMenuOpen(false)}
                className="bg-gold-500 hover:bg-gold-600 text-white font-bold rounded px-4 py-3 text-sm transition-colors text-center"
              >
                Pariteler
              </a>
              <Link
                href="/zekat"
                onClick={() => setMenuOpen(false)}
                className="bg-gold-500 hover:bg-gold-600 text-white font-bold rounded px-4 py-3 text-sm transition-colors text-center"
              >
                Zekat Hesapla
              </Link>
              <a
                href="/#hakkimizda"
                onClick={() => setMenuOpen(false)}
                className="bg-gold-500 hover:bg-gold-600 text-white font-bold rounded px-4 py-3 text-sm transition-colors text-center"
              >
                Hakkımızda
              </a>
              <a
                href="tel:02125572525"
                onClick={() => setMenuOpen(false)}
                className="bg-gold-500 hover:bg-gold-600 text-white font-bold rounded px-4 py-3 text-sm transition-colors text-center inline-flex items-center justify-center gap-2"
              >
                <Phone className="w-4 h-4" />
                <span className="tabular-nums">0212 557 25 25</span>
              </a>
            </div>
          </nav>
        </>
      )}
    </header>
  );
}
