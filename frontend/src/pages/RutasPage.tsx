import { Save, Wand2 } from "lucide-react";
import { useMemo, useState } from "react";

import { apiClient } from "@/api/client";
import {
  useActualizarParametro,
  useActualizarRutas,
  useMatriz,
  useNodos,
  useParametros,
} from "@/api/hooks";
import type { Parametro, Ruta, RutaCambio } from "@/api/tipos";
import { Boton } from "@/components/ui/Boton";
import { Cargando, ErrorApi } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber } from "@/lib/format";
import { activos } from "@/lib/red";

type Vista = "costo" | "distancia";
const clave = (r: { origen: string; destino: string }) => `${r.origen}->${r.destino}`;

function FilaParametro({ parametro }: { parametro: Parametro }) {
  const actualizar = useActualizarParametro();
  const [valor, setValor] = useState(String(parametro.valor));
  const guardar = () => {
    const nuevo = Number(valor.replace(",", "."));
    if (Number.isFinite(nuevo) && nuevo !== parametro.valor) {
      actualizar.mutate({ clave: parametro.clave, valor: nuevo });
    }
  };
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={`param-${parametro.clave}`} className="type-label text-text">
        {parametro.descripcion ?? parametro.clave}
      </label>
      <div className="flex items-center gap-2">
        <input
          id={`param-${parametro.clave}`}
          className="h-10 w-full rounded-control border border-border bg-surface px-3 text-sm tabular-nums focus:border-primary"
          value={valor}
          onChange={(e) => setValor(e.target.value)}
          onBlur={guardar}
          onKeyDown={(e) => e.key === "Enter" && guardar()}
          inputMode="decimal"
        />
        <span className="shrink-0 text-xs text-muted">{parametro.unidad}</span>
      </div>
      {actualizar.isError ? <ErrorApi error={actualizar.error} /> : null}
    </div>
  );
}

export function RutasPage() {
  const matriz = useMatriz();
  const nodos = useNodos();
  const parametros = useParametros();
  const guardarRutas = useActualizarRutas();
  const [vista, setVista] = useState<Vista>("costo");
  const [cambios, setCambios] = useState<Record<string, RutaCambio>>({});
  const [generando, setGenerando] = useState(false);

  const porClave = useMemo(
    () => new Map((matriz.data?.rutas ?? []).map((r) => [clave(r), r])),
    [matriz.data],
  );
  const nombres = useMemo(
    () => new Map(activos(nodos.data).map((n) => [n.codigo, n.nombre])),
    [nodos.data],
  );
  const origenes = matriz.data?.origenes ?? [];
  const destinos = matriz.data?.destinos ?? [];
  const pendientes = Object.values(cambios);
  const fuentes = new Set((matriz.data?.rutas ?? []).map((r) => r.fuente_distancia ?? "—"));

  const editar = (ruta: Ruta, parcial: Partial<RutaCambio>) =>
    setCambios((c) => ({
      ...c,
      [clave(ruta)]: {
        ...(c[clave(ruta)] ?? { origen: ruta.origen, destino: ruta.destino }),
        ...parcial,
      },
    }));

  const generarFaltantes = async () => {
    setGenerando(true);
    try {
      await apiClient.post("/rutas/generar-faltantes");
      await matriz.refetch();
    } finally {
      setGenerando(false);
    }
  };

  return (
    <>
      <PageHero
        eyebrow="Red logística · HU-03 · HU-04"
        title="Rutas y costos"
        description="c_ij = k · d_ij + o_j. Edite distancias, el costo por t·km de una ruta o ciérrela; los cambios se guardan por lote"
        kpis={[
          { valor: String(matriz.data?.rutas.length ?? "—"), etiqueta: "Rutas" },
          {
            valor: String(matriz.data?.rutas.filter((r) => !r.habilitada).length ?? "—"),
            etiqueta: "Cerradas",
          },
          { valor: [...fuentes].join(" · ") || "—", etiqueta: "Origen de la distancia" },
        ]}
      />

      <PageBody>
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
          <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 px-5 pt-5">
              <Segmentado
                items={[
                  { label: "Costo unitario (COP/t)", value: "costo" },
                  { label: "Distancia y edición", value: "distancia" },
                ]}
                value={vista}
                onChange={(v) => setVista(v as Vista)}
                ariaLabel="Vista de la matriz"
              />
              <div className="flex flex-wrap gap-2">
                <Boton
                  variante="secundario"
                  icono={<Wand2 className="size-4" aria-hidden="true" />}
                  onClick={generarFaltantes}
                  disabled={generando}
                >
                  Generar rutas faltantes
                </Boton>
                <Boton
                  icono={<Save className="size-4" aria-hidden="true" />}
                  disabled={!pendientes.length || guardarRutas.isPending}
                  onClick={() =>
                    guardarRutas.mutate(pendientes, { onSuccess: () => setCambios({}) })
                  }
                >
                  Guardar {pendientes.length ? `(${pendientes.length})` : ""}
                </Boton>
              </div>
            </div>
            {guardarRutas.isError ? (
              <div className="px-5 pt-3">
                <ErrorApi error={guardarRutas.error} />
              </div>
            ) : null}

            <div className="mt-4 overflow-x-auto scroll-fino">
              {matriz.isLoading ? (
                <div className="px-5 pb-5">
                  <Cargando />
                </div>
              ) : matriz.isError ? (
                <div className="px-5 pb-5">
                  <ErrorApi error={matriz.error} />
                </div>
              ) : (
                <table
                  className="tabla tabla--compacta"
                  style={{ minWidth: 200 + destinos.length * 150 }}
                >
                  <thead>
                    <tr>
                      <th className="sticky left-0 z-10 w-[200px]">Empresa</th>
                      {destinos.map((d) => (
                        <th key={d} className="text-right">
                          {d}
                          <span className="block text-[11px] font-normal opacity-80">
                            {nombres.get(d)}
                          </span>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {origenes.map((o) => (
                      <tr key={o}>
                        <td className="sticky left-0 z-10 bg-surface">
                          <span className="font-semibold">{o}</span>{" "}
                          <span className="text-xs text-muted">{nombres.get(o)}</span>
                        </td>
                        {destinos.map((d) => {
                          const ruta = porClave.get(`${o}->${d}`);
                          if (!ruta)
                            return (
                              <td key={d} className="text-center text-muted">
                                —
                              </td>
                            );
                          const cambio = cambios[clave(ruta)];
                          const habilitada = cambio?.habilitada ?? ruta.habilitada;
                          if (vista === "costo") {
                            return (
                              <td
                                key={d}
                                className={[
                                  "text-right tabular-nums",
                                  habilitada ? "" : "text-muted line-through",
                                ].join(" ")}
                              >
                                {ruta.costo_unitario != null
                                  ? formatCurrency(ruta.costo_unitario)
                                  : "—"}
                                <span className="block text-[11px] text-muted">
                                  {formatNumber(ruta.distancia_km ?? 0)} km
                                  {ruta.duracion_min
                                    ? ` · ${formatNumber(ruta.duracion_min)} min`
                                    : ""}
                                </span>
                              </td>
                            );
                          }
                          return (
                            <td key={d} className={cambio ? "bg-accent-soft" : ""}>
                              <div className="flex flex-col items-end gap-1">
                                <input
                                  aria-label={`Distancia ${o} a ${d} (km)`}
                                  className="h-7 w-20 rounded-control border border-border bg-surface px-1 text-right text-xs tabular-nums"
                                  defaultValue={ruta.distancia_km ?? ""}
                                  onChange={(e) =>
                                    editar(ruta, {
                                      distancia_km: Number(e.target.value.replace(",", ".")),
                                    })
                                  }
                                />
                                <input
                                  aria-label={`Costo por t·km ${o} a ${d}`}
                                  placeholder="k global"
                                  className="h-7 w-20 rounded-control border border-border bg-surface px-1 text-right text-xs tabular-nums"
                                  defaultValue={ruta.costo_km_t ?? ""}
                                  onChange={(e) =>
                                    e.target.value === ""
                                      ? editar(ruta, { quitar_costo_km_t: true })
                                      : editar(ruta, {
                                          costo_km_t: Number(e.target.value.replace(",", ".")),
                                        })
                                  }
                                />
                                <label className="flex items-center gap-1 text-[11px] text-muted">
                                  <input
                                    type="checkbox"
                                    checked={habilitada}
                                    onChange={(e) => editar(ruta, { habilitada: e.target.checked })}
                                  />
                                  Abierta
                                </label>
                              </div>
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-18 text-text">Parámetros del negocio</h2>
            <p className="mt-1 text-xs text-muted">Se aplican en la próxima ejecución.</p>
            <div className="mt-4 space-y-4">
              {parametros.isLoading ? <Cargando /> : null}
              {parametros.isError ? <ErrorApi error={parametros.error} /> : null}
              {(parametros.data ?? []).map((p) => (
                <FilaParametro key={`${p.clave}-${p.valor}`} parametro={p} />
              ))}
            </div>
            <div className="mt-5 space-y-2 text-xs text-muted">
              <p>
                <Etiqueta variante="neutral">OSRM</Etiqueta> distancia vial real sobre OpenStreetMap
              </p>
              <p>
                <Etiqueta variante="neutral">ESTIMADA</Etiqueta> Haversine × 1,3 o dato del caso
                base
              </p>
              <p>
                <Etiqueta variante="neutral">MANUAL</Etiqueta> editada por el usuario
              </p>
            </div>
          </Tarjeta>
        </div>
      </PageBody>
    </>
  );
}
