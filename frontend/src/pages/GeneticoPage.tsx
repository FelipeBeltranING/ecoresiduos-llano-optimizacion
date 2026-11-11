import { FileSpreadsheet, FileText, Play, RotateCcw } from "lucide-react";
import { useState } from "react";

import {
  urlReporte,
  useEjecutarGenetico,
  useMatriz,
  useNodos,
  useUltimaEjecucion,
} from "@/api/hooks";
import type { ParametrosAG } from "@/api/tipos";
import { MapaReal } from "@/components/mapa/MapaReal";
import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { ConvergenciaChart } from "@/components/ui/ConvergenciaChart";
import { Cargando, ErrorApi, Vacio } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber } from "@/lib/format";
import { activos, descargar, usoDePlantas, ejecucionVigente } from "@/lib/red";

const POR_DEFECTO: ParametrosAG = {
  tamano_poblacion: 100,
  generaciones: 300,
  prob_cruce: 0.85,
  prob_mutacion: 0.1,
  elitismo: 2,
  semilla: 42,
  tipo_seleccion: "torneo",
  tipo_cruce: "un_punto",
};

type Texto = Record<
  "tamano_poblacion" | "generaciones" | "prob_cruce" | "prob_mutacion" | "elitismo" | "semilla",
  string
>;

const aTexto = (p: ParametrosAG): Texto => ({
  tamano_poblacion: String(p.tamano_poblacion),
  generaciones: String(p.generaciones),
  prob_cruce: String(p.prob_cruce).replace(".", ","),
  prob_mutacion: String(p.prob_mutacion).replace(".", ","),
  elitismo: String(p.elitismo),
  semilla: p.semilla == null ? "" : String(p.semilla),
});

const num = (t: string) => Number(t.replace(",", "."));

export function GeneticoPage() {
  const nodos = useNodos();
  const matriz = useMatriz();
  const ultimaAg = useUltimaEjecucion("GENETICO");
  const ultimoExacto = useUltimaEjecucion("EXACTO");
  const ejecutar = useEjecutarGenetico();
  const [texto, setTexto] = useState<Texto>(aTexto(POR_DEFECTO));
  const [seleccion, setSeleccion] = useState<ParametrosAG["tipo_seleccion"]>("torneo");
  const [cruce, setCruce] = useState<ParametrosAG["tipo_cruce"]>("un_punto");

  const detalle = ultimaAg.detalle.data;
  const optimo = ultimoExacto.detalle.data?.costo_total ?? null;
  const gap =
    detalle?.costo_total != null && optimo ? ((detalle.costo_total - optimo) / optimo) * 100 : null;
  const nodosActivos = activos(nodos.data);

  const errores: Partial<Record<keyof Texto, string>> = {};
  if (!(num(texto.tamano_poblacion) >= 10)) errores.tamano_poblacion = "Mínimo 10";
  if (!(num(texto.generaciones) >= 1)) errores.generaciones = "Mínimo 1";
  if (!(num(texto.prob_cruce) >= 0 && num(texto.prob_cruce) <= 1))
    errores.prob_cruce = "Entre 0 y 1";
  if (!(num(texto.prob_mutacion) >= 0 && num(texto.prob_mutacion) <= 1))
    errores.prob_mutacion = "Entre 0 y 1";
  if (!(num(texto.elitismo) >= 0 && num(texto.elitismo) < num(texto.tamano_poblacion)))
    errores.elitismo = "Menor que la población";
  const valido = Object.keys(errores).length === 0;

  const campo = (clave: keyof Texto, etiqueta: string, ayuda: string) => (
    <Campo
      etiqueta={etiqueta}
      value={texto[clave]}
      onChange={(e) => setTexto((t) => ({ ...t, [clave]: e.target.value }))}
      inputMode="decimal"
      estado={errores[clave] ? "error" : "normal"}
      ayuda={errores[clave] ?? ayuda}
    />
  );

  const lanzar = () =>
    ejecutar.mutate({
      tamano_poblacion: num(texto.tamano_poblacion),
      generaciones: num(texto.generaciones),
      prob_cruce: num(texto.prob_cruce),
      prob_mutacion: num(texto.prob_mutacion),
      elitismo: num(texto.elitismo),
      semilla: texto.semilla === "" ? null : num(texto.semilla),
      tipo_seleccion: seleccion,
      tipo_cruce: cruce,
    });

  return (
    <>
      <PageHero
        eyebrow="Algoritmo genético · HU-09 · HU-10"
        title="Algoritmo genético"
        description="Cromosoma = matriz de flujos; aptitud 1/(Z + λ·penalización); reparación por oferta y capacidad; elitismo y parada a las 50 generaciones sin mejora"
        kpis={[
          {
            valor: optimo ? formatCurrency(optimo) : "—",
            etiqueta: "Óptimo de referencia (exacto)",
          },
          {
            valor: detalle?.costo_total != null ? formatCurrency(detalle.costo_total) : "—",
            etiqueta: "Mejor costo del AG",
          },
          {
            valor: gap != null ? `${formatNumber(gap)} %` : "—",
            etiqueta: "Gap frente al óptimo",
            tono: "acento",
          },
        ]}
      />

      <PageBody>
        <div className="grid gap-4 xl:grid-cols-[340px_minmax(0,1fr)]">
          <Tarjeta>
            <h2 className="type-title-22 text-text">Parámetros</h2>
            <div className="mt-4 grid grid-cols-2 gap-3">
              {campo("tamano_poblacion", "Población", "Individuos")}
              {campo("generaciones", "Generaciones", "Máximo")}
              {campo("prob_cruce", "Tasa de cruce", "Entre 0 y 1")}
              {campo("prob_mutacion", "Tasa de mutación", "Entre 0 y 1")}
              {campo("elitismo", "Elitismo", "Individuos intactos")}
              {campo("semilla", "Semilla", "Vacía = aleatoria")}
            </div>
            <p className="mt-4 type-label text-text">Selección</p>
            <Segmentado
              className="mt-1"
              items={[
                { label: "Torneo (k = 3)", value: "torneo" },
                { label: "Ruleta", value: "ruleta" },
              ]}
              value={seleccion}
              onChange={(v) => setSeleccion(v as ParametrosAG["tipo_seleccion"])}
              ariaLabel="Tipo de selección"
            />
            <p className="mt-4 type-label text-text">Cruce</p>
            <Segmentado
              className="mt-1"
              items={[
                { label: "Un punto", value: "un_punto" },
                { label: "Dos puntos", value: "dos_puntos" },
              ]}
              value={cruce}
              onChange={(v) => setCruce(v as ParametrosAG["tipo_cruce"])}
              ariaLabel="Tipo de cruce"
            />
            <div className="mt-5 flex flex-wrap gap-2">
              <Boton
                icono={<Play className="size-4" aria-hidden="true" />}
                disabled={!valido || ejecutar.isPending}
                onClick={lanzar}
              >
                {ejecutar.isPending ? "Evolucionando…" : "Ejecutar AG"}
              </Boton>
              <Boton
                variante="secundario"
                icono={<RotateCcw className="size-4" aria-hidden="true" />}
                onClick={() => {
                  setTexto(aTexto(POR_DEFECTO));
                  setSeleccion("torneo");
                  setCruce("un_punto");
                }}
              >
                Restablecer
              </Boton>
            </div>
            {ejecutar.isError ? (
              <div className="mt-3">
                <ErrorApi error={ejecutar.error} />
              </div>
            ) : null}
          </Tarjeta>

          <div className="min-w-0 space-y-4">
            {ultimaAg.cargando ? <Cargando texto="Cargando la última corrida…" /> : null}
            {!ultimaAg.cargando && !detalle ? (
              <Vacio>Aún no hay corridas del AG sobre la red actual.</Vacio>
            ) : null}
            {detalle && !ejecucionVigente(detalle.flujos, nodosActivos) ? (
              <Etiqueta variante="alerta">
                La red cambió desde esta corrida: vuelva a ejecutar el AG
              </Etiqueta>
            ) : null}
            {detalle ? (
              <>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <KpiCard
                    etiqueta="Mejor costo"
                    valor={formatCurrency(detalle.costo_total ?? 0)}
                    tono="primario"
                  />
                  <KpiCard
                    etiqueta="Gap"
                    valor={gap != null ? `${formatNumber(gap)} %` : "—"}
                    detalle="Frente al exacto"
                    tono="acento"
                  />
                  <KpiCard
                    etiqueta="Tiempo"
                    valor={`${formatNumber((detalle.tiempo_ms ?? 0) / 1000)} s`}
                    detalle={`${detalle.convergencia.length} generaciones`}
                  />
                  <KpiCard
                    etiqueta="Violaciones"
                    valor={formatNumber(detalle.violaciones ?? 0)}
                    detalle="Oferta y capacidad"
                    tono={(detalle.violaciones ?? 0) > 1e-3 ? "peligro" : "texto"}
                  />
                </div>
                <Tarjeta>
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h2 className="type-title-15 text-text">Convergencia (HU-10)</h2>
                    <div className="flex flex-wrap items-center gap-2">
                      <Etiqueta variante="neutral">
                        {detalle.parametros?.tipo_seleccion ?? "torneo"} ·{" "}
                        {detalle.parametros?.tipo_cruce ?? "un_punto"} · semilla{" "}
                        {detalle.parametros?.semilla ?? "—"}
                      </Etiqueta>
                      <Boton
                        variante="fantasma"
                        icono={<FileSpreadsheet className="size-4" aria-hidden="true" />}
                        onClick={() => descargar(urlReporte("ejecuciones", detalle.id, "xlsx"))}
                      >
                        Excel
                      </Boton>
                      <Boton
                        variante="fantasma"
                        icono={<FileText className="size-4" aria-hidden="true" />}
                        onClick={() => descargar(urlReporte("ejecuciones", detalle.id, "pdf"))}
                      >
                        PDF
                      </Boton>
                    </div>
                  </div>
                  <ConvergenciaChart
                    className="mt-4"
                    optimo={optimo}
                    puntos={detalle.convergencia.map((c) => ({
                      generacion: c.generacion,
                      mejor: c.mejor_costo,
                      promedio: c.costo_promedio,
                    }))}
                  />
                </Tarjeta>
                <Tarjeta>
                  <h2 className="type-title-15 text-text">Mejor solución del AG en el mapa</h2>
                  <div className="mt-3">
                    <MapaReal
                      nodos={nodosActivos}
                      rutas={matriz.data?.rutas}
                      flujos={detalle.flujos}
                      usoPlantas={usoDePlantas(nodosActivos, detalle.flujos)}
                      alto="h-[360px]"
                    />
                  </div>
                </Tarjeta>
              </>
            ) : null}
          </div>
        </div>
      </PageBody>
    </>
  );
}
