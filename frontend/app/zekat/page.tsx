import { FooterSection } from "@/components/FooterSection";
import { TopBar } from "@/components/TopBar";
import { ZekatCalculator } from "@/components/ZekatCalculator";

export const metadata = {
  title: "Zekat Hesaplama — Dadaş Kuyumculuk",
  description:
    "Canlı altın, gümüş ve döviz kurlarıyla zekat hesaplama. Nisap kontrolü ve %2,5 oran üzerinden ödenecek zekat tutarı.",
};

export default function PublicZekatPage() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <TopBar />
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-8">
        <ZekatCalculator />
      </main>
      <FooterSection />
    </div>
  );
}
