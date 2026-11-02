import { CircleCheck, TriangleAlert } from "lucide-react";

interface FilaValidacionProps {
  titulo: string;
  nota: string;
  estado?: "correcto" | "alerta";
  className?: string;
}

export function FilaValidacion({
  titulo,
  nota,
  estado = "correcto",
  className = "",
}: FilaValidacionProps) {
  const isAlerta = estado === "alerta";
  return (
    <div className={["flex items-start gap-3", className].join(" ")}>
      {isAlerta ? (
        <TriangleAlert className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden="true" />
      ) : (
        <CircleCheck className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden="true" />
      )}
      <div className="min-w-0">
        <p className="type-cuerpo-strong text-text">{titulo}</p>
        <p className="mt-0.5 text-xs leading-4 text-muted">{nota}</p>
      </div>
    </div>
  );
}
