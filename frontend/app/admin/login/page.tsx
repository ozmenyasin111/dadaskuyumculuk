"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { login } from "@/hooks/useAuth";

export default function AdminLoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showAyet, setShowAyet] = useState(false);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      setShowAyet(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "giriş başarısız");
    } finally {
      setLoading(false);
    }
  }

  function proceed() {
    router.replace("/admin/marjlar");
  }

  if (showAyet) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-6 py-12">
        <div className="bg-white rounded-xl shadow-xl p-8 sm:p-10 w-full max-w-2xl border-t-4 border-gold-500">
          <h1 className="font-brand font-bold text-black text-2xl sm:text-3xl text-center mb-6">
            Bakara Sûresi · 275. Âyet
          </h1>
          <p className="text-gray-800 text-base sm:text-lg leading-relaxed mb-4 italic">
            &quot;Faiz yiyenler ancak şeytanın çarparak sersemlettiği kimse gibi
            kalkarlar. Bunun sebebi onların, &lsquo;Alım satım da ancak faiz
            gibidir&rsquo; demeleridir. Hâlbuki Allah alım satımı helâl, faizi
            ise haram kılmıştır. Artık kime Allah&apos;tan bir öğüt erişir de
            faizciliği bırakırsa geçmişteki kendisinindir, durumunun takdiri
            Allah&apos;a aittir. Kim de yine faizciliğe dönerse işte bunlar
            orada devamlı kalmak üzere cehennemliklerdir.&quot;
          </p>
          <p className="text-right font-bold text-gold-700 mb-6">— Bakara 275</p>
          <a
            href="https://www.youtube.com/@LalegulTV/search?query=alt%C4%B1n%20kuyumcu"
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full text-center bg-white border-2 border-gold-500 hover:bg-gold-50 text-gold-700 font-bold py-3 rounded transition-colors mb-3"
          >
            Altın alım satımı ile ilgili fetvalar için tıklayınız →
          </a>
          <button
            onClick={proceed}
            className="w-full bg-gold-500 hover:bg-gold-600 text-black font-bold py-3 rounded transition-colors"
          >
            Devam Et
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-6">
      <form
        onSubmit={onSubmit}
        className="bg-white rounded-xl shadow-lg p-8 w-full max-w-sm"
      >
        <h1 className="font-brand font-bold text-black text-2xl mb-6 text-center">
          Yönetici Girişi
        </h1>
        <label className="block mb-3">
          <span className="text-sm text-gray-700 font-semibold">Kullanıcı adı</span>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none"
            required
          />
        </label>
        <label className="block mb-5">
          <span className="text-sm text-gray-700 font-semibold">Şifre</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-gold-500 focus:border-gold-500 outline-none"
            required
          />
        </label>
        {error && <p className="text-sm text-fall mb-3">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gold-500 hover:bg-gold-600 text-black font-bold py-2.5 rounded transition-colors disabled:opacity-50"
        >
          {loading ? "Giriş yapılıyor…" : "Giriş"}
        </button>
      </form>
    </div>
  );
}
