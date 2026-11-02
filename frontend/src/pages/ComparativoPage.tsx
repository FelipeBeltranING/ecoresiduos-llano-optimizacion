import { Boton } from "@/components/ui/Boton";
import { Barra } from "@/components/ui/Barra";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { FilaValidacion } from "@/components/ui/FilaValidacion";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Tarjeta } from "@/components/ui/Tarjeta";

const comparacion = [
  {
    metrica: "Costo total (COP/semana)",
    exacto: "64.691.000",
    ag: "65.012.000 (mejor)",
  },
  { metrica: "Costo promedio del AG", exacto: "—", ag: "65.348.000 ± 214.000" },
  { metrica: "Tiempo de ejecución", exacto: "0,4 s", ag: "3,2 s" },
  { metrica: "Gap frente al óptimo", exacto: "0 %", ag: "0,50 % mejor · 1,02 % medio" },
  { metrica: "Violaciones de restricciones", exacto: "0", ag: "0 tras la reparación" },
  { metrica: "Garantiza el óptimo global", exacto: "Sí", ag: "No (cuasi-óptimo)" },
  { metrica: "Precios sombra y rangos", exacto: "Exactos", ag: "Por re-optimización" },
];

const gaps = [
  { escenario: "Caso base", pct: 0.5, texto: "0,50 %" },
  { escenario: "Combustible +20 %", pct: 0.58, texto: "0,58 %" },
  { escenario: "Oferta −10 %", pct: 0.66, texto: "0,66 %" },
  { escenario: "Villavicencio −20 %", pct: 0.52, texto: "0,52 %" },
];

const escalabilidad = [
  { tamano: "10 × 4 (caso base)", exacto: "0,4", ag: "3,2", gap: "0,50 %" },
  { tamano: "25 × 8", exacto: "0,9", ag: "6,0", gap: "1,10 %" },
  { tamano: "50 × 12", exacto: "2,6", ag: "12,5", gap: "2,40 %" },
  { tamano: "100 × 20", exacto: "9,8", ag: "41,0", gap: "4,80 %" },
];

export function ComparativoPage() {
  return (
    <>
      <PageHero
        eyebrow="Comparación · HU-13 · HU-16"
        title="Exacto frente a algoritmo genético"
        description="Reporte del caso base: calidad de la solución, tiempo, restricciones y escalabilidad"
        kpis={[
          { valor: "0,50 %", etiqueta: "Gap del mejor AG" },
          { valor: "10", etiqueta: "Corridas del AG" },
          { valor: "0", etiqueta: "Violaciones" },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <Etiqueta variante="alerta">Cifras del AG y de escalabilidad ilustrativas</Etiqueta>
          <div className="flex flex-wrap gap-2">
            <Boton variante="acento">Exportar Excel</Boton>
            <Boton variante="acento">Exportar PDF</Boton>
          </div>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1fr)_480px]">
          <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-2 px-5 pt-5">
              <h2 className="type-title-15 text-text">Comparación en el caso base</h2>
              <p className="text-xs leading-4 text-muted">AG: mejor y promedio de 10 corridas</p>
            </div>

            <div className="mt-4 hidden overflow-x-auto scroll-fino md:block">
              <table className="tabla min-w-[560px]">
                <thead>
                  <tr>
                    <th>Métrica</th>
                    <th className="w-[190px] text-right">Modelo exacto</th>
                    <th className="w-[230px] text-right">Algoritmo genético</th>
                  </tr>
                </thead>
                <tbody>
                  {comparacion.map((fila) => (
                    <tr key={fila.metrica}>
                      <td className="font-medium text-text">{fila.metrica}</td>
                      <td className="text-right font-semibold tabular-nums text-primary">
                        {fila.exacto}
                      </td>
                      <td className="text-right tabular-nums text-text">{fila.ag}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 space-y-3 px-4 pb-4 md:hidden">
              {comparacion.map((fila) => (
                <div key={fila.metrica} className="rounded-card border border-border p-4">
                  <p className="type-label text-muted">{fila.metrica}</p>
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    <div className="rounded-control bg-primary-soft p-3">
                      <p className="text-xs leading-4 text-primary-dark/80">Exacto</p>
                      <p className="mt-1 text-sm font-semibold leading-5 tabular-nums text-text">
                        {fila.exacto}
                      </p>
                    </div>
                    <div className="rounded-control bg-bg p-3">
                      <p className="text-xs leading-4 text-muted">AG</p>
                      <p className="mt-1 text-sm font-semibold leading-5 tabular-nums text-text">
                        {fila.ag}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-15 text-text">Gap del AG por escenario</h2>
            <p className="mt-1 text-xs leading-4 text-muted">
              (Z_AG − Z*) / Z* en cada escenario de sensibilidad
            </p>

            <div className="mt-4 space-y-4">
              {gaps.map((gap) => (
                <div key={gap.escenario}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[13px] font-medium leading-5 text-text">
                      {gap.escenario}
                    </span>
                    <span className="text-[13px] font-semibold tabular-nums text-text">
                      {gap.texto}
                    </span>
                  </div>
                  <Barra
                    valor={gap.pct}
                    className="mt-2"
                    etiqueta={`Gap del AG en ${gap.escenario}`}
                  />
                </div>
              ))}
            </div>

            <p className="mt-4 text-xs leading-4 text-muted">
              Escala de 0 a 1 %. Un gap menor a 1 % indica una solución muy cercana al óptimo.
            </p>
          </Tarjeta>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-2 px-5 pt-5">
              <h2 className="type-title-15 text-text">Escalabilidad con instancias sintéticas</h2>
              <p className="text-xs leading-4 text-muted">Empresas × plantas</p>
            </div>

            <div className="mt-4 overflow-x-auto scroll-fino">
              <table className="tabla min-w-[520px]">
                <thead>
                  <tr>
                    <th>Tamaño</th>
                    <th className="text-right">Exacto (s)</th>
                    <th className="text-right">AG (s)</th>
                    <th className="text-right">Gap del AG</th>
                  </tr>
                </thead>
                <tbody>
                  {escalabilidad.map((fila) => (
                    <tr key={fila.tamano}>
                      <td className="font-medium text-text">{fila.tamano}</td>
                      <td className="text-right font-semibold tabular-nums text-primary">
                        {fila.exacto}
                      </td>
                      <td className="text-right tabular-nums text-text">{fila.ag}</td>
                      <td className="text-right tabular-nums text-text">{fila.gap}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-15 text-text">Qué conviene usar</h2>
            <div className="mt-4 space-y-4">
              <FilaValidacion
                titulo="El exacto es la referencia"
                nota="Garantiza el óptimo y entrega precios sombra y rangos sin re-ejecutar."
              />
              <FilaValidacion
                titulo="El AG llega cerca en el caso base"
                nota="Termina a menos de 1 % del óptimo, sin violar restricciones."
              />
              <FilaValidacion
                estado="alerta"
                titulo="El gap del AG crece con la red"
                nota="En instancias grandes necesita más generaciones o ajuste de parámetros."
              />
            </div>
          </Tarjeta>
        </div>
      </PageBody>
    </>
  );
}
