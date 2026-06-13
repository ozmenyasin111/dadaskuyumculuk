"use client";

import clsx from "clsx";
import { Banknote, Coins, MapPin } from "lucide-react";

export type MobileTab = "sarrafiye" | "doviz" | "iletisim";

const TABS: { id: MobileTab; label: string; Icon: typeof Coins }[] = [
  { id: "sarrafiye", label: "Sarrafiye", Icon: Coins },
  { id: "doviz", label: "Döviz", Icon: Banknote },
  { id: "iletisim", label: "İletişim", Icon: MapPin },
];

export function MobileTabBar({
  active,
  onChange,
}: {
  active: MobileTab;
  onChange: (tab: MobileTab) => void;
}) {
  return (
    <nav
      className="flex-shrink-0 bg-white border-t border-gray-200"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="flex items-stretch justify-around">
        {TABS.map(({ id, label, Icon }) => {
          const isActive = active === id;
          return (
            <button
              key={id}
              type="button"
              onClick={() => onChange(id)}
              aria-current={isActive ? "page" : undefined}
              className={clsx(
                "flex-1 flex flex-col items-center justify-center gap-1 py-2.5 transition-colors",
                isActive ? "text-gold-600" : "text-gray-400 hover:text-gray-600",
              )}
            >
              <Icon className="w-6 h-6" strokeWidth={isActive ? 2.5 : 2} />
              <span
                className={clsx(
                  "text-[11px] tracking-wide",
                  isActive ? "font-bold" : "font-medium",
                )}
              >
                {label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
