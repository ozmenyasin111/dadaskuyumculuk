import { LegalPage } from "@/components/LegalPage";

export const metadata = {
  title: "Müşteri Aydınlatma Metni — Dadaş Kuyumculuk",
};

export default function MusteriAydinlatmaPage() {
  return (
    <LegalPage title="Müşteri Aydınlatma Metni">
      <p>
        Dadaş Kuyumculuk olarak, mağazamızdan alışveriş yapmanız halinde kişisel
        verilerinizi (kimlik, iletişim, satış işlemi bilgileri) yasal zorunluluklar
        ve müşteri ilişkilerinin yönetimi kapsamında işlemekteyiz.
      </p>
      <h2 className="font-bold text-black text-lg mt-6">İşleme Hukuki Sebebi</h2>
      <p>
        Verileriniz, KVKK 5. maddesi kapsamında bir sözleşmenin kurulması veya
        ifası, hukuki yükümlülüklerin yerine getirilmesi ve meşru menfaat amacıyla
        işlenmektedir.
      </p>
      <h2 className="font-bold text-black text-lg mt-6">Veri Güvenliği</h2>
      <p>
        Kişisel verilerinizin korunması için idari ve teknik güvenlik tedbirleri
        alınmaktadır.
      </p>
      <p className="text-xs text-gray-500 italic mt-8">
        Bu metin örnek niteliğindedir; yetkili hukukçu danışmanlığıyla nihai
        sürümünü oluşturmanız önerilir.
      </p>
    </LegalPage>
  );
}
