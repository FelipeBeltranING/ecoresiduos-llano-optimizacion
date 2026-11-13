const numberFormatter = new Intl.NumberFormat("es-CO", { maximumFractionDigits: 2 });

const currencyFormatter = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});


export function formatNumber(value: number): string {
  return numberFormatter.format(value);
}


export function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}


export function formatPercent(value: number, maximumFractionDigits = 1): string {
  return new Intl.NumberFormat("es-CO", {
    style: "percent",
    maximumFractionDigits,
  }).format(value);
}
