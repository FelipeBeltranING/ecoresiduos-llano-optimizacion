import { flujos, plantas } from "@/data/red";

type Tono = "oscuro" | "claro";

interface RedMapaProps {
  tono?: Tono;
  className?: string;
  mostrarLeyenda?: boolean;
  mostrarEscala?: boolean;
  etiqueta?: string;
}

interface Punto {
  x: number;
  y: number;
  dx: number;
  dy: number;
  anchor: "start" | "end" | "middle";
}

const puntosEmpresa: Record<string, Punto> = {
  E01: { x: 430, y: 45, dx: 12, dy: 4, anchor: "start" },
  E06: { x: 228, y: 112, dx: 14, dy: 4, anchor: "start" },
  E07: { x: 480, y: 148, dx: 12, dy: 4, anchor: "start" },
  E02: { x: 432, y: 232, dx: 12, dy: 4, anchor: "start" },
  E05: { x: 120, y: 238, dx: -12, dy: 4, anchor: "end" },
  E08: { x: 160, y: 292, dx: 12, dy: 4, anchor: "start" },
  E03: { x: 152, y: 348, dx: 12, dy: 4, anchor: "start" },
  E04: { x: 332, y: 358, dx: 12, dy: 4, anchor: "start" },
  E09: { x: 190, y: 428, dx: 12, dy: 4, anchor: "start" },
  E10: { x: 32, y: 408, dx: -8, dy: 4, anchor: "end" },
};

const puntosPlanta: Record<string, Punto> = {
  P01: { x: 186, y: 198, dx: -14, dy: 4, anchor: "end" },
  P02: { x: 196, y: 108, dx: -14, dy: 4, anchor: "end" },
  P03: { x: 176, y: 392, dx: -12, dy: -10, anchor: "end" },
  P04: { x: 772, y: 138, dx: -12, dy: -12, anchor: "end" },
};

const colores = {
  oscuro: {
    flujo: "#8FD6AE",
    empresa: "#B7791F",
    planta: "#FFFFFF",
    plantaSaturada: "#C2410C",
    etiqueta: "#D7E9DF",
    plantaEtiqueta: "#FFFFFF",
    leyenda: "#D7E9DF",
  },
  claro: {
    flujo: "#1F7A4D",
    empresa: "#B7791F",
    planta: "#1F7A4D",
    plantaSaturada: "#C2410C",
    etiqueta: "#17201B",
    plantaEtiqueta: "#17201B",
    leyenda: "#17201B",
  },
};

const anchoFlujo = (toneladas: number) => 1.5 + (toneladas / 140) * 5.5;

export function RedMapa({
  tono = "oscuro",
  className = "",
  mostrarLeyenda = false,
  mostrarEscala = false,
  etiqueta = "Mapa esquemático de la red: empresas, plantas y flujos óptimos",
}: RedMapaProps) {
  const c = colores[tono];

  return (
    <svg
      viewBox="0 0 800 500"
      role="img"
      aria-label={etiqueta}
      className={["block h-full w-full", className].join(" ")}
      preserveAspectRatio="xMidYMid meet"
    >
      <rect width="800" height="500" fill="transparent" />

      {mostrarLeyenda ? (
        <g fontSize="12" fontFamily="Inter, sans-serif" fill={c.leyenda}>
          <circle cx="22" cy="24" r="5" fill={c.empresa} />
          <text x="34" y="28">
            Empresa
          </text>
          <rect x="112" y="19" width="11" height="11" rx="2" fill={c.planta} />
          <text x="130" y="28">
            Planta
          </text>
          <rect x="199" y="19" width="11" height="11" rx="2" fill={c.plantaSaturada} />
          <text x="217" y="28">
            Planta saturada
          </text>
        </g>
      ) : null}

      {/* Flujos óptimos */}
      {flujos.map((flujo) => {
        const origen = puntosEmpresa[flujo.empresa];
        const destino = puntosPlanta[flujo.planta];
        return (
          <line
            key={`${flujo.empresa}-${flujo.planta}`}
            x1={origen.x}
            y1={origen.y}
            x2={destino.x}
            y2={destino.y}
            stroke={c.flujo}
            strokeWidth={anchoFlujo(flujo.toneladas)}
            strokeLinecap="round"
            strokeOpacity={tono === "oscuro" ? 0.9 : 0.45}
          />
        );
      })}

      {/* Plantas */}
      {plantas.map((planta) => {
        const punto = puntosPlanta[planta.codigo];
        const relleno = planta.saturada ? c.plantaSaturada : c.planta;
        return (
          <g key={planta.codigo}>
            <rect
              x={punto.x - 8}
              y={punto.y - 8}
              width="16"
              height="16"
              rx="3"
              fill={relleno}
              stroke={tono === "oscuro" ? "#12392A" : "#E8F3EC"}
              strokeWidth="1.5"
            />
            <text
              x={punto.x + punto.dx}
              y={punto.y + punto.dy}
              textAnchor={punto.anchor}
              fontSize="13"
              fontFamily="Inter, sans-serif"
              fontWeight="600"
              fill={c.plantaEtiqueta}
            >
              {planta.nombre}
            </text>
          </g>
        );
      })}

      {/* Empresas */}
      {Object.entries(puntosEmpresa).map(([codigo, punto]) => (
        <g key={codigo}>
          <circle cx={punto.x} cy={punto.y} r="5" fill={c.empresa} />
          <text
            x={punto.x + punto.dx}
            y={punto.y + punto.dy}
            textAnchor={punto.anchor}
            fontSize="11"
            fontFamily="Inter, sans-serif"
            fontWeight="500"
            fill={c.etiqueta}
          >
            {codigo}
          </text>
        </g>
      ))}

      {mostrarEscala ? (
        <g fontFamily="Inter, sans-serif" fill={c.leyenda}>
          <line
            x1="700"
            y1="472"
            x2="778"
            y2="472"
            stroke={c.leyenda}
            strokeWidth="2"
            strokeLinecap="round"
          />
          <text x="700" y="464" fontSize="11">
            50 km
          </text>
        </g>
      ) : null}
    </svg>
  );
}
