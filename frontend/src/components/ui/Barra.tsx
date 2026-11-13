interface BarraProps {
  
  valor: number;
  tono?: "primario" | "peligro" | "acento";
  className?: string;
  etiqueta?: string;
}

const tonos = {
  primario: "bg-primary",
  peligro: "bg-danger",
  acento: "bg-accent",
};

export function Barra({ valor, tono = "primario", className = "", etiqueta }: BarraProps) {
  const porcentaje = Math.max(0, Math.min(1, valor)) * 100;
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(porcentaje)}
      aria-label={etiqueta}
      className={["h-2 w-full overflow-hidden rounded-full bg-primary-soft", className].join(" ")}
    >
      <div
        className={["h-full rounded-full transition-[width]", tonos[tono]].join(" ")}
        style={{ width: `${porcentaje}%` }}
      />
    </div>
  );
}
