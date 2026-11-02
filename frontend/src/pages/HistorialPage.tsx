import { Download } from "lucide-react";
import { useState } from "react";

import { Boton } from "@/components/ui/Boton";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";

type Metodo = "Exacto" | "Genético" | "Sensibilidad";

interface Ejecucion {
  fecha: string;
  metodo: Metodo;
  escenario: string;
  costo: string;
  gap: string;
  estado: "Óptimo" | "Cuasi-óptimo" | "Completado";
}

const filtros = [
  { label: "Todos", value: "todos" },
  { label: "Exacto", value: "exacto" },
  { label: "Genético", value: "genetico" },
  { label: "Sensibilidad", value: "sensibilidad" },
];

const ejecuciones: Ejecucion[] = [
  {
    fecha: "26 oct 2026 · 14:32",
    metodo: "Exacto",
    escenario: "Caso base",
    costo: "64.691.000",
    gap: "—",
    estado: "Óptimo",
  },
  {
    fecha: "26 oct 2026 · 14:35",
    metodo: "Genético",
    escenario: "Caso base",
    costo: "65.012.000",
    gap: "0,50 %",
    estado: "Cuasi-óptimo",
  },
  {
    fecha: "26 oct 2026 · 15:02",
    metodo: "Sensibilidad",
    escenario: "Combustible +20 %",
    costo: "69.385.200",
    gap: "—",
    estado: "Completado",
  },
  {
    fecha: "25 oct 2026 · 18:20",
    metodo: "Exacto",
    escenario: "Oferta −10 %",
    costo: "58.402.000",
    gap: "—",
    estado: "Óptimo",
  },
  {
    fecha: "25 oct 2026 · 18:24",
    metodo: "Genético",
    escenario: "Oferta −10 %",
    costo: "58.788.000",
    gap: "0,66 %",
    estado: "Cuasi-óptimo",
  },
  {
    fecha: "24 oct 2026 · 09:12",
    metodo: "Exacto",
    escenario: "Villavicencio −20 %",
    costo: "65.756.000",
    gap: "—",
    estado: "Óptimo",
  },
  {
    fecha: "23 oct 2026 · 16:45",
    metodo: "Genético",
    escenario: "Villavicencio −20 %",
    costo: "66.098.000",
    gap: "0,52 %",
    estado: "Cuasi-óptimo",
  },
  {
    fecha: "22 oct 2026 · 11:08",
    metodo: "Sensibilidad",
    escenario: "Oferta −10 %",
    costo: "58.402.000",
    gap: "—",
    estado: "Completado",
  },
];

function estadoEtiqueta(estado: Ejecucion["estado"]) {
  return estado === "Cuasi-óptimo" ? "alerta" : "exito";
}

export function HistorialPage() {
  const [filtro, setFiltro] = useState("todos");

  const visibles = ejecuciones.filter((ejecucion) => {
    if (filtro === "todos") return true;
    return ejecucion.metodo.toLowerCase() === filtro;
  });

  return (
    <>
      <PageHero
        eyebrow="Historial · HU-15 · HU-16"
        title="Historial y reportes"
        description="Consulta de ejecuciones anteriores, escenarios guardados y exportación de resultados"
        kpis={[
          { valor: "14", etiqueta: "Ejecuciones" },
          { valor: "4", etiqueta: "Escenarios" },
          { valor: "6", etiqueta: "Reportes" },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <Segmentado
            items={filtros}
            value={filtro}
            onChange={setFiltro}
            ariaLabel="Filtrar ejecuciones por método"
            className="w-full sm:w-auto"
          />
          <div className="flex flex-wrap gap-2">
            <Boton variante="acento" icono={<Download className="size-4" aria-hidden="true" />}>
              Exportar Excel
            </Boton>
            <Boton variante="acento" icono={<Download className="size-4" aria-hidden="true" />}>
              Exportar PDF
            </Boton>
          </div>
        </div>

        <Tarjeta relleno="none" className="mt-6 overflow-hidden">
          <div className="hidden overflow-x-auto scroll-fino md:block">
            <table className="tabla min-w-[760px]">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Método</th>
                  <th>Escenario</th>
                  <th className="text-right">Costo (COP/sem)</th>
                  <th className="text-right">Gap</th>
                  <th className="text-right">Estado</th>
                  <th className="w-[110px] text-right">
                    <span className="sr-only">Acciones</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {visibles.map((ejecucion) => (
                  <tr key={`${ejecucion.fecha}-${ejecucion.metodo}`}>
                    <td className="text-muted">{ejecucion.fecha}</td>
                    <td className="font-medium text-text">{ejecucion.metodo}</td>
                    <td className="text-text">{ejecucion.escenario}</td>
                    <td className="text-right font-semibold tabular-nums text-text">
                      {ejecucion.costo}
                    </td>
                    <td className="text-right tabular-nums text-muted">{ejecucion.gap}</td>
                    <td className="text-right">
                      <Etiqueta variante={estadoEtiqueta(ejecucion.estado)}>
                        {ejecucion.estado}
                      </Etiqueta>
                    </td>
                    <td className="text-right">
                      <button
                        type="button"
                        className="text-sm font-semibold text-primary hover:text-primary-dark"
                      >
                        Ver detalle
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="divide-y divide-border md:hidden">
            {visibles.map((ejecucion) => (
              <article key={`${ejecucion.fecha}-${ejecucion.metodo}`} className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="type-title-15 text-text">{ejecucion.escenario}</p>
                    <p className="mt-0.5 text-xs leading-4 text-muted">{ejecucion.fecha}</p>
                  </div>
                  <Etiqueta variante={estadoEtiqueta(ejecucion.estado)}>
                    {ejecucion.estado}
                  </Etiqueta>
                </div>
                <dl className="mt-3 grid grid-cols-3 gap-2 text-xs leading-4">
                  <div>
                    <dt className="text-muted">Método</dt>
                    <dd className="mt-0.5 font-semibold text-text">{ejecucion.metodo}</dd>
                  </div>
                  <div>
                    <dt className="text-muted">Costo</dt>
                    <dd className="mt-0.5 font-semibold tabular-nums text-text">
                      {ejecucion.costo}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-muted">Gap</dt>
                    <dd className="mt-0.5 font-semibold tabular-nums text-text">{ejecucion.gap}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border px-4 py-4">
            <p className="text-xs leading-4 text-muted">
              Mostrando {visibles.length} de 14 ejecuciones
            </p>
            <button
              type="button"
              className="text-sm font-semibold text-primary hover:text-primary-dark"
            >
              Cargar más
            </button>
          </div>
        </Tarjeta>
      </PageBody>
    </>
  );
}
