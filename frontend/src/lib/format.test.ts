import { describe, expect, it } from "vitest";

import { formatCurrency, formatNumber, formatPercent } from "./format";

describe("format helpers", () => {
  it("formats numbers with Colombian separators", () => {
    expect(formatNumber(1234.5)).toBe("1.234,5");
  });

  it("formats COP amounts without decimals", () => {
    expect(formatCurrency(1_500_000)).toMatch(/1\.500\.000/);
  });

  it("formats ratios as percentages", () => {
    expect(formatPercent(0.1234)).toMatch(/12,3/);
  });
});
