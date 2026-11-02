import { useState } from "react";

import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";

const tipoItems = [
  { label: "Transporte", value: "transporte" },
  { label: "Oferta", value: "oferta" },
  { label: "Capacidad", value: "capacidad" },
];

const aplicarItems = [
  { label: "Todas las rutas", value: "todas" },
  { label: "Rutas específicas", value: "especificas" },
];

const escenarios = [
  {
    nombre: "Caso base",
    cambio: "—",
    exacto: "64.691.000",
    ag: "65.012.000",
    gap: "0,50 %",
    delta: "—",
    destacado: false,
  },
  {
    nombre: "Combustible +20 %",
    cambio: "k 350 → 420",
    exacto: "69.385.200",
    ag: "69.788.000",
    gap: "0,58 %",
    delta: "+7,3 %",
    destacado: true,
  },
  {
    nombre: "Oferta −10 %",
    cambio: "890 → 801 t",
    exacto: "58.402.000",
    ag: "58.788.000",
    gap: "0,66 %",
    delta: "−9,7 %",
    destacado: false,
  },
  {
    nombre: "Villavicencio −20 %",
    cambio: "300 → 240 t",
    exacto: "65.756.000",
    ag: "66.098.000",
    gap: "0,52 %",
    delta: "+1,6 %",
    destacado: false,
  },
];

const tornado = [
  { etiqueta: "Oferta ±10 %", valor: "$6,3 M", porcentaje: 100 },
  { etiqueta: "Costo de transporte k ±20 %", valor: "$4,7 M", porcentaje: 74 },
  { etiqueta: "Costo de operación ±10 %", valor: "$4,1 M", porcentaje: 65 },
  { etiqueta: "Capacidad Villavicencio ±20 %", valor: "$1,1 M", porcentaje: 18 },
];

const rangos = [
  { parametro: "Capacidad Villavicencio", actual: "300 t", rango: "255 – 330 t" },
  { parametro: "Capacidad Restrepo", actual: "180 t", rango: "150 – 215 t" },
  { parametro: "Costo de transporte k", actual: "350", rango: "305 – 398 COP/t·km" },
  { parametro: "Oferta total", actual: "890 t", rango: "830 – 950 t" },
];

const rutasCercanas = [
  { ruta: "E07 Cabuyaro → Restrepo", costo: "0" },
  { ruta: "E06 Cumural → Villavicencio", costo: "700" },
  { ruta: "E01 Barranca de Upía → Villavicencio", costo: "700" },
  { ruta: "E03 San Martín → Villavicencio", costo: "700" },
  { ruta: "E04 San Carlos → Granada", costo: "2.750" },
];

export function SensibilidadPage() {
  const [tipo, setTipo] = useState("transporte");
  const [aplicar, setAplicar] = useState("todas");
  const [variacion, setVariacion] = useState(20);

  return (
    <>
      <PageHero
        eyebrow="Sensibilidad · HU-11 · HU-12"
        title="Análisis de sensibilidad"
        description="Cambia costos, oferta o capacidad y observa cómo reacciona el óptimo con ambos métodos"
        kpis={[
          { valor: "$64.691.000", etiqueta: "Caso base" },
          { valor: "4", etiqueta: "Escenarios" },
          { valor: "2", etiqueta: "Métodos" },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <Etiqueta variante="alerta">
            Resultados por escenario y rangos de estabilidad ilustrativos
          </Etiqueta>
          <Boton>Ejecutar con ambos métodos</Boton>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[400px_minmax(0,1fr)]">
          <Tarjeta>
            <h2 className="type-title-22 text-text">Nuevo escenario</h2>

            <div className="mt-4 space-y-4">
              <div>
                <p className="type-label mb-1 text-text">Qué quieres variar</p>
                <Segmentado
                  items={tipoItems}
                  value={tipo}
                  onChange={setTipo}
                  ariaLabel="Qué quieres variar"
                  className="w-full"
                />
              </div>

              <Campo
                etiqueta="Nombre del escenario"
                defaultValue="Combustible +20 %"
                ayuda="Se guarda en el historial"
              />

              <div>
                <div className="flex items-center justify-between gap-2">
                  <p className="type-label text-text">Variación del costo de transporte k</p>
                  <span className="text-sm font-semibold tabular-nums text-primary">
                    {variacion > 0 ? `+${variacion}` : variacion} %
                  </span>
                </div>
                <input
                  type="range"
                  min={-30}
                  max={30}
                  step={1}
                  value={variacion}
                  onChange={(event) => setVariacion(Number(event.target.value))}
                  aria-label="Variación del costo de transporte"
                  className="mt-2 w-full accent-primary"
                />
                <div className="flex justify-between text-xs leading-4 text-muted">
                  <span>−30 %</span>
                  <span>0</span>
                  <span>+30 %</span>
                </div>
              </div>

              <div>
                <p className="type-label mb-1 text-text">Aplicar a</p>
                <Segmentado
                  items={aplicarItems}
                  value={aplicar}
                  onChange={setAplicar}
                  ariaLabel="Aplicar el escenario a"
                  className="w-full"
                />
              </div>

              <div className="rounded-card bg-primary-soft p-4">
                <p className="type-title-15 text-primary-dark">Qué cambia</p>
                <p className="mt-1 text-xs leading-4 text-primary-dark/80">
                  k pasa de 350 a 420 COP/t·km y las 40 rutas se recalculan. Se resuelve con el
                  modelo exacto y con el AG.
                </p>
              </div>

              <Boton variante="secundario">Guardar escenario</Boton>
            </div>
          </Tarjeta>

          <div className="min-w-0 space-y-4">
            <Tarjeta>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="type-title-15 text-text">Resultados por escenario</h2>
                <p className="text-xs leading-4 text-muted">COP por semana</p>
              </div>

              <div className="mt-3 overflow-x-auto scroll-fino">
                <table className="tabla min-w-[640px]">
                  <thead>
                    <tr>
                      <th>Escenario</th>
                      <th className="text-right">Cambio</th>
                      <th className="text-right">Exacto</th>
                      <th className="text-right">AG</th>
                      <th className="text-right">Gap AG</th>
                      <th className="text-right">Δ vs base</th>
                    </tr>
                  </thead>
                  <tbody>
                    {escenarios.map((escenario) => (
                      <tr
                        key={escenario.nombre}
                        className={escenario.destacado ? "bg-primary-soft" : ""}
                      >
                        <td
                          className={[
                            "font-medium",
                            escenario.destacado ? "font-semibold text-primary-dark" : "text-text",
                          ].join(" ")}
                        >
                          {escenario.nombre}
                        </td>
                        <td className="text-right text-muted">{escenario.cambio}</td>
                        <td className="text-right font-semibold tabular-nums text-text">
                          {escenario.exacto}
                        </td>
                        <td className="text-right tabular-nums text-text">{escenario.ag}</td>
                        <td className="text-right tabular-nums text-text">{escenario.gap}</td>
                        <td
                          className={[
                            "text-right font-semibold tabular-nums",
                            escenario.delta === "—" ? "text-muted" : "text-danger",
                          ].join(" ")}
                        >
                          {escenario.delta}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Tarjeta>

            <Tarjeta>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="type-title-15 text-text">
                  Impacto sobre el costo semanal (tornado)
                </h2>
                <ul className="flex items-center gap-4 text-xs leading-4 text-text">
                  <li className="inline-flex items-center gap-2">
                    <span aria-hidden="true" className="size-3 rounded-sm bg-primary" />
                    Baja el costo
                  </li>
                  <li className="inline-flex items-center gap-2">
                    <span aria-hidden="true" className="size-3 rounded-sm bg-accent" />
                    Sube el costo
                  </li>
                </ul>
              </div>

              <div className="mt-4 space-y-3">
                {tornado.map((fila) => (
                  <div
                    key={fila.etiqueta}
                    className="grid grid-cols-1 items-center gap-2 sm:grid-cols-[240px_minmax(0,1fr)] sm:gap-3"
                  >
                    <span className="text-[13px] leading-5 text-text">{fila.etiqueta}</span>
                    <div className="flex items-center gap-1.5">
                      <span className="w-14 shrink-0 whitespace-nowrap text-right text-xs tabular-nums text-text">
                        −{fila.valor}
                      </span>
                      <div className="flex flex-1 justify-end">
                        <div
                          className="h-6 rounded-l-sm bg-primary"
                          style={{ width: `${fila.porcentaje * 0.5}%` }}
                        />
                      </div>
                      <div aria-hidden="true" className="h-7 w-px bg-muted/60" />
                      <div className="flex flex-1">
                        <div
                          className="h-6 rounded-r-sm bg-accent"
                          style={{ width: `${fila.porcentaje * 0.5}%` }}
                        />
                      </div>
                      <span className="w-14 shrink-0 whitespace-nowrap text-xs tabular-nums text-text">
                        +{fila.valor}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Tarjeta>
          </div>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Tarjeta className="min-w-0">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="type-title-15 text-text">Rangos de estabilidad</h2>
              <Etiqueta variante="alerta">Ilustrativo</Etiqueta>
            </div>
            <div className="mt-3 overflow-x-auto scroll-fino">
              <table className="tabla min-w-[520px]">
                <thead>
                  <tr>
                    <th>Parámetro</th>
                    <th className="text-right">Valor actual</th>
                    <th className="text-right">Rango sin cambiar la base</th>
                  </tr>
                </thead>
                <tbody>
                  {rangos.map((rango) => (
                    <tr key={rango.parametro}>
                      <td className="font-medium text-text">{rango.parametro}</td>
                      <td className="text-right tabular-nums text-text">{rango.actual}</td>
                      <td className="text-right tabular-nums text-text">{rango.rango}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Tarjeta>

          <Tarjeta className="min-w-0">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="type-title-15 text-text">Rutas no usadas más cercanas a entrar</h2>
              <Etiqueta variante="exito">Del modelo base</Etiqueta>
            </div>
            <div className="mt-3 overflow-x-auto scroll-fino">
              <table className="tabla min-w-[440px]">
                <thead>
                  <tr>
                    <th>Ruta</th>
                    <th className="text-right">Costo reducido (COP/t)</th>
                  </tr>
                </thead>
                <tbody>
                  {rutasCercanas.map((ruta) => (
                    <tr key={ruta.ruta}>
                      <td className="font-medium text-text">{ruta.ruta}</td>
                      <td className="text-right font-semibold tabular-nums text-primary">
                        {ruta.costo}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-xs leading-4 text-muted">
              Costo reducido: cuánto debe bajar el costo de una ruta para que el modelo empiece a
              usarla.
            </p>
          </Tarjeta>
        </div>
      </PageBody>
    </>
  );
}
