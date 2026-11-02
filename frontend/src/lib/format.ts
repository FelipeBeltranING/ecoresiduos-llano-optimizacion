const numberFormatter = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 2 });

const currencyFormatter = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

/** Formats a number with Colombian thousands and decimal separators. */
export function formatNumber(value: number): string {
  return numberFormatter.format(value);
}

/** Formats a COP amount without decimals. */
export function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}

/** Formats a ratio (0.1234) as a percentage with Colombian separators. */
export function formatPercent(value: number, maximumFractionDigits = 1): string {
  return new Intl.NumberFormat("es-CO", {
    style: "percent",
    maximumFractionDigits,
  }).format(value);
}
