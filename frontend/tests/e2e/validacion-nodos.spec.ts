import { expect, test } from "@playwright/test";

test("rechaza campos vacíos y capacidades negativas", async ({ page }) => {
  await page.goto("/red");

  await page.getByRole("button", { name: "Agregar" }).click();
  await expect(page.getByText("Obligatorio").first()).toBeVisible();

  await page.getByLabel("Oferta (t/semana)").fill("-5");
  await page.getByRole("button", { name: "Agregar" }).click();
  await expect(page.getByText("Debe ser mayor que 0")).toBeVisible();
});
