import { ArrowRight, Database, MapPinned, Warehouse } from "lucide-react";
import { Link } from "react-router-dom";

import { useCargarCaso, useMatriz, useNodos, useUltimaEjecucion, useValidacion } from "@/api/hooks";
import { MapaReal } from "@/components/mapa/MapaReal";
import { Barra } from "@/components/ui/Barra";
import { Boton } from "@/components/ui/Boton";
import { Cargando, ErrorApi } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { FilaValidacion } from "@/components/ui/FilaValidacion";
import { PageBody } from "@/components/ui/PageHero";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber } from "@/lib/format";
import { activos, usoDePlantas, valorSensibilidad, ejecucionVigente } from "@/lib/red";

const accesos = [
  { to: "/red", titulo: "Red", texto: "Empresas, plantas y mapa real" },
  { to: "/rutas", titulo: "Rutas", texto: "Distancias OSRM y matriz de costos" },
  { to: "/exacto", titulo: "Exacto", texto: "Óptimo global con PuLP + CBC" },
  { to: "/ag", titulo: "Genético", texto: "Parámetros y convergencia" },
  { to: "/sensibilidad", titulo: "Sensibilidad", texto: "Escenarios, duales y rangos" },
  { to: "/comparativo", titulo: "Comparativo", texto: "Exacto vs. AG y escalabilidad" },
];

export function PanelPage() {
  const nodos = useNodos();
  const matriz = useMatriz();
  const validacion = useValidacion();
  const exacto = useUltimaEjecucion("EXACTO");
  const cargarCaso = useCargarCaso();

  const nodosActivos = activos(nodos.data);
  const empresas = nodosActivos.filter((n) => n.tipo === "FUENTE");
  const plantas = nodosActivos.filter((n) => n.tipo === "PLANTA");
  const detalle = exacto.detalle.data;
  const flujos = detalle?.flujos ?? [];
  const uso = usoDePlantas(nodosActivos, flujos);
  const esCasoReal = empresas.some((e) => e.codigo.startsWith("R"));
  const saturadas = plantas.filter(
    (p) => uso[p.codigo] && uso[p.codigo].uso >= p.capacidad_t! - 1e-6,
  );
  const toneladas = flujos.reduce((suma, f) => suma + f.toneladas, 0);

  return (
    <>
      <section className="bg-primary-dark text-white">
        <div className="mx-auto w-full max-w-[1440px] px-4 sm:px-8">
          <h1 className="sr-only">Panel de control</h1>
          <div className="grid gap-8 py-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] lg:items-center lg:py-10">
            <div>
              <p className="type-eyebrow text-primary-light">
                {esCasoReal
                  ? "Caso real del Meta · EVA 2018 · ICA 2025 · OSRM"
                  : "Caso base del Meta · Semana tipo"}
              </p>
              <p className="mt-6 text-sm leading-5 text-white/80">Costo óptimo semanal</p>
              <p className="mt-1 text-[44px] font-bold leading-[48px] tracking-[-0.03em] tabular-nums sm:text-[56px] sm:leading-[60px]">
                {detalle?.costo_total != null ? formatCurrency(detalle.costo_total) : "—"}
              </p>
              <p className="mt-1 text-sm leading-5 text-[#b9d6c6]">
                {detalle?.costo_total && toneladas
                  ? `COP por semana · ${formatCurrency(detalle.costo_total / toneladas)} por tonelada`
                  : "Ejecute el modelo exacto para ver el óptimo"}
              </p>

              <dl className="mt-6 flex flex-wrap gap-x-8 gap-y-4">
                <div>
                  <dt className="type-cifra-28 text-white">
                    {validacion.data ? `${formatNumber(validacion.data.oferta_total)} t` : "—"}
                  </dt>
                  <dd className="mt-1 text-xs text-[#b9d6c6]">
                    Oferta · {empresas.length} empresas
                  </dd>
                </div>
                <div>
                  <dt className="type-cifra-28 text-white">
                    {validacion.data ? `${formatNumber(validacion.data.capacidad_total)} t` : "—"}
                  </dt>
                  <dd className="mt-1 text-xs text-[#b9d6c6]">
                    Capacidad · {plantas.length} plantas
                  </dd>
                </div>
                <div>
                  <dt className="type-cifra-28 text-accent-soft">
                    {detalle ? `${saturadas.length} de ${plantas.length}` : "—"}
                  </dt>
                  <dd className="mt-1 text-xs text-[#b9d6c6]">Plantas saturadas</dd>
                </div>
              </dl>

              <div className="mt-6 flex flex-wrap gap-2">
                <Boton
                  variante="acento"
                  icono={<Database className="size-4" aria-hidden="true" />}
                  disabled={cargarCaso.isPending}
                  onClick={() => cargarCaso.mutate("caso-base")}
                >
                  Cargar caso base
                </Boton>
                <Boton
                  variante="acento"
                  icono={<MapPinned className="size-4" aria-hidden="true" />}
                  disabled={cargarCaso.isPending}
                  onClick={() => cargarCaso.mutate("caso-real")}
                >
                  Cargar caso real del Meta
                </Boton>
                <Boton
                  variante="acento"
                  icono={<Warehouse className="size-4" aria-hidden="true" />}
                  disabled={cargarCaso.isPending}
                  onClick={() => cargarCaso.mutate("acopios")}
                  title="Agrega los centros de acopio de Puerto López y San Martín a la red activa"
                >
                  Agregar centros de acopio
                </Boton>
              </div>
              {cargarCaso.isError ? (
                <div className="mt-3">
                  <ErrorApi error={cargarCaso.error} />
                </div>
              ) : null}
            </div>

            <div className="overflow-hidden rounded-card border border-primary bg-white">
              {nodos.isLoading ? (
                <div className="p-5">
                  <Cargando texto="Cargando la red…" />
                </div>
              ) : (
                <MapaReal
                  nodos={nodosActivos}
                  rutas={matriz.data?.rutas}
                  flujos={flujos}
                  usoPlantas={uso}
                  alto="h-[360px] lg:h-[460px]"
                  etiqueta="Mapa real de la red con los flujos óptimos"
                />
              )}
            </div>
          </div>
        </div>
      </section>

      <PageBody>
        {nodos.isError ? <ErrorApi error={nodos.error} /> : null}

        <div className="grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
          <Tarjeta>
            <div className="flex items-center justify-between gap-2">
              <h2 className="type-title-18 text-text">Uso de las plantas</h2>
              {detalle ? (
                ejecucionVigente(flujos, nodosActivos) ? (
                  <Etiqueta variante={detalle.estado === "Óptimo" ? "exito" : "alerta"}>
                    {detalle.estado}
                  </Etiqueta>
                ) : (
                  <Etiqueta variante="alerta">Red cambiada: ejecute el exacto</Etiqueta>
                )
              ) : null}
            </div>
            <div className="mt-4 space-y-4">
              {plantas.map((planta) => {
                const datos = uso[planta.codigo];
                const capacidad = planta.capacidad_t ?? 1;
                const fraccion = datos ? datos.uso / capacidad : 0;
                const dual = detalle
                  ? valorSensibilidad(detalle.sensibilidad, "DUAL_CAPACIDAD", planta.codigo)
                  : undefined;
                return (
                  <div key={planta.codigo}>
                    <div className="flex items-center justify-between gap-2 text-[13px]">
                      <span className="font-semibold text-text">
                        {planta.codigo} · {planta.nombre}
                      </span>
                      <span className="tabular-nums text-muted">
                        {formatNumber(datos?.uso ?? 0)} / {formatNumber(capacidad)} t
                      </span>
                    </div>
                    <Barra
                      valor={fraccion}
                      tono={fraccion >= 0.999 ? "peligro" : "primario"}
                      className="mt-2"
                      etiqueta={`Uso de ${planta.nombre}`}
                    />
                    {dual && dual.valor < 0 ? (
                      <p className="mt-1 text-xs text-danger">
                        Precio sombra {formatCurrency(dual.valor)}/t: una tonelada más de capacidad
                        ahorra {formatCurrency(-dual.valor)} por semana
                      </p>
                    ) : null}
                  </div>
                );
              })}
              {!plantas.length && !nodos.isLoading ? (
                <p className="text-sm text-muted">No hay plantas activas. Cargue un caso.</p>
              ) : null}
            </div>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-18 text-text">Validación de la red</h2>
            <div className="mt-4 space-y-4">
              {validacion.isLoading ? <Cargando /> : null}
              {validacion.data ? (
                <>
                  <FilaValidacion
                    estado={validacion.data.es_valida ? "correcto" : "alerta"}
                    titulo={
                      validacion.data.es_valida ? "Red consistente" : "Red con nodos aislados"
                    }
                    nota={
                      validacion.data.nodos_aislados.length
                        ? `Sin rutas: ${validacion.data.nodos_aislados.join(", ")}`
                        : "Todas las empresas tienen al menos una ruta habilitada"
                    }
                  />
                  <FilaValidacion
                    estado={validacion.data.necesita_planta_ficticia ? "alerta" : "correcto"}
                    titulo={
                      validacion.data.necesita_planta_ficticia
                        ? "La oferta supera la capacidad"
                        : "La capacidad cubre la oferta"
                    }
                    nota={validacion.data.mensajes[0] ?? ""}
                  />
                </>
              ) : null}
            </div>
          </Tarjeta>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {accesos.map((acceso) => (
            <Link
              key={acceso.to}
              to={acceso.to}
              className="group flex items-center justify-between gap-3 rounded-card border border-border bg-surface p-4 transition-colors hover:border-primary"
            >
              <span>
                <span className="type-title-15 block text-text">{acceso.titulo}</span>
                <span className="text-xs text-muted">{acceso.texto}</span>
              </span>
              <ArrowRight
                className="size-4 text-primary transition-transform group-hover:translate-x-0.5"
                aria-hidden="true"
              />
            </Link>
          ))}
        </div>
      </PageBody>
    </>
  );
}
