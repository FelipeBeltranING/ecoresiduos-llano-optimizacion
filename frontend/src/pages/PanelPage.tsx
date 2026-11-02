import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import { Etiqueta } from "@/components/ui/Etiqueta";
import { FilaValidacion } from "@/components/ui/FilaValidacion";
import { Barra } from "@/components/ui/Barra";
import { PageBody } from "@/components/ui/PageHero";
import { RedMapa } from "@/components/ui/RedMapa";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { costoOptimo, plantas, totalCapacidad, totalOferta } from "@/data/red";
import { formatNumber } from "@/lib/format";

const kpis = [
  { valor: `${totalOferta} t`, etiqueta: "Oferta semanal" },
  { valor: `${totalCapacidad} t`, etiqueta: "Capacidad" },
  { valor: "2 de 4", etiqueta: "Plantas saturadas" },
];

const kpisMovil = [
  { valor: `${totalOferta} t`, etiqueta: "Oferta", detalle: "10 empresas" },
  { valor: `${totalCapacidad} t`, etiqueta: "Capacidad", detalle: "Holgura de 60 t" },
  { valor: "2 de 4", etiqueta: "Saturadas", detalle: "Villavicencio, Restrepo", tono: "text-danger" },
  { valor: "11", etiqueta: "Rutas", detalle: "En el óptimo" },
];

function estadoPlanta(saturada: boolean, porcentaje: number) {
  if (saturada || porcentaje >= 100) {
    return { texto: "Saturada", variante: "peligro" as const, tono: "text-danger" };
  }
  if (porcentaje >= 95) {
    return { texto: "Casi llena", variante: "alerta" as const, tono: "text-text" };
  }
  return { texto: "Con holgura", variante: "exito" as const, tono: "text-primary" };
}

export function PanelPage() {
  return (
    <>
      <section className="bg-primary-dark text-white">
        <div className="mx-auto w-full max-w-[1440px] px-4 sm:px-8">
          <h1 className="sr-only">Panel de control</h1>
          <div className="grid gap-8 py-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:items-center lg:py-10">
            <div>
              <p className="type-eyebrow text-primary-light">Caso base del meta · Semana tipo</p>

              <p className="mt-6 text-sm leading-5 text-white/80">Costo óptimo semanal</p>
              <p className="mt-1 text-[44px] font-bold leading-[48px] tracking-[-0.03em] tabular-nums sm:text-[56px] sm:leading-[60px] lg:text-[72px] lg:leading-[76px]">
                ${formatNumber(costoOptimo)}
              </p>
              <p className="mt-1 text-sm leading-5 text-[#b9d6c6]">
                COP por semana · $72.687 por tonelada
              </p>

              <dl className="mt-6 hidden flex-wrap gap-x-8 gap-y-4 lg:flex">
                {kpis.map((kpi) => (
                  <div key={kpi.etiqueta}>
                    <dt className="type-cifra-28 text-white">{kpi.valor}</dt>
                    <dd className="mt-1 text-xs leading-4 text-[#b9d6c6]">{kpi.etiqueta}</dd>
                  </div>
                ))}
              </dl>

              <div className="mt-6 hidden max-w-md rounded-card bg-primary p-5 lg:block">
                <p className="type-title-15 text-white">Cuello de botella</p>
                <p className="mt-1 text-sm leading-5 text-white/90">
                  Una tonelada más de capacidad ahorraría $17.750 por semana en Villavicencio y
                  $14.250 en Restrepo.
                </p>
              </div>
            </div>

            <div className="hidden overflow-hidden rounded-card border border-primary lg:block">
              <RedMapa
                tono="oscuro"
                mostrarLeyenda
                mostrarEscala
                className="h-[470px]"
                etiqueta="Mapa esquemático del caso base: empresas, plantas y flujos óptimos"
              />
            </div>
          </div>
        </div>
      </section>

      <PageBody>
        <div className="grid grid-cols-2 gap-3 lg:hidden">
          {kpisMovil.map((kpi) => (
            <article key={kpi.etiqueta} className="rounded-card border border-border bg-surface p-4">
              <p className="type-label text-muted">{kpi.etiqueta}</p>
              <p className={["mt-1 type-cifra-28", kpi.tono ?? "text-text"].join(" ")}>{kpi.valor}</p>
              <p className="mt-0.5 text-xs leading-4 text-muted">{kpi.detalle}</p>
            </article>
          ))}
        </div>

        <Tarjeta className="mt-4 lg:hidden">
          <h2 className="type-title-15 text-text">Flujos óptimos</h2>
          <div className="mt-3 overflow-hidden rounded-card bg-primary-dark">
            <RedMapa tono="oscuro" etiqueta="Flujos óptimos por semana" />
          </div>
          <p className="mt-2 text-xs leading-4 text-muted">
            Línea = toneladas por semana. Empresas en ámbar.
          </p>
        </Tarjeta>

        <section className="mt-6 lg:mt-0">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <h2 className="type-title-22 text-text">Uso de plantas</h2>
            <p className="hidden text-xs leading-4 text-muted sm:block">
              Precio sombra: ahorro semanal por cada tonelada adicional de capacidad
            </p>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4 xl:gap-4">
            {plantas.map((planta) => {
              const porcentaje = Math.round((planta.uso / planta.capacidad) * 100);
              const estado = estadoPlanta(planta.saturada, porcentaje);
              const libre = planta.capacidad - planta.uso;
              return (
                <article
                  key={planta.codigo}
                  className="flex flex-col rounded-card border border-border bg-surface p-5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="type-title-15 text-text">{planta.nombre}</h3>
                    <span className="hidden sm:block">
                      <Etiqueta variante={estado.variante}>{estado.texto}</Etiqueta>
                    </span>
                    <p className={["text-sm font-semibold sm:hidden", estado.tono].join(" ")}>
                      {planta.uso} / {planta.capacidad} t
                    </p>
                  </div>

                  <p
                    className={[
                      "mt-3 hidden type-cifra-44 sm:block",
                      estado.tono,
                    ].join(" ")}
                  >
                    {porcentaje} %
                  </p>

                  <Barra
                    valor={planta.uso / planta.capacidad}
                    tono={planta.saturada ? "peligro" : "primario"}
                    className="mt-3"
                    etiqueta={`Uso de ${planta.nombre}`}
                  />

                  <div className="mt-3 hidden items-center justify-between gap-2 text-xs leading-4 text-muted sm:flex">
                    <span>
                      {planta.uso} de {planta.capacidad} t · libre {libre} t
                    </span>
                  </div>

                  <div className="mt-4 hidden items-center justify-between gap-2 border-t border-border pt-3 text-xs leading-4 sm:flex">
                    <span className="text-muted">Precio sombra</span>
                    <span
                      className={[
                        "type-cuerpo-strong tabular-nums",
                        planta.precioSombra < 0 ? "text-danger" : "text-text",
                      ].join(" ")}
                    >
                      {planta.precioSombra < 0
                        ? `−$${formatNumber(-planta.precioSombra)} / t`
                        : "$0 / t"}
                    </span>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Tarjeta>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="type-title-15 text-text">Validación de la red</h2>
              <Etiqueta variante="exito">Lista para resolver</Etiqueta>
            </div>
            <div className="mt-4 space-y-4">
              <FilaValidacion
                titulo="Oferta ≤ capacidad"
                nota="890 t frente a 950 t; no hace falta planta ficticia"
              />
              <FilaValidacion
                titulo="Restricciones cumplidas"
                nota="Oferta exacta y capacidad respetada en las 4 plantas"
              />
              <FilaValidacion
                estado="alerta"
                titulo="2 plantas al 100 %"
                nota="Villavicencio y Restrepo no admiten más flujo"
              />
            </div>
          </Tarjeta>

          <Tarjeta>
            <div className="flex items-center justify-between gap-2">
              <h2 className="type-title-15 text-text">Historial reciente</h2>
              <Link
                to="/historial"
                className="inline-flex items-center gap-1 text-sm font-semibold text-primary hover:text-primary-dark"
              >
                Ver todo
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </div>

            <div className="mt-4 flex items-start justify-between gap-3 border-b border-border pb-4">
              <div className="min-w-0">
                <p className="type-cuerpo-strong text-text">Exacto (PuLP + CBC)</p>
                <p className="mt-0.5 text-xs leading-4 text-muted">Caso base · 26 oct 2026</p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <span className="type-cuerpo-strong tabular-nums text-text">
                  ${formatNumber(costoOptimo)}
                </span>
                <Etiqueta variante="exito">Óptimo</Etiqueta>
              </div>
            </div>

            <div className="mt-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
              <div className="min-w-0">
                <p className="type-cuerpo-strong text-text">
                  Aún no hay corridas del algoritmo genético
                </p>
                <p className="mt-0.5 text-xs leading-4 text-muted">
                  Ejecútelo para comparar su costo y su gap frente al óptimo.
                </p>
              </div>
              <Link
                to="/ag"
                className="inline-flex shrink-0 items-center justify-center rounded-control border border-border bg-surface px-4 py-2 text-sm font-semibold leading-5 text-text transition-colors hover:bg-primary-soft"
              >
                Configurar AG
              </Link>
            </div>
          </Tarjeta>
        </div>
      </PageBody>
    </>
  );
}
