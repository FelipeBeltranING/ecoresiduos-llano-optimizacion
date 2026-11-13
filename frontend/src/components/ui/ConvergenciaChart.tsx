import { formatNumber } from "@/lib/format";

export interface PuntoConvergencia {
  generacion: number;
  mejor: number;
  promedio: number;
}

interface ConvergenciaChartProps {
  puntos: PuntoConvergencia[];
  /** Costo óptimo del modelo exacto, dibujado como referencia. */
  optimo?: number | null;
  className?: string;
}

const ancho = 900;
const alto = 320;
const margen = { arriba: 24, derecha: 16, abajo: 40, izquierda: 72 };

function ticks(minimo: number, maximo: number, cantidad: number): number[] {
  if (maximo <= minimo) return [minimo];
  const paso = (maximo - minimo) / (cantidad - 1);
  return Array.from({ length: cantidad }, (_, i) => minimo + i * paso);
}

/** Mejor costo y costo promedio por generación del AG frente al óptimo exacto (HU-10). */
export function ConvergenciaChart({ puntos, optimo, className = "" }: ConvergenciaChartProps) {
  if (puntos.length === 0) return null;

  
  const promedios = [...puntos.map((p) => p.promedio)].sort((a, b) => a - b);
  const techo = promedios[Math.floor(promedios.length * 0.9)] ?? promedios[promedios.length - 1];
  const valores = [...puntos.map((p) => p.mejor), techo, ...(optimo ? [optimo] : [])];
  const minimo = Math.min(...valores) * 0.995;
  const maximo = Math.max(...valores) * 1.005;
  const ultimaGeneracion = Math.max(1, puntos[puntos.length - 1].generacion);

  const x = (g: number) =>
    margen.izquierda + (g / ultimaGeneracion) * (ancho - margen.izquierda - margen.derecha);
  const y = (v: number) =>
    margen.arriba +
    ((maximo - Math.min(v, maximo)) / (maximo - minimo || 1)) *
      (alto - margen.arriba - margen.abajo);
  const linea = (campo: "mejor" | "promedio") =>
    puntos
      .map(
        (p, i) => `${i === 0 ? "M" : "L"} ${x(p.generacion).toFixed(1)} ${y(p[campo]).toFixed(1)}`,
      )
      .join(" ");

  const ticksY = ticks(minimo, maximo, 6);
  const ticksX = ticks(0, ultimaGeneracion, 5).map(Math.round);

  return (
    <figure className={className}>
      <svg
        viewBox={`0 0 ${ancho} ${alto}`}
        role="img"
        aria-label="Convergencia del algoritmo genético: mejor costo y costo promedio por generación"
        className="block w-full"
      >
        {ticksY.map((tick) => (
          <g key={tick}>
            <line
              x1={margen.izquierda}
              x2={ancho - margen.derecha}
              y1={y(tick)}
              y2={y(tick)}
              stroke="#E3E9E5"
            />
            <text
              x={margen.izquierda - 10}
              y={y(tick) + 4}
              textAnchor="end"
              fontSize="12"
              fill="#5B6B62"
            >
              ${formatNumber(tick / 1e6)} M
            </text>
          </g>
        ))}
        {ticksX.map((tick) => (
          <text
            key={tick}
            x={x(tick)}
            y={alto - 18}
            textAnchor="middle"
            fontSize="12"
            fill="#5B6B62"
          >
            {tick}
          </text>
        ))}
        <text
          x={(margen.izquierda + ancho) / 2}
          y={alto - 2}
          textAnchor="middle"
          fontSize="12"
          fill="#5B6B62"
        >
          Generación
        </text>
        {optimo ? (
          <g>
            <line
              x1={margen.izquierda}
              x2={ancho - margen.derecha}
              y1={y(optimo)}
              y2={y(optimo)}
              stroke="#17201B"
              strokeWidth="1.5"
              strokeDasharray="6 4"
            />
            <text x={margen.izquierda + 6} y={y(optimo) - 8} fontSize="12" fill="#17201B">
              Óptimo exacto ${formatNumber(optimo / 1e6)} M
            </text>
          </g>
        ) : null}
        <path d={linea("promedio")} fill="none" stroke="#B7791F" strokeWidth="2" />
        <path d={linea("mejor")} fill="none" stroke="#1F7A4D" strokeWidth="2.5" />
      </svg>
      <figcaption className="mt-2 flex flex-wrap gap-4 text-xs text-muted">
        <span className="flex items-center gap-1">
          <span className="h-1 w-4 rounded bg-primary" /> Mejor costo
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1 w-4 rounded bg-accent" /> Costo promedio de la población
        </span>
      </figcaption>
    </figure>
  );
}
