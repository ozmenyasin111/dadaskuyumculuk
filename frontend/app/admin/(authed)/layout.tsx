"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { logout, useAuth } from "@/hooks/useAuth";

export default function AdminAuthedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { me, loading } = useAuth({ redirectIfUnauth: "/admin/login" });
  const pathname = usePathname();
  const router = useRouter();

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
    { href: "/admin/volatilite", label: "VOLATİLİTE (PİYASA SARSINTISI)" },
    { href: "/admin/zekat", label: "ZEKAT HESAPLA" },
    { href: "/admin/kullanicilar", label: "KULLANICILAR" },
  ];

  async function onLogout() {
    await logout();
    router.replace("/admin/login");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
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
            <span className="text-sm text-gray-500">{me.username}</span>
            <button
              onClick={onLogout}
              className="text-sm text-gray-600 hover:text-fall transition-colors"
            >
              Çıkış
            </button>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-6">{children}</main>
    </div>
  );
}
