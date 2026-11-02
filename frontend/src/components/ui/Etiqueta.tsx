import type { ReactNode } from "react";

type Variante = "exito" | "alerta" | "peligro" | "neutral";

interface EtiquetaProps {
  children: ReactNode;
  variante?: Variante;
  className?: string;
}

const variantes: Record<Variante, string> = {
  exito: "bg-primary-soft text-primary-dark",
  alerta: "bg-accent-soft text-accent",
  peligro: "bg-danger-soft text-danger",
  neutral: "bg-white text-primary-dark",
};

export function Etiqueta({ children, variante = "exito", className = "" }: EtiquetaProps) {
  return (
    <span
      className={[
        "inline-flex items-center whitespace-nowrap rounded-full px-2 py-1 text-xs font-medium leading-4",
        variantes[variante],
        className,
      ].join(" ")}
    >
      {children}
    </span>
  );
}
