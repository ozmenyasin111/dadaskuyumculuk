"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

const STORAGE_KEY = "dadas-cookie-consent";

export function CookieBanner() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem(STORAGE_KEY)) setShow(true);
  }, []);

  if (!show) return null;

  const decide = (val: "accept" | "reject" | "settings") => {
    localStorage.setItem(STORAGE_KEY, val);
    document.cookie = `${STORAGE_KEY}=${val}; max-age=${60 * 60 * 24 * 365}; path=/`;
    setShow(false);
  };

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 sm:left-auto sm:translate-x-0 sm:right-6 z-50 max-w-xl w-[calc(100vw-3rem)] bg-white border border-gray-200 rounded-xl shadow-2xl p-5 sm:p-6">
      <div className="flex items-center gap-3 mb-3">
        <Image
          src="/logo-figure.png"
          alt="Dadaş Kuyumculuk"
          width={1024}
          height={1047}
          className="h-12 w-auto object-contain"
        />
        <span className="font-brand font-bold text-base sm:text-lg">DADAŞ KUYUMCULUK</span>
      </div>
      <p className="text-xs sm:text-sm text-gray-700 leading-relaxed mb-4">
        Dadaş Kuyumculuk olarak sizlere daha iyi hizmet sunabilmek için internet
        sitemizde, internet sitesi fonksiyonlarını sağlayabilmek ve bilgi toplumu
        hizmetlerini sunabilmek için gerekli olan zorunlu çerezler ile
        kişiselleştirme, sitemizin daha işlevsel kılınması, sizlere yönelik
        reklam/pazarlama faaliyetlerinin gerçekleştirilmesi amaçlarıyla açık
        rızanıza dayanan diğer çerezler kullanılmaktadır. &quot;Kabul Et&quot;
        tuşuna basmanız halinde tüm çerezlerin kullanımını onaylamış olursunuz.
      </p>
      <div className="flex gap-2 sm:gap-3">
        <button
          onClick={() => decide("settings")}
          className="flex-1 bg-gold-500 hover:bg-gold-600 text-white py-2 sm:py-2.5 rounded font-medium transition-colors text-sm"
        >
          Ayarlar
        </button>
        <button
          onClick={() => decide("reject")}
          className="flex-1 bg-gold-500 hover:bg-gold-600 text-white py-2 sm:py-2.5 rounded font-medium transition-colors text-sm"
        >
          Reddet
        </button>
        <button
          onClick={() => decide("accept")}
          className="flex-1 bg-gold-500 hover:bg-gold-600 text-white py-2 sm:py-2.5 rounded font-medium transition-colors text-sm"
        >
          Kabul Et
        </button>
      </div>
    </div>
  );
}
