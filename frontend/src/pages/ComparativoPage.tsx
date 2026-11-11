import { FileSpreadsheet, FileText, Gauge, Scale } from "lucide-react";
import { useState } from "react";

import {
  urlReporte,
  useAnalisis,
  useEscenarios,
  useIniciarAnalisis,
  useListaAnalisis,
} from "@/api/hooks";
import type { FilaEscalabilidad, ResultadoComparacion } from "@/api/tipos";
import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { ConvergenciaChart } from "@/components/ui/ConvergenciaChart";
import { Cargando, ErrorApi, Vacio } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber } from "@/lib/format";
import { descargar, formatoFecha } from "@/lib/red";

function Descargas({ id }: { id: string }) {
  return (
    <div className="flex gap-1">
      <Boton
        variante="fantasma"
        icono={<FileSpreadsheet className="size-4" aria-hidden="true" />}
        onClick={() => descargar(urlReporte("analisis", id, "xlsx"))}
      >
        Excel
      </Boton>
      <Boton
        variante="fantasma"
        icono={<FileText className="size-4" aria-hidden="true" />}
        onClick={() => descargar(urlReporte("analisis", id, "pdf"))}
      >
        PDF
      </Boton>
    </div>
  );
}

function BarrasTiempo({ filas }: { filas: FilaEscalabilidad[] }) {
  const maximo = Math.max(1, ...filas.flatMap((f) => [f.tiempo_exacto_ms, f.tiempo_ag_ms]));
  return (
    <div className="space-y-3" aria-label="Tiempo de cómputo por tamaño de red">
      {filas.map((f) => (
        <div key={f.variables} className="grid grid-cols-[80px_1fr] items-center gap-3 text-xs">
          <span className="font-semibold text-text">
            {f.empresas} × {f.plantas}
          </span>
          <div className="space-y-1">
            {[
              { valor: f.tiempo_exacto_ms, clase: "bg-primary", nombre: "Exacto" },
              { valor: f.tiempo_ag_ms, clase: "bg-accent", nombre: "AG" },
            ].map((b) => (
              <div key={b.nombre} className="flex items-center gap-2">
                <div
                  className={["h-3 rounded", b.clase].join(" ")}
                  style={{ width: `${Math.max(1, (b.valor / maximo) * 100)}%` }}
                />
                <span className="shrink-0 tabular-nums text-muted">
                  {b.nombre} {formatNumber(b.valor)} ms
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export function ComparativoPage() {
  const escenarios = useEscenarios();
  const iniciar = useIniciarAnalisis();
  const comparaciones = useListaAnalisis("COMPARACION");
  const escalas = useListaAnalisis("ESCALABILIDAD");
  const [corridas, setCorridas] = useState("5");
  const [escenarioId, setEscenarioId] = useState("");

  const idComparacion = comparaciones.data?.[0]?.id;
  const idEscala = escalas.data?.[0]?.id;
  const comparacion = useAnalisis<ResultadoComparacion>(idComparacion);
  const escala = useAnalisis<{ filas: FilaEscalabilidad[] }>(idEscala);
  const r = comparacion.data?.estado === "Terminado" ? comparacion.data.resultado : null;
  const filas = escala.data?.estado === "Terminado" ? (escala.data.resultado?.filas ?? []) : [];

  return (
    <>
      <PageHero
        eyebrow="Comparación · HU-13 · HU-14 · HU-16"
        title="Exacto frente a algoritmo genético"
        description="Calidad de la función objetivo, tiempo de cómputo, violaciones y escalabilidad. Gap = (Z_AG − Z*) / Z* × 100"
        kpis={[
          { valor: r ? formatCurrency(r.exacto.costo) : "—", etiqueta: "Z* exacto" },
          {
            valor: r ? `${formatNumber(r.ag.gap_promedio)} %` : "—",
            etiqueta: "Gap promedio del AG",
            tono: "acento",
          },
          {
            valor: r
              ? `${formatNumber(r.ag.tiempo_promedio_ms / Math.max(r.exacto.tiempo_ms, 1))}×`
              : "—",
            etiqueta: "Tiempo AG / exacto",
          },
        ]}
      />

      <PageBody>
        <div className="grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
          <Tarjeta>
            <h2 className="type-title-18 text-text">Reporte comparativo</h2>
            <div className="mt-3 space-y-3">
              <Campo
                etiqueta="Corridas del AG"
                value={corridas}
                onChange={(e) => setCorridas(e.target.value)}
                inputMode="numeric"
                ayuda="Semillas 0, 1, 2, …"
              />
              <label className="flex flex-col gap-1">
                <span className="type-label text-text">Escenario</span>
                <select
                  className="h-10 rounded-control border border-border bg-surface px-2 text-sm"
                  value={escenarioId}
                  onChange={(e) => setEscenarioId(e.target.value)}
                >
                  <option value="">Red base</option>
                  {(escenarios.data ?? []).map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.nombre}
                    </option>
                  ))}
                </select>
              </label>
              <Boton
                icono={<Scale className="size-4" aria-hidden="true" />}
                disabled={iniciar.isPending || comparacion.data?.estado === "En curso"}
                onClick={() =>
                  iniciar.mutate({
                    tipo: "comparacion",
                    entrada: {
                      corridas: Number(corridas) || 5,
                      escenario_id: escenarioId || null,
                      parametros_ag: { semilla: 0 },
                    },
                  })
                }
              >
                Generar comparativo
              </Boton>
              <hr className="border-border" />
              <h3 className="type-title-15 text-text">Escalabilidad</h3>
              <p className="text-xs text-muted">
                Instancias sintéticas del Meta: 10×4, 25×8, 50×10 y 100×20 (semilla 7).
              </p>
              <Boton
                variante="secundario"
                icono={<Gauge className="size-4" aria-hidden="true" />}
                disabled={iniciar.isPending || escala.data?.estado === "En curso"}
                onClick={() => iniciar.mutate({ tipo: "escalabilidad", entrada: {} })}
              >
                Evaluar escalabilidad
              </Boton>
              {iniciar.isError ? <ErrorApi error={iniciar.error} /> : null}
            </div>
          </Tarjeta>

          <div className="min-w-0 space-y-4">
            <Tarjeta relleno="none" className="overflow-hidden">
              <div className="flex flex-wrap items-center justify-between gap-2 px-5 pt-5">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="type-title-15 text-text">Exacto vs. AG</h2>
                  {comparacion.data ? (
                    <Etiqueta
                      variante={
                        comparacion.data.estado === "Error"
                          ? "peligro"
                          : comparacion.data.estado === "En curso"
                            ? "alerta"
                            : "exito"
                      }
                    >
                      {comparacion.data.estado} · {formatoFecha(comparacion.data.creado_en)}
                    </Etiqueta>
                  ) : null}
                </div>
                {idComparacion && r ? <Descargas id={idComparacion} /> : null}
              </div>
              <div className="p-5 pt-3">
                {comparaciones.isLoading ? <Cargando /> : null}
                {!idComparacion && !comparaciones.isLoading ? (
                  <Vacio>Genere el primer reporte comparativo.</Vacio>
                ) : null}
                {comparacion.data?.estado === "En curso" ? (
                  <Cargando texto="Ejecutando el exacto y las corridas del AG…" />
                ) : null}
                {comparacion.data?.estado === "Error" ? (
                  <ErrorApi error={new Error(comparacion.data.resultado?.error ?? "Error")} />
                ) : null}
                {r ? (
                  <div className="overflow-x-auto scroll-fino">
                    <table className="tabla tabla--compacta min-w-[520px]">
                      <thead>
                        <tr>
                          <th>Métrica</th>
                          <th className="text-right">Modelo exacto</th>
                          <th className="text-right">
                            Algoritmo genético ({r.ag.corridas.length} corridas)
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>Costo (COP/semana)</td>
                          <td className="text-right tabular-nums">
                            {formatCurrency(r.exacto.costo)}
                          </td>
                          <td className="text-right tabular-nums">
                            mejor {formatCurrency(r.ag.mejor)} · prom.{" "}
                            {formatCurrency(r.ag.promedio)}
                          </td>
                        </tr>
                        <tr>
                          <td>Desviación estándar</td>
                          <td className="text-right">—</td>
                          <td className="text-right tabular-nums">
                            {formatCurrency(r.ag.desviacion)}
                          </td>
                        </tr>
                        <tr>
                          <td>Gap frente al óptimo</td>
                          <td className="text-right">0 %</td>
                          <td className="text-right tabular-nums">
                            mejor {formatNumber(r.ag.gap_mejor)} % · prom.{" "}
                            {formatNumber(r.ag.gap_promedio)} %
                          </td>
                        </tr>
                        <tr>
                          <td>Tiempo de cómputo</td>
                          <td className="text-right tabular-nums">
                            {formatNumber(r.exacto.tiempo_ms)} ms
                          </td>
                          <td className="text-right tabular-nums">
                            {formatNumber(r.ag.tiempo_promedio_ms)} ms por corrida
                          </td>
                        </tr>
                        <tr>
                          <td>Violaciones de restricciones</td>
                          <td className="text-right tabular-nums">
                            {formatNumber(r.exacto.violaciones)}
                          </td>
                          <td className="text-right tabular-nums">
                            máx. {formatNumber(r.ag.violaciones_max)}
                          </td>
                        </tr>
                        <tr>
                          <td>Red</td>
                          <td colSpan={2} className="text-right">
                            {r.red.empresas} empresas × {r.red.plantas} plantas
                            {r.red.usa_planta_ficticia ? " (incluye ficticia)" : ""}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                ) : null}
              </div>
            </Tarjeta>

            {r ? (
              <Tarjeta>
                <h2 className="type-title-15 text-text">Convergencia de la mejor corrida</h2>
                <ConvergenciaChart
                  className="mt-3"
                  optimo={r.exacto.costo}
                  puntos={r.ag.convergencia_mejor}
                />
                <div className="mt-4 overflow-x-auto scroll-fino">
                  <table className="tabla tabla--compacta min-w-[460px]">
                    <thead>
                      <tr>
                        <th>Semilla</th>
                        <th className="text-right">Costo</th>
                        <th className="text-right">Gap</th>
                        <th className="text-right">Tiempo</th>
                        <th className="text-right">Generaciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {r.ag.corridas.map((c) => (
                        <tr key={c.semilla}>
                          <td>{c.semilla}</td>
                          <td className="text-right tabular-nums">{formatCurrency(c.costo)}</td>
                          <td className="text-right tabular-nums">{formatNumber(c.gap)} %</td>
                          <td className="text-right tabular-nums">
                            {formatNumber(c.tiempo_ms)} ms
                          </td>
                          <td className="text-right tabular-nums">{c.generaciones}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Tarjeta>
            ) : null}

            <Tarjeta relleno="none" className="overflow-hidden">
              <div className="flex flex-wrap items-center justify-between gap-2 px-5 pt-5">
                <h2 className="type-title-15 text-text">Escalabilidad (HU-14)</h2>
                {idEscala && filas.length ? <Descargas id={idEscala} /> : null}
              </div>
              <div className="p-5 pt-3">
                {escala.data?.estado === "En curso" ? (
                  <Cargando texto="Resolviendo instancias sintéticas…" />
                ) : null}
                {escala.data?.estado === "Error" ? (
                  <ErrorApi error={new Error(escala.data.resultado?.error ?? "Error")} />
                ) : null}
                {!idEscala && !escalas.isLoading ? (
                  <Vacio>Evalúe la escalabilidad para ver tiempos y gap por tamaño.</Vacio>
                ) : null}
                {filas.length ? (
                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="overflow-x-auto scroll-fino">
                      <table className="tabla tabla--compacta min-w-[420px]">
                        <thead>
                          <tr>
                            <th>Tamaño</th>
                            <th className="text-right">Variables</th>
                            <th className="text-right">Exacto</th>
                            <th className="text-right">AG</th>
                            <th className="text-right">Gap</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filas.map((f) => (
                            <tr key={f.variables}>
                              <td className="font-semibold">
                                {f.empresas} × {f.plantas}
                              </td>
                              <td className="text-right tabular-nums">{f.variables}</td>
                              <td className="text-right tabular-nums">
                                {formatNumber(f.tiempo_exacto_ms)} ms
                              </td>
                              <td className="text-right tabular-nums">
                                {formatNumber(f.tiempo_ag_ms)} ms
                              </td>
                              <td className="text-right tabular-nums">{formatNumber(f.gap)} %</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <BarrasTiempo filas={filas} />
                  </div>
                ) : null}
              </div>
            </Tarjeta>
          </div>
        </div>
      </PageBody>
    </>
  );
}
