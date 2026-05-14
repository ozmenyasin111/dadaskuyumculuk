"use client";

import { LogOut, Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { logout, useAuth } from "@/hooks/useAuth";

export default function AdminAuthedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { me, loading } = useAuth({ redirectIfUnauth: "/admin/login" });
  const pathname = usePathname();
  const router = useRouter();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClickOutside = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  useEffect(() => {
    setMobileNavOpen(false);
  }, [pathname]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-500">
        Yükleniyor…
      </div>
    );
  }
  if (!me) return null;

  const nav = [
    { href: "/admin/marjlar", label: "KÂR MARJLARI" },
    { href: "/admin/volatilite", label: "VOLATİLİTE" },
    { href: "/admin/zekat", label: "ZEKAT HESAPLA" },
    { href: "/admin/kullanicilar", label: "KULLANICILAR" },
  ];

  async function onLogout() {
    await logout();
    router.replace("/admin/login");
  }

  const initial = me.username.charAt(0).toLocaleUpperCase("tr-TR");

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 relative">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <Link
            href="/admin/marjlar"
            className="font-brand font-bold text-black text-sm sm:text-lg tracking-wider uppercase truncate min-w-0"
            lang="tr"
          >
            <span className="hidden sm:inline">DADAŞ KUYUMCULUK YÖNETİM PANELİ</span>
            <span className="sm:hidden">DADAŞ YÖNETİM</span>
          </Link>

          {/* Masaüstü nav */}
          <nav className="hidden md:flex items-center gap-4">
            {nav.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                className={
                  pathname.startsWith(n.href)
                    ? "text-gold-700 font-bold text-xs tracking-wider"
                    : "text-gray-600 hover:text-gold-600 font-bold text-xs tracking-wider"
                }
              >
                {n.label}
              </Link>
            ))}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen((o) => !o)}
                className="w-9 h-9 rounded-full bg-gold-500 hover:bg-gold-600 text-white font-bold flex items-center justify-center transition-colors shadow-sm uppercase"
                title={me.username}
              >
                {initial}
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-44 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden z-40">
                  <div className="px-3 py-2 border-b border-gray-100 text-xs text-gray-500">
                    Giriş: <span className="font-bold text-gray-800">{me.username}</span>
                  </div>
                  <button
                    onClick={onLogout}
                    className="w-full text-left px-3 py-2.5 text-sm font-bold text-fall hover:bg-red-50 flex items-center gap-2 transition-colors"
                  >
                    <span aria-hidden>🔴</span>
                    <LogOut className="w-4 h-4" /> Çıkış Yap
                  </button>
                </div>
              )}
            </div>
          </nav>

          {/* Mobil — avatar + hamburger */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => {
                setUserMenuOpen((o) => !o);
                setMobileNavOpen(false);
              }}
              className="w-9 h-9 rounded-full bg-gold-500 hover:bg-gold-600 text-white font-bold flex items-center justify-center transition-colors shadow-sm uppercase"
              title={me.username}
            >
              {initial}
            </button>
            <button
              onClick={() => {
                setMobileNavOpen((o) => !o);
                setUserMenuOpen(false);
              }}
              aria-label={mobileNavOpen ? "Menüyü kapat" : "Menüyü aç"}
              className="w-9 h-9 rounded bg-gold-500 hover:bg-gold-600 text-white flex items-center justify-center transition-colors"
            >
              {mobileNavOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobil user menü (avatar açılınca) */}
        {userMenuOpen && (
          <div className="md:hidden absolute right-4 top-full mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden z-40">
            <div className="px-3 py-2 border-b border-gray-100 text-xs text-gray-500">
              Giriş: <span className="font-bold text-gray-800">{me.username}</span>
            </div>
            <button
              onClick={onLogout}
              className="w-full text-left px-3 py-2.5 text-sm font-bold text-fall hover:bg-red-50 flex items-center gap-2 transition-colors"
            >
              <span aria-hidden>🔴</span>
              <LogOut className="w-4 h-4" /> Çıkış Yap
            </button>
          </div>
        )}

        {/* Mobil nav paneli (hamburger açılınca) */}
        {mobileNavOpen && (
          <>
            <button
              aria-label="Menüyü kapat"
              onClick={() => setMobileNavOpen(false)}
              className="fixed inset-0 top-[64px] bg-black/40 z-20 md:hidden"
            />
            <nav className="absolute left-0 right-0 top-full bg-white border-b border-gray-200 shadow-lg z-30 md:hidden">
              <div className="flex flex-col p-4 gap-2">
                {nav.map((n) => (
                  <Link
                    key={n.href}
                    href={n.href}
                    onClick={() => setMobileNavOpen(false)}
                    className={
                      pathname.startsWith(n.href)
                        ? "bg-gold-500 text-white font-bold rounded px-4 py-3 text-sm text-center"
                        : "bg-gray-100 hover:bg-gold-100 text-gray-800 font-bold rounded px-4 py-3 text-sm text-center"
                    }
                  >
                    {n.label}
                  </Link>
                ))}
              </div>
            </nav>
          </>
        )}
      </header>
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6">{children}</main>
    </div>
  );
}
