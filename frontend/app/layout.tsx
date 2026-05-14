import type { Metadata } from "next";
import { Cinzel, Inter } from "next/font/google";

import { CookieBanner } from "@/components/CookieBanner";

import "./globals.css";

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  variable: "--font-app",
  display: "swap",
});

const cinzel = Cinzel({
  subsets: ["latin", "latin-ext"],
  variable: "--font-brand",
  weight: ["600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Dadaş Kuyumculuk — Canlı Altın ve Döviz Fiyatları",
  description:
    "1972'den beri faaliyet gösteren Dadaş Kuyumculuk'tan canlı altın, döviz ve parite fiyatları.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr" className={`${inter.variable} ${cinzel.variable}`}>
      <body className="font-sans">
        {children}
        <CookieBanner />
      </body>
    </html>
  );
}
