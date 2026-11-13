import { expect, test } from "@playwright/test";

test("carga el panel principal", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("link", { name: "EcoResiduos del Llano" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Panel de control" })).toBeAttached();
});
