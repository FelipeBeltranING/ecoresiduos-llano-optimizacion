import { FileSpreadsheet, FileText } from "lucide-react";
import { useState } from "react";

import {
  urlReporte,
  useEjecucion,
  useEjecuciones,
  useEscenarios,
  useListaAnalisis,
} from "@/api/hooks";
import type { Metodo } from "@/api/tipos";
import { Boton } from "@/components/ui/Boton";
import { Cargando, ErrorApi, Vacio } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber } from "@/lib/format";
import { descargar, formatoFecha } from "@/lib/red";

const TAMANO = 15;

function Detalle({ id }: { id: string }) {
  const detalle = useEjecucion(id);
  if (detalle.isLoading) return <Cargando />;
  if (detalle.isError) return <ErrorApi error={detalle.error} />;
  const d = detalle.data;
  if (!d) return null;
  return (
    <div className="space-y-3 text-sm">
      <div className="flex flex-wrap gap-2">
        <Etiqueta>{d.metodo === "EXACTO" ? "Exacto" : "Genético"}</Etiqueta>
        <Etiqueta variante="neutral">{d.estado}</Etiqueta>
      </div>
      <p className="text-2xl font-bold tabular-nums text-text">
        {formatCurrency(d.costo_total ?? 0)}
      </p>
      <p className="text-xs text-muted">
        {formatoFecha(d.creado_en)} · {formatNumber(d.tiempo_ms ?? 0)} ms ·{" "}
        {formatNumber(d.violaciones ?? 0)} violaciones
      </p>
      {d.parametros ? (
        <p className="text-xs text-muted">
          Población {d.parametros.tamano_poblacion}, generaciones {d.parametros.generaciones}, cruce{" "}
          {d.parametros.prob_cruce} ({d.parametros.tipo_cruce}), mutación{" "}
          {d.parametros.prob_mutacion}, selección {d.parametros.tipo_seleccion}, semilla{" "}
          {d.parametros.semilla ?? "—"}
        </p>
      ) : null}
      <div className="max-h-[260px] overflow-auto scroll-fino">
        <table className="tabla tabla--compacta">
          <thead>
            <tr>
              <th>Ruta</th>
              <th className="text-right">t</th>
              <th className="text-right">COP/t</th>
            </tr>
          </thead>
          <tbody>
            {d.flujos.map((f) => (
              <tr key={`${f.origen}-${f.destino}`}>
                <td>
                  {f.origen} → {f.destino}
                </td>
                <td className="text-right tabular-nums">{formatNumber(f.toneladas)}</td>
                <td className="text-right tabular-nums">{formatCurrency(f.costo_unitario)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex gap-2">
        <Boton
          variante="acento"
          icono={<FileSpreadsheet className="size-4" aria-hidden="true" />}
          onClick={() => descargar(urlReporte("ejecuciones", d.id, "xlsx"))}
        >
          Excel
        </Boton>
        <Boton
          variante="acento"
          icono={<FileText className="size-4" aria-hidden="true" />}
          onClick={() => descargar(urlReporte("ejecuciones", d.id, "pdf"))}
        >
          PDF
        </Boton>
      </div>
    </div>
  );
}

export function HistorialPage() {
  const [metodo, setMetodo] = useState<"" | Metodo>("");
  const [escenario, setEscenario] = useState("");
  const [desde, setDesde] = useState("");
  const [pagina, setPagina] = useState(1);
  const [seleccion, setSeleccion] = useState<string | null>(null);
  const escenarios = useEscenarios();
  const analisis = useListaAnalisis();
  const lista = useEjecuciones({
    metodo: metodo || undefined,
    escenario_id: escenario && escenario !== "base" ? escenario : undefined,
    solo_base: escenario === "base" || undefined,
    desde: desde ? new Date(`${desde}T00:00:00`).toISOString() : undefined,
    pagina,
    tamano: TAMANO,
  });
  const total = lista.data?.total ?? 0;
  const paginas = Math.max(1, Math.ceil(total / TAMANO));

  return (
    <>
      <PageHero
        eyebrow="Historial · HU-15 · HU-16"
        title="Historial y reportes"
        description="Cada ejecución guarda un snapshot de la red y sus parámetros (el AG guarda la semilla y es reproducible)"
        kpis={[
          { valor: String(total), etiqueta: "Ejecuciones (filtro actual)" },
          { valor: String(escenarios.data?.length ?? "—"), etiqueta: "Escenarios" },
          { valor: String(analisis.data?.length ?? "—"), etiqueta: "Análisis" },
        ]}
      />
      <PageBody>
        <div className="flex flex-wrap items-end gap-3">
          <Segmentado
            items={[
              { label: "Todos", value: "" },
              { label: "Exacto", value: "EXACTO" },
              { label: "Genético", value: "GENETICO" },
            ]}
            value={metodo}
            onChange={(v) => {
              setMetodo(v as "" | Metodo);
              setPagina(1);
            }}
            ariaLabel="Filtrar por método"
          />
          <label className="flex flex-col gap-1">
            <span className="type-label text-text">Escenario</span>
            <select
              className="h-10 rounded-control border border-border bg-surface px-2 text-sm"
              value={escenario}
              onChange={(e) => {
                setEscenario(e.target.value);
                setPagina(1);
              }}
            >
              <option value="">Todos</option>
              <option value="base">Solo red base</option>
              {(escenarios.data ?? []).map((e) => (
                <option key={e.id} value={e.id}>
                  {e.nombre}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="type-label text-text">Desde</span>
            <input
              type="date"
              className="h-10 rounded-control border border-border bg-surface px-2 text-sm"
              value={desde}
              onChange={(e) => {
                setDesde(e.target.value);
                setPagina(1);
              }}
            />
          </label>
        </div>

        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
            {lista.isLoading ? (
              <div className="p-5">
                <Cargando />
              </div>
            ) : null}
            {lista.isError ? (
              <div className="p-5">
                <ErrorApi error={lista.error} />
              </div>
            ) : null}
            {lista.data && lista.data.items.length === 0 ? (
              <div className="p-5">
                <Vacio>No hay ejecuciones con este filtro.</Vacio>
              </div>
            ) : null}
            {lista.data?.items.length ? (
              <div className="overflow-x-auto scroll-fino">
                <table className="tabla tabla--compacta min-w-[640px]">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Método</th>
                      <th>Escenario</th>
                      <th className="text-right">Costo</th>
                      <th className="text-right">Tiempo</th>
                      <th className="text-right">Violaciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lista.data.items.map((e) => (
                      <tr
                        key={e.id}
                        className={[
                          "cursor-pointer hover:bg-primary-soft",
                          seleccion === e.id ? "bg-primary-soft" : "",
                        ].join(" ")}
                        onClick={() => setSeleccion(e.id)}
                        tabIndex={0}
                        onKeyDown={(ev) => ev.key === "Enter" && setSeleccion(e.id)}
                      >
                        <td>{formatoFecha(e.creado_en)}</td>
                        <td>{e.metodo === "EXACTO" ? "Exacto" : "Genético"}</td>
                        <td className="text-xs text-muted">{e.escenario_nombre ?? "Red base"}</td>
                        <td className="text-right tabular-nums">
                          {e.costo_total != null ? formatCurrency(e.costo_total) : "—"}
                        </td>
                        <td className="text-right tabular-nums">
                          {formatNumber(e.tiempo_ms ?? 0)} ms
                        </td>
                        <td className="text-right tabular-nums">
                          {formatNumber(e.violaciones ?? 0)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
            <div className="flex items-center justify-between gap-2 px-5 py-3 text-xs text-muted">
              <span>
                Página {pagina} de {paginas}
              </span>
              <div className="flex gap-2">
                <Boton
                  variante="secundario"
                  disabled={pagina <= 1}
                  onClick={() => setPagina((p) => p - 1)}
                >
                  Anterior
                </Boton>
                <Boton
                  variante="secundario"
                  disabled={pagina >= paginas}
                  onClick={() => setPagina((p) => p + 1)}
                >
                  Siguiente
                </Boton>
              </div>
            </div>
          </Tarjeta>

          <div className="space-y-4">
            <Tarjeta>
              <h2 className="type-title-15 text-text">Detalle</h2>
              <div className="mt-3">
                {seleccion ? (
                  <Detalle id={seleccion} />
                ) : (
                  <Vacio>Elija una ejecución de la lista.</Vacio>
                )}
              </div>
            </Tarjeta>
            <Tarjeta>
              <h2 className="type-title-15 text-text">Análisis guardados</h2>
              <ul className="mt-3 space-y-2">
                {(analisis.data ?? []).slice(0, 8).map((a) => (
                  <li
                    key={a.id}
                    className="flex flex-wrap items-center justify-between gap-2 text-sm"
                  >
                    <span>
                      {a.tipo === "COMPARACION" ? "Comparativo" : "Escalabilidad"} ·{" "}
                      <span className="text-xs text-muted">
                        {formatoFecha(a.creado_en)} · {a.estado}
                      </span>
                    </span>
                    {a.estado === "Terminado" ? (
                      <span className="flex gap-1">
                        <Boton
                          variante="fantasma"
                          onClick={() => descargar(urlReporte("analisis", a.id, "xlsx"))}
                        >
                          Excel
                        </Boton>
                        <Boton
                          variante="fantasma"
                          onClick={() => descargar(urlReporte("analisis", a.id, "pdf"))}
                        >
                          PDF
                        </Boton>
                      </span>
                    ) : null}
                  </li>
                ))}
                {analisis.data?.length === 0 ? (
                  <li className="text-sm text-muted">Sin análisis todavía.</li>
                ) : null}
              </ul>
            </Tarjeta>
          </div>
        </div>
      </PageBody>
    </>
  );
}
