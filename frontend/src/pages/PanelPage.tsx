import {
  ArrowUpRight,
  Building2,
  CircleCheck,
  CircleDashed,
  Factory,
  Route as RouteIcon,
  Wallet,
} from "lucide-react";
import { Link } from "react-router-dom";

import { API_URL } from "@/api";
import { PageHeader } from "@/components/ui/PageHeader";

const indicators = [
  { label: "Empresas activas", hint: "HU-01", icon: Building2 },
  { label: "Plantas de procesamiento", hint: "HU-02", icon: Factory },
  { label: "Rutas habilitadas", hint: "HU-03", icon: RouteIcon },
  { label: "Costo total de la red", hint: "HU-07", icon: Wallet },
];

const workPath = [
  {
    to: "/red",
    title: "Cargar la red",
    detail: "Empresas, plantas y centros de acopio",
    issues: "HU-01 · HU-02",
  },
  {
    to: "/rutas",
    title: "Completar distancias",
    detail: "Matriz de costos y rutas habilitadas",
    issues: "HU-03",
  },
  {
    to: "/exacto",
    title: "Resolver el modelo",
    detail: "Óptimo exacto con PuLP y CBC",
    issues: "HU-07",
  },
  {
    to: "/ag",
    title: "Comparar con el AG",
    detail: "Convergencia y brecha frente al óptimo",
    issues: "HU-09 · HU-13",
  },
];

export function PanelPage() {
  return (
    <section className="space-y-6">
      <PageHeader
        title="Panel de control"
        description="Vista general de la red logística de EcoResiduos del Llano. Los indicadores se activarán cuando el backend exponga los endpoints de la red."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {indicators.map(({ label, hint, icon: Icon }) => (
          <article
            key={label}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel"
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm font-medium text-slate-600">{label}</p>
              <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-slate-50 text-slate-500">
                <Icon className="size-4" aria-hidden="true" />
              </span>
            </div>
            <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">—</p>
            <p className="mt-1 text-xs text-slate-400">Pendiente · {hint}</p>
          </article>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-base font-semibold text-slate-900">Ruta de trabajo</h2>
            <span className="text-xs text-slate-400">Sprint 1</span>
          </div>
          <ol className="mt-4 grid gap-3 sm:grid-cols-2">
            {workPath.map((step, index) => (
              <li key={step.to}>
                <Link
                  to={step.to}
                  className="group flex h-full flex-col justify-between gap-3 rounded-xl border border-slate-200 p-4 transition-colors hover:border-brand-300 hover:bg-brand-50/40"
                >
                  <div className="flex items-start gap-3">
                    <span className="grid size-7 shrink-0 place-items-center rounded-full bg-slate-900 text-xs font-semibold text-white">
                      {index + 1}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-slate-900">{step.title}</p>
                      <p className="mt-0.5 text-xs text-slate-500">{step.detail}</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-brand-700">
                    {step.issues}
                    <ArrowUpRight
                      className="size-3.5 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                      aria-hidden="true"
                    />
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </div>

        <aside className="rounded-2xl border border-slate-200 bg-white p-5 shadow-panel">
          <h2 className="text-base font-semibold text-slate-900">Estado del sprint</h2>
          <ul className="mt-4 space-y-3 text-sm">
            <li className="flex gap-3">
              <CircleCheck className="mt-0.5 size-4 shrink-0 text-brand-600" aria-hidden="true" />
              <span>
                <span className="font-medium text-slate-900">Frontend base</span>
                <span className="block text-xs text-slate-500">
                  Layout, router y cliente API (T-01c)
                </span>
              </span>
            </li>
            <li className="flex gap-3">
              <CircleCheck className="mt-0.5 size-4 shrink-0 text-brand-600" aria-hidden="true" />
              <span>
                <span className="font-medium text-slate-900">Integración continua</span>
                <span className="block text-xs text-slate-500">
                  GitHub Actions para lint, test y build (T-01d)
                </span>
              </span>
            </li>
            <li className="flex gap-3">
              <CircleDashed className="mt-0.5 size-4 shrink-0 text-slate-400" aria-hidden="true" />
              <span>
                <span className="font-medium text-slate-900">API y base de datos</span>
                <span className="block text-xs text-slate-500">
                  FastAPI, Supabase y migración V1 (T-01b)
                </span>
              </span>
            </li>
            <li className="flex gap-3">
              <CircleDashed className="mt-0.5 size-4 shrink-0 text-slate-400" aria-hidden="true" />
              <span>
                <span className="font-medium text-slate-900">Motores de optimización</span>
                <span className="block text-xs text-slate-500">
                  Modelo exacto y genético (HU-07 · HU-09)
                </span>
              </span>
            </li>
          </ul>
          <div className="mt-4 rounded-xl bg-slate-50 p-3">
            <p className="text-[11px] font-medium uppercase tracking-wider text-slate-400">API</p>
            <code className="mt-1 block break-all font-mono text-[11px] text-slate-700">
              {API_URL}
            </code>
          </div>
        </aside>
      </div>
    </section>
  );
}
