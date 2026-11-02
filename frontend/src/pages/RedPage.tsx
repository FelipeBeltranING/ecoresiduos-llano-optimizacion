import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { useState } from "react";

import { Barra } from "@/components/ui/Barra";
import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { empresas, plantas, totalCapacidad, totalOferta } from "@/data/red";
import { formatNumber } from "@/lib/format";

const tabs = [
  { label: "Empresas", value: "empresas" },
  { label: "Plantas", value: "plantas" },
  { label: "Centros de acopio", value: "acopios" },
];

export function RedPage() {
  const [tab, setTab] = useState("empresas");
  const [busqueda, setBusqueda] = useState("");
  const [mostrarTodas, setMostrarTodas] = useState(false);
  const [formAbierto, setFormAbierto] = useState(false);

  const termino = busqueda.trim().toLowerCase();
  const filtradas = empresas.filter((empresa) =>
    `${empresa.codigo} ${empresa.nombre} ${empresa.municipio}`.toLowerCase().includes(termino),
  );
  const visiblesMovil = mostrarTodas ? filtradas : filtradas.slice(0, 5);

  return (
    <>
      <PageHero
        eyebrow="Red logística · HU-01"
        title="Empresas aliadas"
        description="10 empresas fuente que generan residuos agropecuarios cada semana"
        kpis={[
          { valor: `${totalOferta} t`, etiqueta: "Oferta total" },
          { valor: `${totalCapacidad} t`, etiqueta: "Capacidad" },
          { valor: `${totalCapacidad - totalOferta} t`, etiqueta: "Holgura" },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <Segmentado
            items={tabs}
            value={tab}
            onChange={setTab}
            ariaLabel="Tipo de nodo de la red"
            className="w-full sm:w-auto"
          />

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="relative">
              <Search
                className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted"
                aria-hidden="true"
              />
              <input
                type="search"
                value={busqueda}
                onChange={(event) => setBusqueda(event.target.value)}
                placeholder="Buscar empresa o municipio"
                aria-label="Buscar empresa o municipio"
                className="h-10 w-full rounded-control border border-border bg-surface pl-9 pr-3 text-sm text-text outline-none placeholder:text-muted/80 focus:border-primary sm:w-[280px]"
              />
            </div>
            <div className="hidden sm:block">
              <Boton onClick={() => setFormAbierto((abierto) => !abierto)}>Nueva empresa</Boton>
            </div>
          </div>
        </div>

        {tab === "empresas" ? (
          <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1fr)_400px]">
            <Tarjeta relleno="none" className="overflow-hidden">
              <div className="hidden overflow-x-auto scroll-fino md:block">
                <table className="tabla table-fixed">
                  <colgroup>
                    <col className="w-16" />
                    <col />
                    <col className="w-[160px]" />
                    <col className="w-[188px]" />
                    <col className="w-[104px]" />
                    <col className="w-[64px]" />
                  </colgroup>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Empresa</th>
                      <th>Municipio</th>
                      <th>Tipo de residuo</th>
                      <th className="text-right">Oferta (t/sem) ↓</th>
                      <th>
                        <span className="sr-only">Acciones</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtradas.map((empresa) => (
                      <tr key={empresa.codigo}>
                        <td className="font-semibold text-primary">{empresa.codigo}</td>
                        <td className="font-medium text-text">{empresa.nombre}</td>
                        <td className="whitespace-nowrap text-muted">{empresa.municipio}</td>
                        <td className="whitespace-nowrap text-muted">{empresa.residuo}</td>
                        <td className="text-right font-semibold tabular-nums text-text">
                          {empresa.oferta}
                        </td>
                        <td className="text-right">
                          <button
                            type="button"
                            className="text-sm font-semibold text-primary hover:text-primary-dark"
                          >
                            Editar
                          </button>
                        </td>
                      </tr>
                    ))}
                    {filtradas.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-10 text-center text-sm text-muted">
                          No se encontraron empresas con “{busqueda}”.
                        </td>
                      </tr>
                    ) : null}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td
                        colSpan={4}
                        className="border-t border-border px-3 py-3 text-sm font-semibold text-text"
                      >
                        Total de la oferta semanal
                      </td>
                      <td className="border-t border-border px-3 py-3 text-right font-semibold tabular-nums text-text">
                        {totalOferta}
                      </td>
                      <td className="border-t border-border py-3 pl-1 pr-3 text-xs text-muted">t</td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              <div className="divide-y divide-border md:hidden">
                {visiblesMovil.map((empresa) => (
                  <article key={empresa.codigo} className="p-3">
                    <div className="rounded-control border border-border p-3">
                      <div className="flex items-start justify-between gap-3">
                        <span className="text-xs font-medium leading-4 text-primary">
                          {empresa.codigo}
                        </span>
                        <div className="text-right">
                          <p className="type-title-15 tabular-nums text-text">
                            {empresa.oferta} t
                          </p>
                          <p className="text-[11px] leading-4 text-muted">por semana</p>
                        </div>
                      </div>
                      <p className="mt-1 type-title-15 text-text">{empresa.nombre}</p>
                      <p className="mt-1 text-[13px] leading-5 text-muted">
                        {empresa.municipio} · {empresa.residuo}
                      </p>
                    </div>
                  </article>
                ))}
              </div>

              {!mostrarTodas && filtradas.length > 5 ? (
                <div className="px-3 pb-3 md:hidden">
                  <Boton
                    variante="secundario"
                    className="w-full"
                    onClick={() => setMostrarTodas(true)}
                  >
                    Mostrar las {filtradas.length - 5} restantes
                  </Boton>
                </div>
              ) : null}

              <div className="flex flex-col gap-3 border-t border-border px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-xs leading-4 text-muted">
                  Mostrando 1–{filtradas.length} de {filtradas.length} empresas
                </p>
                <div className="hidden items-center gap-1 sm:flex">
                  <button
                    type="button"
                    aria-label="Página anterior"
                    disabled
                    className="grid size-8 place-items-center rounded-control border border-border text-muted disabled:opacity-50"
                  >
                    <ChevronLeft className="size-4" aria-hidden="true" />
                  </button>
                  <span className="grid size-8 place-items-center rounded-control bg-primary text-sm font-semibold text-white">
                    1
                  </span>
                  <button
                    type="button"
                    aria-label="Página siguiente"
                    disabled
                    className="grid size-8 place-items-center rounded-control border border-border text-muted disabled:opacity-50"
                  >
                    <ChevronRight className="size-4" aria-hidden="true" />
                  </button>
                </div>
              </div>

              <div className="px-3 pb-3 sm:hidden">
                <Boton
                  className="w-full"
                  onClick={() => setFormAbierto((abierto) => !abierto)}
                  aria-expanded={formAbierto}
                >
                  Nueva empresa
                </Boton>
              </div>
            </Tarjeta>

            <Tarjeta className={formAbierto ? "block" : "hidden xl:block"}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="type-title-22 text-text">Nueva empresa</h2>
                  <p className="mt-1 max-w-sm text-xs leading-4 text-muted">
                    Los campos con * son obligatorios. Se valida mientras escribe.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setFormAbierto(false)}
                  className="text-sm font-semibold text-muted hover:text-text xl:hidden"
                >
                  Cerrar
                </button>
              </div>

              <form
                className="mt-4 flex flex-col gap-4"
                onSubmit={(event) => event.preventDefault()}
              >
                <Campo etiqueta="Código *" defaultValue="E11" estado="exito" ayuda="Código disponible" />
                <Campo
                  etiqueta="Nombre de la empresa *"
                  defaultValue="Porcícola La Sabana"
                  estado="exito"
                  ayuda="Nombre único en la red"
                />
                <Campo etiqueta="Municipio *" defaultValue="Guamal" ayuda="Municipio del Meta" />

                <div className="flex flex-col gap-1">
                  <label htmlFor="tipo-residuo" className="type-label text-text">
                    Tipo de residuo *
                  </label>
                  <select
                    id="tipo-residuo"
                    defaultValue="ganaderia"
                    className="h-10 w-full rounded-control border border-border bg-surface px-3 text-sm text-text outline-none focus:border-primary"
                  >
                    <option value="ganaderia">Ganadería (estiércol)</option>
                    <option value="palma">Palma (raquis, fibra)</option>
                    <option value="arroz">Arroz (cascarilla)</option>
                    <option value="forestal">Forestal (aserrín, corteza)</option>
                  </select>
                  <p className="text-xs leading-4 text-muted">Define el uso del residuo</p>
                </div>

                <Campo
                  etiqueta="Oferta semanal (t) *"
                  type="number"
                  defaultValue={0}
                  estado="error"
                  ayuda="La oferta debe ser mayor que 0"
                />

                <div className="grid grid-cols-2 gap-3">
                  <Campo
                    etiqueta="Latitud"
                    defaultValue="3.88"
                    estado="exito"
                    ayuda="Válida"
                  />
                  <Campo
                    etiqueta="Longitud"
                    placeholder="Ej. −73.77"
                    estado="error"
                    ayuda="Requerida para el mapa"
                  />
                </div>

                <div className="rounded-card bg-primary-soft p-4">
                  <p className="type-title-15 text-primary-dark">Efecto en la red</p>
                  <p className="mt-1 text-xs leading-4 text-primary-dark/80">
                    Con 0 t la oferta sigue en 890 t frente a 950 t de capacidad. Si la oferta
                    supera la capacidad, se agrega una planta ficticia con la diferencia.
                  </p>
                </div>

                <div className="flex flex-wrap justify-end gap-2">
                  <Boton variante="secundario" onClick={() => setFormAbierto(false)}>
                    Cancelar
                  </Boton>
                  <Boton type="submit">Guardar empresa</Boton>
                </div>
              </form>
            </Tarjeta>
          </div>
        ) : null}

        {tab === "plantas" ? (
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {plantas.map((planta) => {
              const porcentaje = Math.round((planta.uso / planta.capacidad) * 100);
              return (
                <Tarjeta key={planta.codigo}>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-xs font-medium leading-4 text-primary">{planta.codigo}</p>
                      <h2 className="mt-1 type-title-18 text-text">{planta.nombre}</h2>
                    </div>
                    <Etiqueta variante={planta.saturada ? "peligro" : "exito"}>
                      {planta.saturada ? "Saturada" : "Con holgura"}
                    </Etiqueta>
                  </div>
                  <p className="mt-4 type-cifra-28 tabular-nums text-text">
                    {planta.uso} / {planta.capacidad} t
                  </p>
                  <Barra
                    valor={planta.uso / planta.capacidad}
                    tono={planta.saturada ? "peligro" : "primario"}
                    className="mt-3"
                    etiqueta={`Uso de ${planta.nombre}`}
                  />
                  <dl className="mt-4 space-y-2 text-xs leading-4">
                    <div className="flex justify-between gap-2">
                      <dt className="text-muted">Ocupación</dt>
                      <dd className="font-semibold tabular-nums text-text">{porcentaje} %</dd>
                    </div>
                    <div className="flex justify-between gap-2">
                      <dt className="text-muted">Costo de operación</dt>
                      <dd className="font-semibold tabular-nums text-text">
                        ${formatNumber(planta.operacion)} / t
                      </dd>
                    </div>
                    <div className="flex justify-between gap-2">
                      <dt className="text-muted">Precio sombra</dt>
                      <dd
                        className={[
                          "font-semibold tabular-nums",
                          planta.precioSombra < 0 ? "text-danger" : "text-text",
                        ].join(" ")}
                      >
                        {planta.precioSombra < 0
                          ? `−$${formatNumber(-planta.precioSombra)}`
                          : "$0"}
                      </dd>
                    </div>
                  </dl>
                </Tarjeta>
              );
            })}
          </div>
        ) : null}

        {tab === "acopios" ? (
          <Tarjeta className="mt-6">
            <h2 className="type-title-18 text-text">Centros de acopio</h2>
            <p className="mt-1 max-w-2xl text-sm leading-5 text-muted">
              Todavía no hay centros de acopio configurados. En el caso base, las 10 empresas
              entregan directamente a las 4 plantas de procesamiento, por lo que esta capa no
              altera el óptimo.
            </p>
            <div className="mt-4 rounded-card border border-dashed border-border bg-bg p-6 text-sm text-muted">
              Agregue un centro de acopio para consolidar la oferta de varias empresas antes de
              enviarla a una planta.
            </div>
          </Tarjeta>
        ) : null}
      </PageBody>
    </>
  );
}
