import { CircleAlert, LoaderCircle } from "lucide-react";
import type { ReactNode } from "react";

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return (
    <p role="status" className="flex items-center gap-2 text-sm text-muted">
      <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
      {texto}
    </p>
  );
}

export function ErrorApi({ error }: { error: unknown }) {
  const mensaje = error instanceof Error ? error.message : "No se pudo completar la solicitud.";
  return (
    <p
      role="alert"
      className="flex items-start gap-2 rounded-control border border-danger/40 bg-danger-soft px-3 py-2 text-sm text-danger"
    >
      <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
      <span>{mensaje}</span>
    </p>
  );
}

export function Vacio({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-card border border-dashed border-border bg-bg px-4 py-8 text-center text-sm text-muted">
      {children}
    </div>
  );
}
