import { useState } from "react";

import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { ConvergenciaChart } from "@/components/ui/ConvergenciaChart";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { Barra } from "@/components/ui/Barra";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { costoOptimo } from "@/data/red";
import { formatNumber } from "@/lib/format";

const seleccionItems = [
  { label: "Torneo (k = 3)", value: "torneo" },
  { label: "Ruleta", value: "ruleta" },
];

const cruceItems = [
  { label: "Un punto", value: "un-punto" },
  { label: "Dos puntos", value: "dos-puntos" },
];

export function GeneticoPage() {
  const [seleccion, setSeleccion] = useState("torneo");
  const [cruce, setCruce] = useState("un-punto");

  return (
    <>
      <PageHero
        eyebrow="Algoritmo genético · HU-09 · HU-10"
        title="Algoritmo genético"
        description="Ajusta los parámetros, ejecuta y compara la convergencia con el óptimo del modelo exacto"
        kpis={[
          { valor: `$${formatNumber(costoOptimo)}`, etiqueta: "Óptimo de referencia" },
          { valor: "Selección por torneo", etiqueta: "k = 3" },
          { valor: "2", etiqueta: "Individuos de elite" },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <Etiqueta variante="alerta">
            Cifras ilustrativas hasta implementar HU-09 y HU-10
          </Etiqueta>
          <div className="flex flex-wrap gap-2">
            <Boton variante="secundario">Restablecer valores</Boton>
            <Boton>Ejecutar algoritmo genético</Boton>
          </div>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
          <Tarjeta>
            <h2 className="type-title-22 text-text">Parámetros</h2>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <Campo etiqueta="Población" defaultValue={100} ayuda="Individuos" />
              <Campo etiqueta="Generaciones" defaultValue={300} ayuda="Máximo" />
              <Campo etiqueta="Tasa de cruce" defaultValue="0,85" ayuda="Entre 0 y 1" />
              <Campo etiqueta="Tasa de mutación" defaultValue="0,10" ayuda="Entre 0 y 1" />
              <Campo
                etiqueta="Penalización λ"
                defaultValue="1.000.000"
                ayuda="Violar restricciones"
              />
              <Campo etiqueta="Elitismo" defaultValue={2} ayuda="Pasan intactos" />
            </div>

            <div className="mt-4 space-y-4">
              <div>
                <p className="type-label mb-1 text-text">Selección</p>
                <Segmentado
                  items={seleccionItems}
                  value={seleccion}
                  onChange={setSeleccion}
                  ariaLabel="Método de selección"
                  className="w-full"
                />
              </div>

              <div>
                <p className="type-label mb-1 text-text">Cruce</p>
                <Segmentado
                  items={cruceItems}
                  value={cruce}
                  onChange={setCruce}
                  ariaLabel="Tipo de cruce"
                  className="w-full"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Campo etiqueta="Semilla" defaultValue={42} ayuda="Reproducible" />
                <Campo etiqueta="Parada" defaultValue={50} ayuda="Generaciones sin mejora" />
              </div>
            </div>

            <div className="mt-4 rounded-card bg-primary-soft p-4">
              <p className="type-title-15 text-primary-dark">Población inicial</p>
              <p className="mt-1 text-xs leading-4 text-primary-dark/80">
                10 % construida con la heurística de costo mínimo y 90 % aleatoria. Cada individuo
                se repara reescalando sus filas para cumplir la oferta.
              </p>
            </div>
          </Tarjeta>

          <div className="min-w-0">
            <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
              <KpiCard etiqueta="Mejor costo" valor="$65.012.000" detalle="COP por semana" />
              <KpiCard etiqueta="Gap frente al óptimo" valor="0,50 %" detalle="(Z_AG − Z*) / Z*" />
              <KpiCard etiqueta="Generaciones" valor="187" detalle="Parada: 50 sin mejora" />
              <KpiCard etiqueta="Violaciones" valor="0" detalle="Tras la reparación" />
            </div>

            <Tarjeta className="mt-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="type-title-15 text-text">Convergencia por generación</h2>
                <ul className="flex flex-wrap items-center gap-4 text-xs leading-4 text-text">
                  <li className="inline-flex items-center gap-2">
                    <span aria-hidden="true" className="h-0.5 w-4 rounded bg-primary" />
                    Mejor costo
                  </li>
                  <li className="inline-flex items-center gap-2">
                    <span aria-hidden="true" className="h-0.5 w-4 rounded bg-accent" />
                    Costo promedio
                  </li>
                  <li className="inline-flex items-center gap-2">
                    <span
                      aria-hidden="true"
                      className="h-0 w-4 border-t-2 border-dashed border-text"
                    />
                    Óptimo exacto
                  </li>
                </ul>
              </div>
              <div className="mt-3 overflow-x-auto scroll-fino">
                <ConvergenciaChart className="h-auto min-w-[680px]" />
              </div>
            </Tarjeta>

            <Tarjeta className="mt-4">
              <h2 className="type-title-15 text-text">Calidad frente al óptimo</h2>
              <div className="mt-4 space-y-4">
                <div className="flex items-center gap-3">
                  <span className="w-[150px] shrink-0 text-[13px] leading-5 text-text">
                    Modelo exacto
                  </span>
                  <Barra valor={1} className="flex-1" etiqueta="Costo del modelo exacto" />
                  <span className="shrink-0 type-cuerpo-strong tabular-nums text-text">
                    ${formatNumber(costoOptimo)}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-[150px] shrink-0 text-[13px] leading-5 text-text">
                    Algoritmo genético
                  </span>
                  <Barra
                    valor={costoOptimo / 65_012_000}
                    className="flex-1"
                    etiqueta="Costo del algoritmo genético"
                  />
                  <span className="shrink-0 type-cuerpo-strong tabular-nums text-text">
                    $65.012.000
                  </span>
                </div>
              </div>
            </Tarjeta>
          </div>
        </div>
      </PageBody>
    </>
  );
}
