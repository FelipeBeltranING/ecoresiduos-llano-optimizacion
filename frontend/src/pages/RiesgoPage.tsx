import { Check, Minus } from "lucide-react";
import { useDeferredValue, useState } from "react";

import { useCriticidad } from "@/api/hooks";
import type { CriticidadNodo } from "@/api/tipos";
import { Cargando, ErrorApi, Vacio } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { KpiCard } from "@/components/ui/KpiCard";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatNumber } from "@/lib/format";

const decimal = (valor: number, digitos = 2) =>
  new Intl.NumberFormat("es-CO", {
    minimumFractionDigits: digitos,
    maximumFractionDigits: digitos,
  }).format(valor);

/** Pesos en décimas: α y β se eligen y γ = 1 − α − β. */
function usePesos() {
  const [alfa, setAlfa] = useState(5);
  const [beta, setBeta] = useState(3);
  const gamma = 10 - alfa - beta;
  return {
    alfa,
    beta,
    gamma,
    cambiarAlfa: (valor: number) => {
      setAlfa(valor);
      if (valor + beta > 10) setBeta(10 - valor);
    },
    cambiarBeta: (valor: number) => setBeta(Math.min(valor, 10 - alfa)),
    fijar: (pesos: number[]) => {
      setAlfa(Math.round(pesos[0] * 10));
      setBeta(Math.round(pesos[1] * 10));
    },
  };
}

function Deslizador(props: {
  id: string;
  etiqueta: string;
  ayuda: string;
  valor: number;
  maximo: number;
  onChange: (valor: number) => void;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <label htmlFor={props.id} className="type-label text-text">
          {props.etiqueta}
        </label>
        <span className="text-sm font-semibold tabular-nums">{decimal(props.valor / 10, 1)}</span>
      </div>
      <input
        id={props.id}
        type="range"
        min={0}
        max={props.maximo}
        step={1}
        value={props.valor}
        onChange={(e) => props.onChange(Number(e.target.value))}
        className="mt-2 h-11 w-full accent-[var(--color-primary)]"
      />
      <p className="text-xs text-muted">{props.ayuda}</p>
    </div>
  );
}

function BarraIce({ valor }: { valor: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 overflow-hidden rounded-full bg-bg" aria-hidden="true">
        <div className="h-full rounded-full bg-danger" style={{ width: `${valor * 100}%` }} />
      </div>
      <span className="tabular-nums">{decimal(valor, 3)}</span>
    </div>
  );
}

function FilaNodo({ nodo }: { nodo: CriticidadNodo }) {
  return (
    <tr className="border-t border-border align-top">
      <td className="py-3 pr-3 font-semibold tabular-nums">{nodo.ranking_ice}</td>
      <td className="py-3 pr-3">
        <p className="font-semibold">{nodo.codigo}</p>
        <p className="text-xs text-muted">{nodo.nombre}</p>
        <Etiqueta variante={nodo.tipo === "ACOPIO" ? "alerta" : "neutral"} className="mt-1">
          {nodo.tipo === "ACOPIO" ? "Acopio" : "Planta"}
        </Etiqueta>
      </td>
      <td className="py-3 pr-3 tabular-nums">{decimal(nodo.intermediacion, 3)}</td>
      <td className="py-3 pr-3 tabular-nums">{decimal(nodo.grado_entrada)}</td>
      <td className="py-3 pr-3">
        <p className="tabular-nums">{decimal(nodo.resiliencia, 1)}</p>
        <ul className="mt-1 space-y-0.5 text-xs text-muted">
          {Object.entries(nodo.mecanismos).map(([nombre, cumple]) => (
            <li key={nombre} className="flex items-center gap-1">
              {cumple ? (
                <Check className="size-3 text-primary" aria-label="cumple" />
              ) : (
                <Minus className="size-3" aria-label="no cumple" />
              )}
              {nombre}
            </li>
          ))}
        </ul>
      </td>
      <td className="py-3 pr-3">
        <BarraIce valor={nodo.ice} />
      </td>
      <td className="py-3 pr-3 tabular-nums">
        <p>+{decimal(nodo.delta_costo_pct, 1)} %</p>
        <p className="text-xs text-muted">
          {formatNumber(nodo.toneladas_sin_planta)} t sin planta · puesto {nodo.ranking_impacto}
        </p>
      </td>
    </tr>
  );
}

export function RiesgoPage() {
  const pesos = usePesos();
  const alfa = useDeferredValue(pesos.alfa);
  const beta = useDeferredValue(pesos.beta);
  const gamma = 10 - alfa - beta;
  const consulta = useCriticidad(alfa / 10, beta / 10, gamma / 10);
  const datos = consulta.data;
  const masCritico = datos?.nodos[0];

  return (
    <>
      <PageHero
        eyebrow="¿Qué pasa si falla una planta?"
        title="Riesgo de la red (ICE)"
        description="Índice de Criticidad Estructural: ICE = α·C_B + β·C_D⁻ + γ·(1 − R). Cada nodo se cierra y se vuelve a optimizar para comparar el ranking con el impacto real."
        kpis={
          datos
            ? [
                {
                  valor: masCritico ? masCritico.codigo : "—",
                  etiqueta: "Nodo más crítico",
                  tono: "peligro",
                },
                {
                  valor: datos.spearman == null ? "—" : decimal(datos.spearman),
                  etiqueta: "ρ de Spearman ICE vs. impacto",
                  tono: "acento",
                },
              ]
            : undefined
        }
      />
      <PageBody className="space-y-6">
        <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
          <Tarjeta className="space-y-5">
            <p className="type-title-15">Pesos del índice</p>
            <Deslizador
              id="alfa"
              etiqueta="α · intermediación (C_B)"
              ayuda="Fracción del flujo que pasa por el nodo"
              valor={pesos.alfa}
              maximo={10}
              onChange={pesos.cambiarAlfa}
            />
            <Deslizador
              id="beta"
              etiqueta="β · dependencia (C_D⁻)"
              ayuda="Empresas que envían residuo al nodo"
              valor={pesos.beta}
              maximo={10 - pesos.alfa}
              onChange={pesos.cambiarBeta}
            />
            <div className="flex items-baseline justify-between">
              <p className="type-label">γ · fragilidad (1 − R)</p>
              <span className="text-sm font-semibold tabular-nums">
                {decimal(pesos.gamma / 10, 1)}
              </span>
            </div>
            {datos?.pesos_calibrados ? (
              <button
                type="button"
                onClick={() => pesos.fijar(datos.pesos_calibrados ?? [])}
                className="min-h-11 w-full rounded-control border border-border px-3 py-2 text-left text-sm hover:bg-primary-soft"
              >
                Usar pesos calibrados (
                {datos.pesos_calibrados.map((p) => decimal(p, 1)).join(" · ")})
                <span className="block text-xs text-muted">
                  ρ = {decimal(datos.spearman_calibrado ?? 0)} con las fallas simuladas
                </span>
              </button>
            ) : null}
          </Tarjeta>

          <div className="space-y-4">
            {datos ? (
              <div className="grid gap-4 sm:grid-cols-3">
                <KpiCard
                  etiqueta="Más crítico según ICE"
                  valor={masCritico ? masCritico.codigo : "—"}
                  detalle={masCritico?.nombre ?? undefined}
                  tono="peligro"
                />
                <KpiCard
                  etiqueta="Si se cierra"
                  valor={masCritico ? `+${decimal(masCritico.delta_costo_pct, 0)} %` : "—"}
                  detalle={
                    masCritico
                      ? `${formatNumber(masCritico.toneladas_sin_planta)} t quedan sin planta`
                      : undefined
                  }
                />
                <KpiCard
                  etiqueta="ρ de Spearman"
                  valor={datos.spearman == null ? "—" : decimal(datos.spearman)}
                  detalle="1 = el ICE ordena igual que el impacto real"
                  tono="primario"
                />
              </div>
            ) : null}

            <Tarjeta relleno="none" className="overflow-x-auto p-4 sm:p-5">
              {consulta.isLoading ? <Cargando texto="Simulando la falla de cada nodo…" /> : null}
              {consulta.isError ? <ErrorApi error={consulta.error} /> : null}
              {datos && datos.nodos.length === 0 ? (
                <Vacio>Cargue una red con plantas para calcular el ICE.</Vacio>
              ) : null}
              {datos && datos.nodos.length > 0 ? (
                <table className="w-full min-w-[720px] text-left text-sm">
                  <thead className="type-label text-muted">
                    <tr>
                      <th className="pb-2 pr-3">#</th>
                      <th className="pb-2 pr-3">Nodo</th>
                      <th className="pb-2 pr-3">C_B</th>
                      <th className="pb-2 pr-3">C_D⁻</th>
                      <th className="pb-2 pr-3">R (mecanismos)</th>
                      <th className="pb-2 pr-3">ICE</th>
                      <th className="pb-2 pr-3">Impacto al cerrar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {datos.nodos.map((nodo) => (
                      <FilaNodo key={nodo.codigo} nodo={nodo} />
                    ))}
                  </tbody>
                </table>
              ) : null}
            </Tarjeta>

            {datos ? (
              <div className="space-y-1 text-xs text-muted">
                {datos.notas.map((nota) => (
                  <p key={nota}>{nota}</p>
                ))}
                <p>Adaptado de: {datos.referencia}</p>
              </div>
            ) : null}
          </div>
        </div>
      </PageBody>
    </>
  );
}
