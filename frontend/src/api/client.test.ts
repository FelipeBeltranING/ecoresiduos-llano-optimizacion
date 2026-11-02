import { describe, expect, it } from "vitest";

import { normalizeBaseUrl } from "./client";

describe("normalizeBaseUrl", () => {
  it("falls back to the local prefix when the variable is missing", () => {
    expect(normalizeBaseUrl(undefined)).toBe("/api/v1");
    expect(normalizeBaseUrl("   ")).toBe("/api/v1");
  });

  it("trims the value and removes trailing slashes", () => {
    expect(normalizeBaseUrl(" http://localhost:8000/api/v1/ ")).toBe("http://localhost:8000/api/v1");
  });
});
