import { AlertCircle } from "lucide-react";

export function PriceNotice() {
  return (
    <div className="fixed bottom-6 right-6 z-20 bg-white border border-gray-200 rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 max-w-[min(20rem,calc(100vw-3rem))]">
      <span className="font-bold text-sm text-gold-700">
        Fiyatlarımız bilgi amaçlıdır.
      </span>
      <div className="w-7 h-7 rounded-full bg-gold-500 text-white flex items-center justify-center flex-shrink-0">
        <AlertCircle className="w-4 h-4" />
      </div>
    </div>
  );
}
