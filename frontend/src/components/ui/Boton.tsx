import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variante = "primario" | "secundario" | "acento" | "fantasma";
type Tamano = "md" | "lg";

interface BotonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante;
  tamano?: Tamano;
  icono?: ReactNode;
}

const variantes: Record<Variante, string> = {
  primario: "bg-primary text-white hover:bg-primary-dark",
  secundario: "border border-border bg-surface text-text hover:bg-primary-soft",
  acento: "border border-accent/70 bg-accent-soft text-text hover:bg-accent/20",
  fantasma: "text-primary hover:bg-primary-soft",
};

const tamanos: Record<Tamano, string> = {
  md: "px-4 py-2",
  lg: "px-5 py-3",
};

export function Boton({
  variante = "primario",
  tamano = "md",
  icono,
  className = "",
  children,
  type = "button",
  ...props
}: BotonProps) {
  return (
    <button
      type={type}
      className={[
        "inline-flex items-center justify-center gap-2 rounded-control text-sm font-semibold leading-5 transition-colors",
        "disabled:cursor-not-allowed disabled:opacity-50",
        variantes[variante],
        tamanos[tamano],
        className,
      ].join(" ")}
      {...props}
    >
      {icono}
      {children}
    </button>
  );
}
