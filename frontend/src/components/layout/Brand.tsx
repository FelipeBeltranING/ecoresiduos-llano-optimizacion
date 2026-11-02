import { Recycle } from "lucide-react";
import { Link } from "react-router-dom";

interface BrandProps {
  onNavigate?: () => void;
}

export function Brand({ onNavigate }: BrandProps) {
  return (
    <Link
      to="/"
      onClick={onNavigate}
      className="flex items-center gap-3 rounded-xl"
      aria-label="EcoResiduos del Llano, ir al panel"
    >
      <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-brand-700 text-white shadow-sm">
        <Recycle className="size-5" aria-hidden="true" />
      </span>
      <span className="min-w-0 leading-tight">
        <span className="block truncate text-sm font-semibold tracking-tight text-slate-900">
          EcoResiduos
        </span>
        <span className="block truncate text-xs text-slate-500">del Llano · Grupo Orion</span>
      </span>
    </Link>
  );
}
