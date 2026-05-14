"use client";

import { LogOut } from "lucide-react";
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
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

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
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
          <Link
            href="/admin/marjlar"
            className="font-brand font-bold text-black text-base sm:text-lg tracking-wider uppercase"
            lang="tr"
          >
            DADAŞ KUYUMCULUK YÖNETİM PANELİ
          </Link>
          <nav className="flex items-center gap-4">
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
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen((o) => !o)}
                className="w-9 h-9 rounded-full bg-gold-500 hover:bg-gold-600 text-white font-bold flex items-center justify-center transition-colors shadow-sm uppercase"
                title={me.username}
              >
                {initial}
              </button>
              {menuOpen && (
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
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-6">{children}</main>
    </div>
  );
}
