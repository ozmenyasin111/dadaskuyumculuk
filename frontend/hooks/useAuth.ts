"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError, api } from "@/lib/api";

type Me = { id: number; username: string };

export function useAuth(opts: { redirectIfUnauth?: string } = {}) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    api<Me>("/api/auth/me")
      .then((u) => setMe(u))
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401 && opts.redirectIfUnauth) {
          router.replace(opts.redirectIfUnauth);
        }
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { me, loading };
}

export async function login(username: string, password: string) {
  return api<Me>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function logout() {
  await api("/api/auth/logout", { method: "POST" });
}
