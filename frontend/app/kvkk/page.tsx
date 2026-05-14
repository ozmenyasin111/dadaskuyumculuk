import { LegalPage } from "@/components/LegalPage";

export const metadata = {
  title: "KVKK Aydınlatma Metni — Dadaş Kuyumculuk",
};

export default function KvkkPage() {
  return (
    <LegalPage title="KVKK Aydınlatma Metni">
      <p>
        Dadaş Kuyumculuk olarak, 6698 sayılı Kişisel Verilerin Korunması Kanunu
        (&quot;KVKK&quot;) kapsamında veri sorumlusu sıfatıyla, kişisel verilerinizin işlenme
        süreçleri ve haklarınız hakkında sizleri bilgilendiririz.
      </p>
      <h2 className="font-bold text-black text-lg mt-6">İşlenen Kişisel Veriler</h2>
      <p>
        Mağazamızı ziyaret etmeniz, telefon görüşmesi yapmanız veya web sitemiz
        üzerinden iletişime geçmeniz halinde kimlik, iletişim ve işlem bilgileriniz
        işlenebilir.
      </p>
      <h2 className="font-bold text-black text-lg mt-6">Kişisel Verilerin İşlenme Amacı</h2>
      <p>
        Müşteri ilişkilerinin yönetimi, talep ve şikâyet süreçlerinin takibi, yasal
        yükümlülüklerin yerine getirilmesi ve güvenlik amacıyla işlenmektedir.
      </p>
      <h2 className="font-bold text-black text-lg mt-6">Haklarınız</h2>
      <p>
        KVKK&apos;nın 11. maddesi kapsamında, kişisel verilerinize ilişkin haklarınızı
        kullanmak için 0212 557 25 25 numarası üzerinden bizimle iletişime
        geçebilirsiniz.
      </p>
      <p className="text-xs text-gray-500 italic mt-8">
        Bu metin örnek niteliğindedir; yetkili hukukçu danışmanlığıyla nihai
        sürümünü oluşturmanız önerilir.
      </p>
    </LegalPage>
  );
}
