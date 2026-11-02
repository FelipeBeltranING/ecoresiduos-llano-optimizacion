import { Barra } from "@/components/ui/Barra";
import { Boton } from "@/components/ui/Boton";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { FilaValidacion } from "@/components/ui/FilaValidacion";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { RedMapa } from "@/components/ui/RedMapa";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { costoOptimo, empresas, flujos, plantas } from "@/data/red";
import { formatNumber } from "@/lib/format";

export function ExactoPage() {
  return (
    <>
      <PageHero
        eyebrow="Optimización exacta · HU-07 · HU-08"
        title="Resultado del modelo exacto"
        description="Programación lineal con PuLP + CBC · caso base · 26 oct 2026"
        kpis={[
          { valor: "Óptimo", etiqueta: "Estado del solver" },
          { valor: `$${formatNumber(costoOptimo)}`, etiqueta: "Costo semanal Z*" },
          { valor: "11 de 40", etiqueta: "Rutas con flujo" },
        ]}
      />

      <PageBody>
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap items-center gap-3">
            <Etiqueta variante="exito">Solución óptima encontrada</Etiqueta>
            <p className="text-xs leading-4 text-muted">
              0 violaciones de restricciones · sin planta ficticia
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Boton variante="acento">Descargar Excel</Boton>
            <Boton variante="acento">Descargar PDF</Boton>
            <div className="hidden sm:block">
              <Boton>Volver a ejecutar</Boton>
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)]">
          <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
            <h2 className="px-5 pt-5 type-title-15 text-text">
              Flujos óptimos x<sub>ij</sub> (toneladas por semana)
            </h2>

            <div className="mt-4 hidden overflow-x-auto scroll-fino md:block">
              <table className="tabla min-w-[620px]">
                <thead>
                  <tr>
                    <th className="w-[200px]">Empresa</th>
                    {plantas.map((planta) => (
                      <th key={planta.codigo} className="w-[140px] text-right">
                        {planta.nombre}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {empresas.map((empresa) => (
                    <tr key={empresa.codigo}>
                      <td>
                        <span className="font-semibold text-text">{empresa.codigo}</span>{" "}
                        <span className="text-text">{empresa.nombre}</span>
                      </td>
                      {plantas.map((planta) => {
                        const flujo = flujos.find(
                          (item) =>
                            item.empresa === empresa.codigo && item.planta === planta.codigo,
                        );
                        return (
                          <td
                            key={planta.codigo}
                            className={[
                              "text-center tabular-nums",
                              flujo ? "bg-primary-soft font-semibold text-text" : "text-muted",
                            ].join(" ")}
                          >
                            {flujo ? formatNumber(flujo.toneladas) : "—"}
                          </td>
                        );
                      })}
                    </tr>
                  ))}

                  <tr className="bg-bg">
                    <td className="text-sm font-semibold text-text">Uso / capacidad (t)</td>
                    {plantas.map((planta) => (
                      <td
                        key={planta.codigo}
                        className={[
                          "text-center font-semibold tabular-nums",
                          planta.saturada ? "text-danger" : "text-text",
                        ].join(" ")}
                      >
                        {planta.uso} / {planta.capacidad}
                      </td>
                    ))}
                  </tr>
                  <tr className="bg-bg">
                    <td className="text-sm font-semibold text-text">Precio sombra (COP/t)</td>
                    {plantas.map((planta) => (
                      <td
                        key={planta.codigo}
                        className={[
                          "text-center font-semibold tabular-nums",
                          planta.precioSombra < 0 ? "text-danger" : "text-text",
                        ].join(" ")}
                      >
                        {planta.precioSombra < 0
                          ? `−${formatNumber(-planta.precioSombra)}`
                          : "0"}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="mt-4 space-y-3 px-4 pb-4 md:hidden">
              {plantas.map((planta) => {
                const flujosPlanta = flujos.filter((flujo) => flujo.planta === planta.codigo);
                return (
                  <article key={planta.codigo} className="rounded-card border border-border p-4">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="type-title-15 text-text">{planta.nombre}</h3>
                      <span
                        className={[
                          "text-sm font-semibold tabular-nums",
                          planta.saturada ? "text-danger" : "text-text",
                        ].join(" ")}
                      >
                        {planta.uso} / {planta.capacidad} t
                      </span>
                    </div>
                    <Barra
                      valor={planta.uso / planta.capacidad}
                      tono={planta.saturada ? "peligro" : "primario"}
                      className="mt-3"
                      etiqueta={`Uso de ${planta.nombre}`}
                    />
                    <div className="mt-2 flex items-center justify-between gap-2 text-xs leading-4">
                      <span className="text-muted">Precio sombra</span>
                      <span
                        className={[
                          "font-semibold tabular-nums",
                          planta.precioSombra < 0 ? "text-danger" : "text-text",
                        ].join(" ")}
                      >
                        {planta.precioSombra < 0
                          ? `−$${formatNumber(-planta.precioSombra)} / t`
                          : "$0 / t"}
                      </span>
                    </div>
                    <ul className="mt-3 space-y-2 border-t border-border pt-3">
                      {flujosPlanta.map((flujo) => (
                        <li
                          key={flujo.empresa}
                          className="flex items-center justify-between gap-2 text-[13px] leading-5"
                        >
                          <span className="text-text">
                            {flujo.empresa}{" "}
                            {empresas.find((empresa) => empresa.codigo === flujo.empresa)?.nombre}
                          </span>
                          <span className="font-semibold tabular-nums text-text">
                            {flujo.toneladas} t
                          </span>
                        </li>
                      ))}
                    </ul>
                  </article>
                );
              })}
            </div>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-15 text-text">Red con flujos óptimos</h2>
            <div className="mt-4 overflow-hidden rounded-card bg-primary-soft">
              <RedMapa
                tono="claro"
                etiqueta="Red con los flujos óptimos del modelo exacto"
              />
            </div>
            <p className="mt-3 text-xs leading-4 text-muted">
              Línea = toneladas por semana, de empresa (ámbar) a planta. Rojo: planta saturada.
              Esquema con coordenadas reales.
            </p>
          </Tarjeta>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <Tarjeta>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="type-title-15 text-text">Dónde se va el costo</h2>
              <p className="text-xs leading-4 text-muted">
                Suma: ${formatNumber(costoOptimo)} por semana
              </p>
            </div>
            <div className="mt-4 space-y-4">
              {plantas.map((planta) => (
                <div key={planta.codigo} className="flex items-center gap-3">
                  <span className="w-24 shrink-0 text-[13px] leading-5 text-text">
                    {planta.nombre}
                  </span>
                  <Barra
                    valor={planta.porcentajeCosto / 31.5}
                    className="flex-1"
                    etiqueta={`Participación de ${planta.nombre} en el costo`}
                  />
                  <span className="w-[92px] shrink-0 text-right text-[13px] font-semibold tabular-nums text-text">
                    ${formatNumber(planta.costoTotal)}
                  </span>
                  <span className="w-12 shrink-0 text-right text-[13px] tabular-nums text-muted">
                    {planta.porcentajeCosto.toLocaleString("es-CO", {
                      minimumFractionDigits: 1,
                    })}{" "}
                    %
                  </span>
                </div>
              ))}
            </div>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-15 text-text">Holguras y cuello de botella</h2>
            <div className="mt-4 space-y-4">
              <FilaValidacion
                estado="alerta"
                titulo="Villavicencio y Restrepo sin holgura"
                nota="0 t libres: cada tonelada extra ahorraría $17.750 y $14.250 por semana"
              />
              <FilaValidacion
                titulo="Granada y Puerto Gaitán con capacidad libre"
                nota="5 t y 55 t libres; su precio sombra es 0"
              />
              <FilaValidacion
                titulo="Restricciones de oferta y capacidad cumplidas"
                nota="Las 10 empresas colocan toda su oferta"
              />
            </div>
          </Tarjeta>
        </div>
      </PageBody>
    </>
  );
}
