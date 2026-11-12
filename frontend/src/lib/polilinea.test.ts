import { describe, expect, it } from "vitest";

import { decodificarPolilinea } from "./polilinea";

describe("decodificarPolilinea", () => {
  it("decodifica el ejemplo de la especificación de Google", () => {
    const puntos = decodificarPolilinea("_p~iF~ps|U_ulLnnqC_mqNvxq`@");
    expect(puntos).toEqual([
      [38.5, -120.2],
      [40.7, -120.95],
      [43.252, -126.453],
    ]);
  });

  it("devuelve una lista vacía para un texto vacío", () => {
    expect(decodificarPolilinea("")).toEqual([]);
  });
});
