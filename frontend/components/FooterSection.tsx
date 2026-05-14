import Image from "next/image";
import Link from "next/link";
import { Instagram } from "lucide-react";

export function FooterSection() {
  return (
    <footer className="bg-black text-white mt-16">
      <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 sm:grid-cols-3 gap-8">
        <div className="flex flex-col items-start gap-3">
          <div className="flex items-center gap-3">
            <Image
              src="/logo-figure.png"
              alt=""
              width={1037}
              height={1024}
              className="h-16 w-auto"
              style={{ filter: "invert(0.92) brightness(1.05)" }}
            />
            <div className="leading-none">
              <div className="font-brand font-bold text-white text-2xl tracking-[0.04em]">
                DADAŞ
              </div>
              <div className="font-brand font-bold text-gold-400 text-[11px] tracking-[0.28em] mt-1">
                KUYUMCULUK
              </div>
              <div className="font-brand font-bold text-gold-500 text-[10px] tracking-[0.28em] mt-1">
                1974
              </div>
            </div>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed mt-2">
            1974&apos;ten bu yana güvenilir kuyumculuk hizmeti.
          </p>
        </div>

        <div className="text-sm">
          <div className="font-bold uppercase tracking-wider text-gold-400 mb-3 text-xs">
            Bilgilendirme
          </div>
          <ul className="space-y-2 text-gray-300">
            <li>
              <a href="#hakkimizda" className="hover:text-gold-400 transition-colors">
                Hakkımızda
              </a>
            </li>
            <li>
              <Link href="/kvkk" className="hover:text-gold-400 transition-colors">
                KVKK
              </Link>
            </li>
            <li>
              <Link
                href="/iletisim-aydinlatma"
                className="hover:text-gold-400 transition-colors"
              >
                İletişim Formu Aydınlatma Metni
              </Link>
            </li>
            <li>
              <Link
                href="/musteri-aydinlatma"
                className="hover:text-gold-400 transition-colors"
              >
                Müşteri Aydınlatma Metni
              </Link>
            </li>
          </ul>
        </div>

        <div className="text-sm">
          <div className="font-bold uppercase tracking-wider text-gold-400 mb-3 text-xs">
            Sosyal Medya
          </div>
          <a
            href="https://www.instagram.com/dadaskuyumculuk/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-gray-300 hover:text-gold-400 transition-colors"
          >
            <Instagram className="w-5 h-5" />
            @dadaskuyumculuk
          </a>
        </div>
      </div>
      <div className="border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-4 text-xs text-gray-500 text-center">
          © {new Date().getFullYear()} Dadaş Kuyumculuk. Tüm hakları saklıdır.
        </div>
      </div>
    </footer>
  );
}
