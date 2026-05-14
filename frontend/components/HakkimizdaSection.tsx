import Image from "next/image";
import { MapPin, Phone } from "lucide-react";

const MAP_URL = "https://share.google/aYsPNr2zozwmhwt2O";

export function HakkimizdaSection() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-8 sm:p-12">
      <div className="flex flex-col md:flex-row md:items-center gap-8 md:gap-12 mb-8">
        <div className="flex-shrink-0 flex justify-center md:justify-start">
          <Image
            src="/logo-figure.png"
            alt="Dadaş Kuyumculuk"
            width={1037}
            height={1024}
            className="h-48 sm:h-60 md:h-72 w-auto"
          />
        </div>
        <div className="flex-1 md:text-left text-center">
          <h2 className="font-brand font-bold text-black text-4xl sm:text-6xl tracking-[0.04em]">
            DADAŞ
          </h2>
          <div className="font-brand font-bold text-gold-700 text-base sm:text-lg tracking-[0.32em] mt-2">
            KUYUMCULUK
          </div>
          <div className="font-brand font-bold text-gold-600 text-sm sm:text-base tracking-[0.32em] mt-1">
            1974
          </div>
          <p className="text-base text-gray-700 leading-relaxed mt-6">
            1974 yılından bu yana altın ve kıymetli maden sektörlerinde faaliyet
            gösteren Dadaş Kuyumculuk, sektördeki 52 yılı aşkın tecrübesiyle
            güvenilir ve köklü bir markadır. Müşteri memnuniyetini esas alan
            hizmet anlayışıyla faaliyet gösteren Dadaş Kuyumculuk, altın
            piyasalarında şeffaf, etik ve sürdürülebilir bir yapıyla hizmet
            sunmaktadır ve etik değerlerden ödün vermeden kaliteli hizmeti
            teknolojiyle birleştirir.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto">
        <a
          href="tel:02125572525"
          className="flex items-center gap-3 bg-gray-50 hover:bg-gold-50 border border-gray-200 rounded-lg px-4 py-3 transition-colors"
        >
          <div className="w-10 h-10 rounded-full bg-gold-100 text-gold-700 flex items-center justify-center">
            <Phone className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-wide font-bold">
              Telefon
            </div>
            <div className="font-bold text-black tabular-nums">
              0212 557 25 25
            </div>
          </div>
        </a>
        <a
          href={MAP_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 bg-gray-50 hover:bg-gold-50 border border-gray-200 rounded-lg px-4 py-3 transition-colors"
        >
          <div className="w-10 h-10 rounded-full bg-gold-100 text-gold-700 flex items-center justify-center">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-wide font-bold">
              Konum
            </div>
            <div className="font-bold text-black">Haritada Görüntüle →</div>
          </div>
        </a>
      </div>
    </div>
  );
}
