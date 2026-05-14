"use client";

import { Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { AdminUser } from "@/lib/types";

export default function KullanicilarPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [flash, setFlash] = useState<string | null>(null);

  async function load() {
    setUsers(await api<AdminUser[]>("/api/admin/users"));
  }
  useEffect(() => {
    load();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api<AdminUser>("/api/admin/users", {
        method: "POST",
        body: JSON.stringify({ username: newUsername, password: newPassword }),
      });
      setNewUsername("");
      setNewPassword("");
      setFlash("kullanıcı eklendi");
      setTimeout(() => setFlash(null), 2000);
      await load();
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "hata");
    }
  }

  async function changePassword(id: number) {
    const pwd = prompt("Yeni şifre (min 6 karakter):");
    if (!pwd) return;
    try {
      await api(`/api/admin/users/${id}/password`, {
        method: "PATCH",
        body: JSON.stringify({ password: pwd }),
      });
      setFlash("şifre güncellendi");
      setTimeout(() => setFlash(null), 2000);
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "hata");
    }
  }

  async function remove(id: number, username: string) {
    if (!confirm(`${username} silinsin mi?`)) return;
    try {
      await api(`/api/admin/users/${id}`, { method: "DELETE" });
      await load();
    } catch (err) {
      setFlash(err instanceof Error ? err.message : "hata");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gold-700">Kullanıcılar</h1>
        {flash && <span className="text-sm text-rise">{flash}</span>}
      </div>

      <form
        onSubmit={add}
        className="bg-white rounded-lg border border-gray-200 p-4 mb-6 flex flex-col sm:flex-row gap-3 sm:items-end"
      >
        <label className="flex-1">
          <span className="text-xs text-gray-600 mb-1 block">Kullanıcı adı</span>
          <input
            type="text"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            required
            minLength={1}
            className="w-full px-3 py-2 border border-gray-300 rounded outline-none focus:ring-2 focus:ring-gold-500"
          />
        </label>
        <label className="flex-1">
          <span className="text-xs text-gray-600 mb-1 block">Şifre</span>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            minLength={6}
            className="w-full px-3 py-2 border border-gray-300 rounded outline-none focus:ring-2 focus:ring-gold-500"
          />
        </label>
        <button
          type="submit"
          className="px-4 py-2 bg-gold-500 hover:bg-gold-600 text-white rounded font-medium transition-colors w-full sm:w-auto"
        >
          Ekle
        </button>
      </form>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="hidden sm:grid sm:grid-cols-12 sm:gap-2 bg-gray-50 px-4 py-2 text-xs uppercase text-gray-500">
          <div className="col-span-3">Kullanıcı</div>
          <div className="col-span-4">Oluşturulma</div>
          <div className="col-span-3">Son giriş</div>
          <div className="col-span-2 text-right">İşlem</div>
        </div>
        {users.map((u) => (
          <div
            key={u.id}
            className="flex flex-col gap-1.5 sm:grid sm:grid-cols-12 sm:gap-2 sm:items-center px-4 py-3 border-b border-gray-100"
          >
            <div className="sm:col-span-3 font-bold text-gray-800">{u.username}</div>
            <div className="sm:col-span-4 text-xs sm:text-sm text-gray-600 tabular-nums">
              <span className="sm:hidden font-semibold text-gray-500">Oluşturulma: </span>
              {new Date(u.created_at).toLocaleString("tr-TR")}
            </div>
            <div className="sm:col-span-3 text-xs sm:text-sm text-gray-600 tabular-nums">
              <span className="sm:hidden font-semibold text-gray-500">Son giriş: </span>
              {u.last_login
                ? new Date(u.last_login).toLocaleString("tr-TR")
                : "—"}
            </div>
            <div className="sm:col-span-2 flex items-center justify-start sm:justify-end gap-2 mt-2 sm:mt-0">
              <button
                onClick={() => changePassword(u.id)}
                className="text-xs px-2 py-1 text-gold-700 hover:bg-gold-50 rounded"
              >
                Şifre
              </button>
              <button
                onClick={() => remove(u.id, u.username)}
                className="text-fall hover:bg-red-50 p-1 rounded"
                title="Sil"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
