import { CircleAlert, CircleCheck } from "lucide-react";
import type { InputHTMLAttributes } from "react";

type Estado = "normal" | "exito" | "error";

interface CampoProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "className"> {
  etiqueta: string;
  ayuda?: string;
  estado?: Estado;
  contenedorClassName?: string;
}

const estados: Record<Estado, string> = {
  normal: "border-border",
  exito: "border-primary",
  error: "border-danger",
};

export function Campo({
  etiqueta,
  ayuda,
  estado = "normal",
  id,
  contenedorClassName = "",
  ...props
}: CampoProps) {
  const inputId = id ?? `campo-${etiqueta.toLowerCase().replace(/\s+/g, "-")}`;
  const Icono = estado === "error" ? CircleAlert : CircleCheck;
  const ayudaColor =
    estado === "error" ? "text-danger" : estado === "exito" ? "text-muted" : "text-muted";

  return (
    <div className={["flex flex-col gap-1", contenedorClassName].join(" ")}>
      <label htmlFor={inputId} className="type-label text-text">
        {etiqueta}
      </label>
      <div className="relative">
        <input
          id={inputId}
          className={[
            "h-10 w-full rounded-control border bg-surface px-3 text-sm text-text outline-none transition-colors",
            "placeholder:text-muted/70 focus:border-primary",
            estados[estado],
            estado !== "normal" ? "pr-9" : "",
          ].join(" ")}
          aria-invalid={estado === "error" || undefined}
          {...props}
        />
        {estado !== "normal" ? (
          <Icono
            aria-hidden="true"
            className={[
              "pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2",
              estado === "error" ? "text-danger" : "text-primary",
            ].join(" ")}
          />
        ) : null}
      </div>
      {ayuda ? <p className={["text-xs leading-4", ayudaColor].join(" ")}>{ayuda}</p> : null}
    </div>
  );
}
