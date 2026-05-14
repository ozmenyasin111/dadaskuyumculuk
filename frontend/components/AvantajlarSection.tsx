import { Award, BellRing, Gauge } from "lucide-react";

const ITEMS = [
  { icon: Gauge, title: "Hızlı ve Güvenli İşlem" },
  { icon: Award, title: "Kaliteli Ürün Doğru Fiyat" },
  { icon: BellRing, title: "Kusursuz Hizmet Garantisi" },
];

export function AvantajlarSection() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-8 sm:p-12">
      <h2 className="text-center text-2xl sm:text-3xl font-bold text-black mb-10 sm:mb-12">
        Dadaş Kuyumculuk İle Ayrıcalıklarınız
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-12">
        {ITEMS.map(({ icon: Icon, title }) => (
          <div
            key={title}
            className="flex flex-col items-center gap-4 text-center"
          >
            <div className="w-16 h-16 rounded-full bg-gold-100 text-gold-700 flex items-center justify-center">
              <Icon className="w-8 h-8" strokeWidth={2.5} />
            </div>
            <h3 className="font-bold text-black text-base sm:text-lg">{title}</h3>
          </div>
        ))}
      </div>
    </div>
  );
}
