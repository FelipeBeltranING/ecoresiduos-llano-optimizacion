import { FlaskConical, Play, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import {
  useCalcularRangos,
  useCrearEscenario,
  useEjecutarEscenario,
  useEliminarEscenario,
  useEscenarios,
  useMatriz,
  useNodos,
  useTornado,
  useUltimaEjecucion,
} from "@/api/hooks";
import type { Ajuste, Rango, TipoAjuste } from "@/api/tipos";
import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { Cargando, ErrorApi, Vacio } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber } from "@/lib/format";
import { activos } from "@/lib/red";

const TIPOS: { value: TipoAjuste; label: string }[] = [
  { value: "COSTO_TRANSPORTE", label: "Combustible / transporte (k)" },
  { value: "OFERTA", label: "Oferta de residuos" },
  { value: "CAPACIDAD", label: "Capacidad de planta (cuello de botella)" },
  { value: "COSTO_RUTA", label: "Costo de una ruta" },
  { value: "CERRAR_RUTA", label: "Cerrar una ruta" },
];

const PRESETS: { nombre: string; ajustes: Ajuste[] }[] = [
  {
    nombre: "Combustible +20 %",
    ajustes: [{ tipo: "COSTO_TRANSPORTE", porcentaje: 20, objetivo: null }],
  },
  { nombre: "Oferta +10 %", ajustes: [{ tipo: "OFERTA", porcentaje: 10, objetivo: null }] },
];

const etiquetaTipo = (t: TipoAjuste) => TIPOS.find((x) => x.value === t)?.label ?? t;
const rango = (r: Rango) =>
  `${r.inferior == null ? "−∞" : formatNumber(r.inferior)} … ${r.superior == null ? "+∞" : formatNumber(r.superior)}`;

function Tornado() {
  const [porcentaje, setPorcentaje] = useState("20");
  const tornado = useTornado(Number(porcentaje));
  const datos = tornado.data;
  const maximo = datos
    ? Math.max(
        1,
        ...datos.impactos.flatMap((i) => [
          Math.abs((i.costo_menos ?? datos.costo_base) - datos.costo_base),
          Math.abs((i.costo_mas ?? datos.costo_base) - datos.costo_base),
        ]),
      )
    : 1;
  return (
    <Tarjeta>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="type-title-15 text-text">Gráfica de tornado: impacto en Z</h2>
        <Segmentado
          items={["10", "20", "30"].map((p) => ({ label: `±${p} %`, value: p }))}
          value={porcentaje}
          onChange={setPorcentaje}
          ariaLabel="Variación del tornado"
        />
      </div>
      {tornado.isLoading ? <Cargando /> : null}
      {tornado.isError ? <ErrorApi error={tornado.error} /> : null}
      {datos ? (
        <div
          className="mt-4 space-y-2"
          role="table"
          aria-label="Impacto de cada parámetro en el costo total"
        >
          {datos.impactos.slice(0, 10).map((i) => {
            const menos = (i.costo_menos ?? datos.costo_base) - datos.costo_base;
            const mas = (i.costo_mas ?? datos.costo_base) - datos.costo_base;
            const barra = (delta: number) => (
              <div
                className={["h-4 rounded", delta >= 0 ? "bg-danger/80" : "bg-primary/80"].join(" ")}
                style={{ width: `${(Math.abs(delta) / maximo) * 100}%` }}
                title={formatCurrency(delta)}
              />
            );
            return (
              <div
                key={i.parametro}
                role="row"
                className="grid grid-cols-[150px_1fr_1fr] items-center gap-2 text-[12px]"
              >
                <span role="cell" className="truncate text-text">
                  {i.parametro}
                </span>
                <div role="cell" className="flex justify-end">
                  {barra(menos)}
                </div>
                <div role="cell" className="flex">
                  {barra(mas)}
                </div>
              </div>
            );
          })}
          <p className="pt-2 text-xs text-muted">
            Izquierda: parámetro −{porcentaje} %; derecha: +{porcentaje} %. Rojo sube el costo,
            verde lo baja. Base {formatCurrency(datos.costo_base)}.
          </p>
        </div>
      ) : null}
    </Tarjeta>
  );
}

function Rangos() {
  const exacto = useUltimaEjecucion("EXACTO");
  const calcular = useCalcularRangos();
  const [vista, setVista] = useState<Rango["tipo"]>("CAPACIDAD");
  const filas = (calcular.data?.rangos ?? []).filter((r) => r.tipo === vista);
  return (
    <Tarjeta relleno="none" className="overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-2 px-5 pt-5">
        <div>
          <h2 className="type-title-15 text-text">
            Precios sombra, costos reducidos y rangos (HU-12)
          </h2>
          <p className="text-xs text-muted">
            Re-optimización paramétrica: hasta dónde puede moverse cada dato sin cambiar la base
            óptima
          </p>
        </div>
        <Boton
          disabled={!exacto.id || calcular.isPending}
          onClick={() => exacto.id && calcular.mutate(exacto.id)}
        >
          {calcular.isPending ? "Calculando…" : "Calcular rangos"}
        </Boton>
      </div>
      {calcular.isError ? (
        <div className="px-5 pt-3">
          <ErrorApi error={calcular.error} />
        </div>
      ) : null}
      {calcular.data ? (
        <>
          <div className="px-5 pt-4">
            <Segmentado
              items={[
                { label: "Capacidad", value: "CAPACIDAD" },
                { label: "Oferta", value: "OFERTA" },
                { label: "Costo de rutas", value: "COSTO_RUTA" },
              ]}
              value={vista}
              onChange={(v) => setVista(v as Rango["tipo"])}
              ariaLabel="Tipo de rango"
            />
          </div>
          <div className="mt-3 max-h-[360px] overflow-auto scroll-fino">
            <table className="tabla tabla--compacta min-w-[520px]">
              <thead>
                <tr>
                  <th>Elemento</th>
                  <th className="text-right">Valor actual</th>
                  <th className="text-right">
                    {vista === "COSTO_RUTA" ? "Costo reducido" : "Precio sombra"}
                  </th>
                  <th className="text-right">Rango de estabilidad</th>
                </tr>
              </thead>
              <tbody>
                {filas.map((r) => (
                  <tr key={r.elemento}>
                    <td className="font-semibold">{r.elemento}</td>
                    <td className="text-right tabular-nums">{formatNumber(r.valor)}</td>
                    <td
                      className={[
                        "text-right tabular-nums",
                        (r.dual_o_costo_reducido ?? 0) < 0 ? "text-danger" : "",
                      ].join(" ")}
                    >
                      {r.dual_o_costo_reducido == null
                        ? "—"
                        : formatNumber(r.dual_o_costo_reducido)}
                    </td>
                    <td className="text-right tabular-nums">{rango(r)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="p-5">
          <Vacio>
            {exacto.id
              ? "Calcule los rangos de la última ejecución del exacto."
              : "Ejecute primero el modelo exacto."}
          </Vacio>
        </div>
      )}
    </Tarjeta>
  );
}

export function SensibilidadPage() {
  const nodos = useNodos();
  const matriz = useMatriz();
  const escenarios = useEscenarios();
  const crear = useCrearEscenario();
  const eliminar = useEliminarEscenario();
  const ejecutar = useEjecutarEscenario();
  const [nombre, setNombre] = useState("");
  const [ajustes, setAjustes] = useState<Ajuste[]>([
    { tipo: "CAPACIDAD", porcentaje: -30, objetivo: null },
  ]);
  const [incluirAg, setIncluirAg] = useState(true);

  const nodosActivos = activos(nodos.data);
  const objetivos = (tipo: TipoAjuste): string[] => {
    if (tipo === "OFERTA")
      return nodosActivos.filter((n) => n.tipo === "FUENTE").map((n) => n.codigo);
    if (tipo === "CAPACIDAD")
      return nodosActivos.filter((n) => n.tipo === "PLANTA").map((n) => n.codigo);
    if (tipo === "COSTO_TRANSPORTE")
      return nodosActivos.filter((n) => n.tipo === "FUENTE").map((n) => n.codigo);
    return (matriz.data?.rutas ?? []).map((r) => `${r.origen}->${r.destino}`);
  };
  const exigeObjetivo = (t: TipoAjuste) => t === "COSTO_RUTA" || t === "CERRAR_RUTA";
  const resultado = ejecutar.data;

  const cambiarAjuste = (i: number, parcial: Partial<Ajuste>) =>
    setAjustes((lista) => lista.map((a, j) => (j === i ? { ...a, ...parcial } : a)));

  return (
    <>
      <PageHero
        eyebrow="Sensibilidad · HU-11 · HU-12"
        title="Análisis de sensibilidad"
        description="Combustible, oferta y cuellos de botella: cada escenario se resuelve con el exacto y el AG y se compara con la red base"
        kpis={[
          { valor: String(escenarios.data?.length ?? "—"), etiqueta: "Escenarios guardados" },
          {
            valor: resultado ? `${formatNumber(resultado.variacion_porcentual)} %` : "—",
            etiqueta: "Variación de Z (último)",
            tono: "acento",
          },
          {
            valor: resultado?.gap_ag != null ? `${formatNumber(resultado.gap_ag)} %` : "—",
            etiqueta: "Gap del AG (último)",
          },
        ]}
      />

      <PageBody>
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <Tarjeta>
            <h2 className="type-title-18 text-text">Nuevo escenario</h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {PRESETS.map((p) => (
                <Boton
                  key={p.nombre}
                  variante="secundario"
                  onClick={() => {
                    setNombre(p.nombre);
                    setAjustes(p.ajustes);
                  }}
                >
                  {p.nombre}
                </Boton>
              ))}
            </div>
            <form
              className="mt-4 space-y-3"
              onSubmit={(e) => {
                e.preventDefault();
                crear.mutate({ nombre, ajustes }, { onSuccess: () => setNombre("") });
              }}
            >
              <Campo
                etiqueta="Nombre del escenario"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                required
                minLength={3}
              />
              {ajustes.map((ajuste, i) => (
                <div
                  key={i}
                  className="grid gap-2 rounded-control border border-border p-3 sm:grid-cols-[1.4fr_1fr_100px_auto] sm:items-end"
                >
                  <label className="flex flex-col gap-1 text-xs">
                    <span className="type-label text-text">Ajuste</span>
                    <select
                      className="h-10 rounded-control border border-border bg-surface px-2 text-sm"
                      value={ajuste.tipo}
                      onChange={(e) =>
                        cambiarAjuste(i, { tipo: e.target.value as TipoAjuste, objetivo: null })
                      }
                    >
                      {TIPOS.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="flex flex-col gap-1 text-xs">
                    <span className="type-label text-text">Aplica a</span>
                    <select
                      className="h-10 rounded-control border border-border bg-surface px-2 text-sm"
                      value={ajuste.objetivo ?? ""}
                      onChange={(e) => cambiarAjuste(i, { objetivo: e.target.value || null })}
                      required={exigeObjetivo(ajuste.tipo)}
                    >
                      {!exigeObjetivo(ajuste.tipo) ? (
                        <option value="">Todos</option>
                      ) : (
                        <option value="">Elija…</option>
                      )}
                      {objetivos(ajuste.tipo).map((o) => (
                        <option key={o} value={o}>
                          {o}
                        </option>
                      ))}
                    </select>
                  </label>
                  {ajuste.tipo !== "CERRAR_RUTA" ? (
                    <Campo
                      etiqueta="Cambio %"
                      value={String(ajuste.porcentaje)}
                      onChange={(e) =>
                        cambiarAjuste(i, {
                          porcentaje: Number(e.target.value.replace(",", ".")) || 0,
                        })
                      }
                      inputMode="decimal"
                    />
                  ) : (
                    <span />
                  )}
                  <Boton
                    variante="fantasma"
                    aria-label="Quitar ajuste"
                    onClick={() => setAjustes((l) => l.filter((_, j) => j !== i))}
                    disabled={ajustes.length === 1}
                  >
                    <Trash2 className="size-4" aria-hidden="true" />
                  </Boton>
                </div>
              ))}
              <div className="flex flex-wrap gap-2">
                <Boton
                  variante="secundario"
                  icono={<Plus className="size-4" aria-hidden="true" />}
                  onClick={() =>
                    setAjustes((l) => [...l, { tipo: "OFERTA", porcentaje: 10, objetivo: null }])
                  }
                >
                  Agregar ajuste
                </Boton>
                <Boton
                  type="submit"
                  disabled={crear.isPending}
                  icono={<FlaskConical className="size-4" aria-hidden="true" />}
                >
                  Guardar escenario
                </Boton>
              </div>
              {crear.isError ? <ErrorApi error={crear.error} /> : null}
            </form>
          </Tarjeta>

          <Tarjeta>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="type-title-18 text-text">Escenarios</h2>
              <label className="flex items-center gap-2 text-xs text-muted">
                <input
                  type="checkbox"
                  checked={incluirAg}
                  onChange={(e) => setIncluirAg(e.target.checked)}
                />
                Ejecutar también el AG
              </label>
            </div>
            <div className="mt-3 space-y-2">
              {escenarios.isLoading ? <Cargando /> : null}
              {escenarios.isError ? <ErrorApi error={escenarios.error} /> : null}
              {escenarios.data?.length === 0 ? <Vacio>Aún no hay escenarios.</Vacio> : null}
              {(escenarios.data ?? []).map((esc) => (
                <article
                  key={esc.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-control border border-border p-3"
                >
                  <div className="min-w-0">
                    <p className="type-cuerpo-strong text-text">{esc.nombre}</p>
                    <p className="text-xs text-muted">
                      {esc.ajustes
                        .map(
                          (a) =>
                            `${etiquetaTipo(a.tipo)}${a.objetivo ? ` ${a.objetivo}` : ""} ${a.tipo === "CERRAR_RUTA" ? "" : `${a.porcentaje > 0 ? "+" : ""}${a.porcentaje} %`}`,
                        )
                        .join(" · ")}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Boton
                      icono={<Play className="size-4" aria-hidden="true" />}
                      disabled={ejecutar.isPending}
                      onClick={() => ejecutar.mutate({ id: esc.id, incluirAg })}
                    >
                      Ejecutar
                    </Boton>
                    <Boton
                      variante="fantasma"
                      aria-label={`Eliminar ${esc.nombre}`}
                      onClick={() => eliminar.mutate(esc.id)}
                    >
                      <Trash2 className="size-4" aria-hidden="true" />
                    </Boton>
                  </div>
                </article>
              ))}
            </div>
            {ejecutar.isPending ? (
              <div className="mt-3">
                <Cargando texto="Resolviendo el escenario con ambos métodos…" />
              </div>
            ) : null}
            {ejecutar.isError ? (
              <div className="mt-3">
                <ErrorApi error={ejecutar.error} />
              </div>
            ) : null}
          </Tarjeta>
        </div>

        {resultado ? (
          <Tarjeta className="mt-4">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="type-title-18 text-text">Resultado: {resultado.nombre}</h2>
              {resultado.usa_planta_ficticia ? (
                <Etiqueta variante="peligro">
                  {formatNumber(resultado.toneladas_ficticia)} t sin procesar (planta ficticia)
                </Etiqueta>
              ) : null}
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <KpiCard etiqueta="Costo base" valor={formatCurrency(resultado.costo_base)} />
              <KpiCard
                etiqueta="Costo del escenario (exacto)"
                valor={formatCurrency(resultado.costo_exacto)}
                detalle={`${formatNumber(resultado.variacion_porcentual)} % frente a la base`}
                tono={resultado.variacion_porcentual > 0 ? "peligro" : "primario"}
              />
              <KpiCard
                etiqueta="Costo del escenario (AG)"
                valor={resultado.costo_ag != null ? formatCurrency(resultado.costo_ag) : "—"}
                detalle={
                  resultado.gap_ag != null
                    ? `Gap ${formatNumber(resultado.gap_ag)} %`
                    : "No ejecutado"
                }
                tono="acento"
              />
              <KpiCard
                etiqueta="Tiempos"
                valor={`${formatNumber(resultado.tiempo_exacto_ms)} ms`}
                detalle={
                  resultado.tiempo_ag_ms != null
                    ? `AG ${formatNumber(resultado.tiempo_ag_ms / 1000)} s`
                    : "Exacto"
                }
              />
            </div>
            {resultado.cambios_flujo.length ? (
              <div className="mt-4 overflow-x-auto scroll-fino">
                <table className="tabla tabla--compacta min-w-[480px]">
                  <thead>
                    <tr>
                      <th>Ruta</th>
                      <th className="text-right">Base (t)</th>
                      <th className="text-right">Escenario (t)</th>
                      <th className="text-right">Cambio</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resultado.cambios_flujo.map((c) => (
                      <tr key={`${c.origen}-${c.destino}`}>
                        <td className="font-semibold">
                          {c.origen} → {c.destino}
                        </td>
                        <td className="text-right tabular-nums">
                          {formatNumber(c.toneladas_base)}
                        </td>
                        <td className="text-right tabular-nums">
                          {formatNumber(c.toneladas_escenario)}
                        </td>
                        <td
                          className={[
                            "text-right tabular-nums",
                            c.toneladas_escenario > c.toneladas_base
                              ? "text-primary"
                              : "text-danger",
                          ].join(" ")}
                        >
                          {formatNumber(c.toneladas_escenario - c.toneladas_base)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="mt-4 text-sm text-muted">
                La distribución de flujos no cambia en este escenario.
              </p>
            )}
          </Tarjeta>
        ) : null}

        <div className="mt-4 grid gap-4 xl:grid-cols-2">
          <Tornado />
          <Rangos />
        </div>
      </PageBody>
    </>
  );
}
