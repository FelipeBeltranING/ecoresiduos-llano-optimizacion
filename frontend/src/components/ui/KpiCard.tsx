interface KpiCardProps {
  etiqueta: string;
  valor: string;
  detalle?: string;
  tono?: "texto" | "primario" | "peligro" | "acento";
}

const tonos = {
  texto: "text-text",
  primario: "text-primary",
  peligro: "text-danger",
  acento: "text-accent",
};

export function KpiCard({ etiqueta, valor, detalle, tono = "texto" }: KpiCardProps) {
  return (
    <article className="rounded-card border border-border bg-surface p-5">
      <p className="type-label text-muted">{etiqueta}</p>
      <p
        className={[
          "mt-2 text-[24px] font-bold leading-7 tracking-[-0.015em] tabular-nums sm:text-[28px] sm:leading-8",
          tonos[tono],
        ].join(" ")}
      >
        {valor}
      </p>
      {detalle ? <p className="mt-1 text-xs leading-4 text-muted">{detalle}</p> : null}
    </article>
  );
}
