import { useState } from "react";

import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { costos, distancia, empresas, flujoDe, plantas } from "@/data/red";
import { formatNumber } from "@/lib/format";

type Modo = "costo" | "distancia" | "flujo";

const modos = [
  { label: "Costo unitario (COP/t)", value: "costo" },
  { label: "Distancia (km)", value: "distancia" },
  { label: "Flujo óptimo (t)", value: "flujo" },
];

interface Celda {
  empresa: string;
  planta: (typeof plantas)[number]["codigo"];
}

const celdaInicial: Celda = { empresa: "E05", planta: "P02" };

export function RutasPage() {
  const [modo, setModo] = useState<Modo>("costo");
  const [seleccion, setSeleccion] = useState<Celda>(celdaInicial);

  const plantaSeleccionada = plantas.find((planta) => planta.codigo === seleccion.planta);
  const costoSeleccionado = costos[seleccion.empresa][seleccion.planta];
  const distanciaSeleccionada = plantaSeleccionada
    ? distancia(costoSeleccionado, plantaSeleccionada.operacion)
    : 0;

  return (
    <>
      <PageHero
        eyebrow="Red logística · HU-03"
        title="Rutas y costos"
        description="Cada celda es una ruta de una empresa a una planta. Edita un valor y el costo se recalcula"
        kpis={[
          { valor: "40", etiqueta: "Rutas habilitadas" },
          { valor: "350", etiqueta: "COP por t·km" },
          { valor: "11", etiqueta: "Rutas en el óptimo" },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <Segmentado
            items={modos}
            value={modo}
            onChange={(value) => setModo(value as Modo)}
            ariaLabel="Métrica de la matriz de rutas"
            className="w-full sm:w-auto"
          />

          <div className="flex flex-wrap items-center gap-4">
            <span className="inline-flex items-center gap-2 text-xs leading-4 text-text">
              <span aria-hidden="true" className="size-3 rounded-sm bg-primary-soft ring-1 ring-primary" />
              Ruta usada en el óptimo
            </span>
            <span className="inline-flex items-center gap-2 text-xs leading-4 text-text">
              <span aria-hidden="true" className="size-3 rounded-sm ring-2 ring-accent" />
              Celda en edición
            </span>
            <div className="flex gap-2">
              <Boton variante="secundario">Descartar</Boton>
              <Boton>Guardar cambios</Boton>
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
            <div className="overflow-x-auto scroll-fino">
              <table className="tabla min-w-[880px]">
                <thead>
                  <tr>
                    <th className="sticky left-0 z-20 w-[240px] bg-primary-dark">Empresa</th>
                    {plantas.map((planta) => (
                      <th key={planta.codigo} className="w-[180px] text-left">
                        {planta.codigo} {planta.nombre}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {empresas.map((empresa) => (
                    <tr key={empresa.codigo}>
                      <td className="sticky left-0 z-10 bg-surface">
                        <span className="font-semibold text-primary">{empresa.codigo}</span>{" "}
                        <span className="font-medium text-text">{empresa.nombre}</span>
                      </td>
                      {plantas.map((planta) => {
                        const flujo = flujoDe(empresa.codigo, planta.codigo);
                        const costo = costos[empresa.codigo][planta.codigo];
                        const km = distancia(costo, planta.operacion);
                        const isSelected =
                          seleccion.empresa === empresa.codigo &&
                          seleccion.planta === planta.codigo;

                        return (
                          <td
                            key={planta.codigo}
                            className={[
                              "p-0",
                              flujo ? "bg-primary-soft" : "",
                              isSelected ? "ring-2 ring-inset ring-accent" : "",
                            ].join(" ")}
                          >
                            <button
                              type="button"
                              onClick={() =>
                                setSeleccion({ empresa: empresa.codigo, planta: planta.codigo })
                              }
                              aria-label={`${empresa.codigo} a ${planta.nombre}`}
                              className={[
                                "flex h-11 w-full items-center gap-2 px-3 text-left",
                                modo !== "costo" || flujo ? "justify-between" : "justify-end",
                              ].join(" ")}
                            >
                              {flujo && modo !== "flujo" ? (
                                <span className="text-xs font-medium leading-4 text-primary">
                                  {flujo.toneladas} t
                                </span>
                              ) : null}
                              {modo === "costo" ? (
                                <span
                                  className={[
                                    "text-sm tabular-nums",
                                    flujo ? "font-semibold text-primary-dark" : "text-text",
                                  ].join(" ")}
                                >
                                  {formatNumber(costo)}
                                </span>
                              ) : null}
                              {modo === "distancia" ? (
                                <span
                                  className={[
                                    "text-sm tabular-nums",
                                    flujo ? "font-semibold text-primary-dark" : "text-text",
                                  ].join(" ")}
                                >
                                  {km} km
                                </span>
                              ) : null}
                              {modo === "flujo" ? (
                                <span
                                  className={[
                                    "w-full text-right text-sm tabular-nums",
                                    flujo ? "font-semibold text-primary-dark" : "text-muted",
                                  ].join(" ")}
                                >
                                  {flujo ? `${flujo.toneladas} t` : "—"}
                                </span>
                              ) : null}
                            </button>
                          </td>
                        );
                      })}
                    </tr>
                  ))}

                  <tr className="bg-bg">
                    <td className="sticky left-0 z-10 bg-bg text-sm font-semibold text-text">
                      Costo de operación o<sub>j</sub> (COP/t)
                    </td>
                    {plantas.map((planta) => (
                      <td key={planta.codigo} className="text-right tabular-nums text-text">
                        {formatNumber(planta.operacion)}
                      </td>
                    ))}
                  </tr>
                  <tr className="bg-bg">
                    <td className="sticky left-0 z-10 bg-bg text-sm font-semibold text-text">
                      Capacidad (t/sem)
                    </td>
                    {plantas.map((planta) => (
                      <td key={planta.codigo} className="text-right tabular-nums text-text">
                        {planta.capacidad}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="border-t border-border px-4 py-3 text-xs leading-4 text-muted">
              Cada celda es c = 350 · distancia + costo de operación. Las celdas con toneladas son
              las rutas que usa el modelo exacto.
            </p>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-22 text-text">Parámetros globales</h2>

            <div className="mt-4 space-y-4">
              <Campo
                etiqueta="Costo de transporte k (COP/t·km)"
                defaultValue={350}
                estado="exito"
                ayuda="Cambiarlo recalcula las 40 rutas"
              />
              <Campo
                etiqueta="Penalización planta ficticia M (COP/t)"
                defaultValue="1.000.000"
                ayuda="Costo de no procesar una tonelada"
              />
              <Campo
                etiqueta="Tarifa de recepción (COP/t)"
                defaultValue={0}
                ayuda="Reservada para escenarios de margen"
              />
            </div>

            <div className="mt-5 rounded-card border border-accent/70 bg-accent-soft p-4">
              <p className="type-title-15 text-primary-dark">
                Celda en edición · {seleccion.empresa} → {plantaSeleccionada?.nombre}
              </p>
              <p className="mt-1 type-cuerpo-strong tabular-nums text-text">
                350 × {distanciaSeleccionada} km +{" "}
                {formatNumber(plantaSeleccionada?.operacion ?? 0)} = {formatNumber(costoSeleccionado)}{" "}
                COP/t
              </p>
              <p className="mt-1 text-xs leading-4 text-muted">
                Al editar la distancia, el costo de la celda se actualiza al instante.
              </p>
            </div>

            <Boton variante="secundario" className="mt-4">
              Recalcular todos los costos
            </Boton>
          </Tarjeta>
        </div>
      </PageBody>
    </>
  );
}
