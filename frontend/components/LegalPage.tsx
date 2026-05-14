import Link from "next/link";

import { FooterSection } from "./FooterSection";
import { TopBar } from "./TopBar";

export function LegalPage({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <TopBar />
      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-12">
        <Link
          href="/"
          className="text-sm text-gold-700 hover:text-gold-600 transition-colors"
        >
          ← Anasayfaya dön
        </Link>
        <h1 className="font-brand font-bold text-black text-3xl sm:text-4xl mt-4 mb-8">
          {title}
        </h1>
        <article className="prose prose-sm sm:prose-base max-w-none text-gray-700 leading-relaxed space-y-4">
          {children}
        </article>
      </main>
      <FooterSection />
    </div>
  );
}
