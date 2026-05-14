export const formatTR = (n: number, fractionDigits = 2): string =>
  new Intl.NumberFormat("tr-TR", {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(n);

export const autoFractionDigits = (n: number): number =>
  Math.abs(n) < 1 ? 4 : 2;

export const formatPrice = (n: number): string =>
  formatTR(n, autoFractionDigits(n));

export const formatPct = (n: number): string => {
  const sign = n > 0 ? "+" : "";
  return `${sign}${formatTR(n, 2)}%`;
};

export const formatTime = (ms: number): string => {
  if (!ms) return "—";
  return new Date(ms).toLocaleTimeString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
};
