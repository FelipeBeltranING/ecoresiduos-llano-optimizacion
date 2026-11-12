import { FileSpreadsheet, FileText, Play } from "lucide-react";

import {
  urlReporte,
  useEjecutarExacto,
  useMatriz,
  useNodos,
  useUltimaEjecucion,
  useValidacion,
} from "@/api/hooks";
import { MapaReal } from "@/components/mapa/MapaReal";
import { Barra } from "@/components/ui/Barra";
import { Boton } from "@/components/ui/Boton";
import { Cargando, ErrorApi, Vacio } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { FilaValidacion } from "@/components/ui/FilaValidacion";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber } from "@/lib/format";
import {
  CODIGO_FICTICIA,
  activos,
  descargar,
  formatoFecha,
  usoDePlantas,
  valorSensibilidad,
  ejecucionVigente,
} from "@/lib/red";

export function ExactoPage() {
  const nodos = useNodos();
  const matriz = useMatriz();
  const validacion = useValidacion();
  const ultima = useUltimaEjecucion("EXACTO");
  const ejecutar = useEjecutarExacto();
  const detalle = ultima.detalle.data;

  const nodosActivos = activos(nodos.data);
  const empresas = nodosActivos.filter((n) => n.tipo === "FUENTE");
  const plantas = nodosActivos.filter((n) => n.tipo === "PLANTA");
  const flujos = detalle?.flujos ?? [];
  const uso = usoDePlantas(nodosActivos, flujos);
  const columnas = [
    ...plantas.map((p) => p.codigo),
    ...(flujos.some((f) => f.destino === CODIGO_FICTICIA) ? [CODIGO_FICTICIA] : []),
  ];
  const costoPorPlanta = columnas.map((codigo) => ({
    codigo,
    costo: flujos
      .filter((f) => f.destino === codigo)
      .reduce((s, f) => s + f.toneladas * f.costo_unitario, 0),
  }));
  const costoTotal = detalle?.costo_total ?? 0;
  const ficticia = flujos
    .filter((f) => f.destino === CODIGO_FICTICIA)
    .reduce((s, f) => s + f.toneladas, 0);

  return (
    <>
      <PageHero
        eyebrow="Optimización exacta · HU-06 · HU-07 · HU-08"
        title="Resultado del modelo exacto"
        description={
          detalle
            ? `Programación lineal con PuLP + CBC · ${formatoFecha(detalle.creado_en)} · ${formatNumber(detalle.tiempo_ms ?? 0)} ms`
            : "Programación lineal con PuLP + CBC"
        }
        kpis={[
          { valor: detalle?.estado ?? "—", etiqueta: "Estado del solver" },
          { valor: detalle ? formatCurrency(costoTotal) : "—", etiqueta: "Costo semanal Z*" },
          {
            valor: detalle ? `${flujos.length} de ${matriz.data?.rutas.length ?? "—"}` : "—",
            etiqueta: "Rutas con flujo",
          },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap items-center gap-3">
            {detalle && !ejecucionVigente(flujos, nodosActivos) ? (
              <Etiqueta variante="alerta">
                La red cambió desde esta ejecución: vuelva a ejecutar
              </Etiqueta>
            ) : null}
            {detalle ? (
              <>
                <Etiqueta variante={detalle.estado === "Óptimo" ? "exito" : "peligro"}>
                  {detalle.estado === "Óptimo" ? "Solución óptima encontrada" : detalle.estado}
                </Etiqueta>
                <p className="text-xs leading-4 text-muted">
                  {formatNumber(detalle.violaciones ?? 0)} violaciones de restricciones ·{" "}
                  {ficticia > 0
                    ? `${formatNumber(ficticia)} t a la planta ficticia`
                    : "sin planta ficticia"}
                </p>
              </>
            ) : null}
            {validacion.data && !validacion.data.es_valida ? (
              <Etiqueta variante="peligro">La red tiene nodos aislados</Etiqueta>
            ) : null}
          </div>
          <div className="flex flex-wrap gap-2">
            <Boton
              variante="acento"
              disabled={!ultima.id}
              icono={<FileSpreadsheet className="size-4" aria-hidden="true" />}
              onClick={() => ultima.id && descargar(urlReporte("ejecuciones", ultima.id, "xlsx"))}
            >
              Descargar Excel
            </Boton>
            <Boton
              variante="acento"
              disabled={!ultima.id}
              icono={<FileText className="size-4" aria-hidden="true" />}
              onClick={() => ultima.id && descargar(urlReporte("ejecuciones", ultima.id, "pdf"))}
            >
              Descargar PDF
            </Boton>
            <Boton
              icono={<Play className="size-4" aria-hidden="true" />}
              disabled={ejecutar.isPending}
              onClick={() => ejecutar.mutate()}
            >
              {ejecutar.isPending
                ? "Resolviendo…"
                : detalle
                  ? "Volver a ejecutar"
                  : "Ejecutar modelo exacto"}
            </Boton>
          </div>
        </div>
        {ejecutar.isError ? (
          <div className="mt-3">
            <ErrorApi error={ejecutar.error} />
          </div>
        ) : null}

        {ultima.cargando ? (
          <div className="mt-6">
            <Cargando texto="Cargando la última ejecución…" />
          </div>
        ) : !detalle ? (
          <div className="mt-6">
            <Vacio>Aún no hay ejecuciones del modelo exacto sobre la red actual.</Vacio>
          </div>
        ) : (
          <>
            <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
              <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
                <h2 className="px-5 pt-5 type-title-15 text-text">
                  Flujos óptimos x<sub>ij</sub> (toneladas por semana)
                </h2>
                <div className="mt-4 overflow-x-auto scroll-fino">
                  <table
                    className="tabla tabla--compacta"
                    style={{ minWidth: 220 + columnas.length * 110 }}
                  >
                    <thead>
                      <tr>
                        <th className="w-[220px]">Empresa</th>
                        {columnas.map((c) => (
                          <th key={c} className="text-right">
                            {c === CODIGO_FICTICIA ? "Ficticia" : c}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {empresas.map((empresa) => (
                        <tr key={empresa.codigo}>
                          <td>
                            <span className="font-semibold">{empresa.codigo}</span>{" "}
                            <span className="text-xs text-muted">{empresa.nombre}</span>
                          </td>
                          {columnas.map((c) => {
                            const flujo = flujos.find(
                              (f) => f.origen === empresa.codigo && f.destino === c,
                            );
                            return (
                              <td
                                key={c}
                                className={[
                                  "text-right tabular-nums",
                                  flujo
                                    ? c === CODIGO_FICTICIA
                                      ? "bg-danger-soft font-semibold"
                                      : "bg-primary-soft font-semibold"
                                    : "text-muted",
                                ].join(" ")}
                              >
                                {flujo ? formatNumber(flujo.toneladas) : "—"}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                      <tr className="bg-bg">
                        <td className="font-semibold">Uso / capacidad (t)</td>
                        {columnas.map((c) => (
                          <td key={c} className="text-right font-semibold tabular-nums">
                            {uso[c]
                              ? `${formatNumber(uso[c].uso)} / ${formatNumber(uso[c].capacidad)}`
                              : formatNumber(ficticia)}
                          </td>
                        ))}
                      </tr>
                      <tr className="bg-bg">
                        <td className="font-semibold">Precio sombra (COP/t)</td>
                        {columnas.map((c) => {
                          const dual = valorSensibilidad(detalle.sensibilidad, "DUAL_CAPACIDAD", c);
                          return (
                            <td
                              key={c}
                              className={[
                                "text-right font-semibold tabular-nums",
                                dual && dual.valor < 0 ? "text-danger" : "",
                              ].join(" ")}
                            >
                              {dual ? formatNumber(dual.valor) : "—"}
                            </td>
                          );
                        })}
                      </tr>
                    </tbody>
                  </table>
                </div>
              </Tarjeta>

              <Tarjeta>
                <h2 className="type-title-15 text-text">Red con flujos óptimos (mapa real)</h2>
                <div className="mt-3">
                  <MapaReal
                    nodos={nodosActivos}
                    rutas={matriz.data?.rutas}
                    flujos={flujos}
                    usoPlantas={uso}
                    alto="h-[400px]"
                    etiqueta="Flujos óptimos del modelo exacto sobre OpenStreetMap"
                  />
                </div>
                <p className="mt-3 text-xs leading-4 text-muted">
                  El grosor es proporcional a las toneladas; el trazado sigue la vía real (OSRM).
                  Rojo: planta saturada.
                </p>
              </Tarjeta>
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-2">
              <Tarjeta>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h2 className="type-title-15 text-text">Dónde se va el costo</h2>
                  <p className="text-xs text-muted">
                    Suma: {formatCurrency(costoTotal)} por semana
                  </p>
                </div>
                <div className="mt-4 space-y-4">
                  {costoPorPlanta.map(({ codigo, costo }) => (
                    <div key={codigo} className="flex items-center gap-3">
                      <span className="w-20 shrink-0 text-[13px]">
                        {codigo === CODIGO_FICTICIA ? "Ficticia" : codigo}
                      </span>
                      <Barra
                        valor={costoTotal ? costo / costoTotal : 0}
                        className="flex-1"
                        etiqueta={`Costo de ${codigo}`}
                        tono={codigo === CODIGO_FICTICIA ? "peligro" : "primario"}
                      />
                      <span className="w-[120px] shrink-0 text-right text-[13px] font-semibold tabular-nums">
                        {formatCurrency(costo)}
                      </span>
                    </div>
                  ))}
                </div>
              </Tarjeta>

              <Tarjeta>
                <h2 className="type-title-15 text-text">Holguras y cuellos de botella</h2>
                <div className="mt-4 space-y-4">
                  {plantas.map((planta) => {
                    const holgura = valorSensibilidad(
                      detalle.sensibilidad,
                      "HOLGURA_CAPACIDAD",
                      planta.codigo,
                    );
                    const dual = valorSensibilidad(
                      detalle.sensibilidad,
                      "DUAL_CAPACIDAD",
                      planta.codigo,
                    );
                    const saturada = (holgura?.valor ?? 1) <= 1e-6;
                    return (
                      <FilaValidacion
                        key={planta.codigo}
                        estado={saturada ? "alerta" : "correcto"}
                        titulo={`${planta.codigo} · ${planta.nombre}: ${saturada ? "sin holgura" : `${formatNumber(holgura?.valor ?? 0)} t libres`}`}
                        nota={
                          saturada && dual
                            ? `Cada tonelada extra de capacidad ahorraría ${formatCurrency(-dual.valor)} por semana`
                            : "Precio sombra 0: ampliarla no reduce el costo"
                        }
                      />
                    );
                  })}
                </div>
              </Tarjeta>
            </div>
          </>
        )}
      </PageBody>
    </>
  );
}
