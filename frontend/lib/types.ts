export type PriceRow = {
  symbol_key: string;
  display_name: string;
  category: string;
  alis: number;
  satis: number;
  raw_bid: number;
  raw_ask: number;
  trend: "up" | "down" | "flat";
  pct_change: number;
  using_volatility: boolean;
  is_readonly: boolean;
  sort_order: number;
};

export type Parite = {
  symbol: string;
  bid: number;
  ask: number;
  trend: "up" | "down" | "flat";
  pct_change: number;
};

export type PricesPayload = {
  fiyatlar: PriceRow[];
  pariteler: Parite[];
  guncellendi: number;
  healthy: boolean;
};

export type Margin = {
  id: number;
  symbol_key: string;
  display_name: string;
  category: string;
  alis_offset: string;
  satis_offset: string;
  classic_alis_offset: string;
  classic_satis_offset: string;
  sort_order: number;
  is_readonly: boolean;
  is_multiplier: boolean;
};

export type PricingMode = "milyem" | "classic";

export type Volatility = {
  id: number;
  category: string;
  threshold: string;
  alis_override: string;
  satis_override: string;
  enabled: boolean;
};

export type AdminUser = {
  id: number;
  username: string;
  created_at: string;
  last_login: string | null;
};
