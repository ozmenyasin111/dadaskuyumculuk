import { LegalPage } from "@/components/LegalPage";

export const metadata = {
  title: "İletişim Formu Aydınlatma Metni — Dadaş Kuyumculuk",
};

export default function IletisimAydinlatmaPage() {
  return (
    <LegalPage title="İletişim Formu Aydınlatma Metni">
      <p>
        Web sitemiz veya telefon üzerinden bizimle iletişime geçmeniz halinde,
        sağlamış olduğunuz ad, soyad, telefon numarası ve mesaj içeriği bilgileriniz
        talep ve şikâyetlerinizin değerlendirilmesi amacıyla işlenmektedir.
      </p>
      <h2 className="font-bold text-black text-lg mt-6">Verilerin Saklanması</h2>
      <p>
        İletişim bilgileriniz, ilgili işin tamamlanması ve KVKK&apos;da öngörülen
        süre boyunca saklanır; sonrasında imha edilir.
      </p>
      <h2 className="font-bold text-black text-lg mt-6">Aktarım</h2>
      <p>
        Kişisel verileriniz, yasal zorunluluklar haricinde üçüncü kişilerle
        paylaşılmaz.
      </p>
      <p className="text-xs text-gray-500 italic mt-8">
        Bu metin örnek niteliğindedir; yetkili hukukçu danışmanlığıyla nihai
        sürümünü oluşturmanız önerilir.
      </p>
    </LegalPage>
  );
}
