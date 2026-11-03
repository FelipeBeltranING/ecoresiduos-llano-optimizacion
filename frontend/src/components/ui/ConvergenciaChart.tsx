interface ConvergenciaChartProps {
  className?: string;
}

type Punto = [number, number];

const ancho = 900;
const alto = 320;
const margen = { arriba: 24, derecha: 16, abajo: 40, izquierda: 64 };

const x = (generacion: number) =>
  margen.izquierda +
  (generacion / 200) * (ancho - margen.izquierda - margen.derecha);

const y = (millones: number) =>
  margen.arriba + ((74 - millones) / (74 - 64)) * (alto - margen.arriba - margen.abajo);

const mejorCosto: Punto[] = [
  [0, 70.3],
  [5, 70.3],
  [10, 69.9],
  [15, 69.5],
  [20, 69.1],
  [25, 68.6],
  [30, 68.4],
  [35, 67.9],
  [40, 67.5],
  [45, 67.3],
  [50, 66.8],
  [55, 66.6],
  [60, 66.5],
  [65, 66.2],
  [70, 66.1],
  [75, 65.8],
  [80, 65.6],
  [85, 65.4],
  [90, 65.2],
  [95, 65.1],
  [100, 64.99],
  [110, 64.93],
  [120, 64.86],
  [135, 64.82],
  [150, 64.77],
  [165, 64.74],
  [180, 64.71],
  [200, 64.69],
];

const costoPromedio: Punto[] = [
  [0, 73.0],
  [8, 71.7],
  [15, 71.0],
  [22, 70.3],
  [30, 70.2],
  [38, 69.6],
  [46, 69.2],
  [54, 68.9],
  [62, 68.2],
  [70, 67.9],
  [78, 67.4],
  [86, 67.1],
  [94, 67.2],
  [102, 66.9],
  [110, 66.6],
  [118, 66.7],
  [126, 66.4],
  [134, 66.5],
  [142, 66.3],
  [150, 66.4],
  [158, 66.2],
  [166, 66.3],
  [174, 66.2],
  [182, 66.2],
  [190, 66.1],
  [200, 66.0],
];

function curva(puntos: Punto[]): string {
  let d = `M ${x(puntos[0][0])} ${y(puntos[0][1])}`;
  for (let i = 1; i < puntos.length; i += 1) {
    const [g0, v0] = puntos[i - 1];
    const [g1, v1] = puntos[i];
    const mx = (x(g0) + x(g1)) / 2;
    d += ` C ${mx} ${y(v0)}, ${mx} ${y(v1)}, ${x(g1)} ${y(v1)}`;
  }
  return d;
}

export function ConvergenciaChart({ className = "" }: ConvergenciaChartProps) {
  const ticksY = [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74];
  const ticksX = [0, 50, 100, 150, 200];
  const xParada = x(180);
  const yOptimo = y(64.69);

  return (
    <svg
      viewBox={`0 0 ${ancho} ${alto}`}
      role="img"
      aria-label="Convergencia del algoritmo genético: mejor costo y costo promedio por generación frente al óptimo exacto"
      className={["block w-full", className].join(" ")}
    >
      {ticksY.map((tick) => (
        <g key={tick}>
          <line
            x1={margen.izquierda}
            x2={ancho - margen.derecha}
            y1={y(tick)}
            y2={y(tick)}
            stroke="#E3E9E5"
            strokeWidth="1"
          />
          <text
            x={margen.izquierda - 12}
            y={y(tick) + 4}
            textAnchor="end"
            fontSize="12"
            fontFamily="Inter, sans-serif"
            fill="#5B6B62"
          >
            ${tick} M
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
          fontFamily="Inter, sans-serif"
          fill="#5B6B62"
        >
          {tick}
        </text>
      ))}

      <text
        x={(margen.izquierda + ancho - margen.derecha) / 2}
        y={alto - 2}
        textAnchor="middle"
        fontSize="12"
        fontFamily="Inter, sans-serif"
        fill="#5B6B62"
      >
        Generación
      </text>

      {/* Parada anticipada */}
      <line
        x1={xParada}
        x2={xParada}
        y1={margen.arriba}
        y2={alto - margen.abajo}
        stroke="#5B6B62"
        strokeWidth="1.5"
        strokeDasharray="4 4"
      />
      <text
        x={xParada - 8}
        y={margen.arriba + 8}
        textAnchor="end"
        fontSize="12"
        fontFamily="Inter, sans-serif"
        fill="#17201B"
      >
        Parada: 50 generaciones sin mejora
      </text>

      {/* Óptimo exacto */}
      <line
        x1={margen.izquierda}
        x2={ancho - margen.derecha}
        y1={yOptimo}
        y2={yOptimo}
        stroke="#17201B"
        strokeWidth="1.5"
        strokeDasharray="6 4"
      />
      <text
        x={margen.izquierda + 6}
        y={yOptimo - 8}
        fontSize="12"
        fontFamily="Inter, sans-serif"
        fill="#17201B"
      >
        Óptimo exacto $64,69 M
      </text>

      <path d={curva(costoPromedio)} fill="none" stroke="#B7791F" strokeWidth="2" />
      <path d={curva(mejorCosto)} fill="none" stroke="#1F7A4D" strokeWidth="2.5" />
    </svg>
  );
}
