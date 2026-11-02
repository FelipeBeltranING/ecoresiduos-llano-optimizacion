import { ArrowRight, CircleDashed, type LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";

import { PageHeader } from "./PageHeader";

interface ModulePlaceholderProps {
  title: string;
  description: string;
  icon: LucideIcon;
  issues: string[];
  upcoming: string[];
}

export function ModulePlaceholder({
  title,
  description,
  icon: Icon,
  issues,
  upcoming,
}: ModulePlaceholderProps) {
  return (
    <section className="space-y-6">
      <PageHeader title={title} description={description} />

      <div className="flex flex-col items-start gap-4 rounded-2xl border border-dashed border-slate-300 bg-white p-6 shadow-panel sm:flex-row sm:items-center">
        <span className="grid size-12 shrink-0 place-items-center rounded-2xl bg-brand-50 text-brand-700">
          <Icon className="size-6" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold text-slate-900">Módulo en construcción</h2>
            {issues.map((issue) => (
              <span
                key={issue}
                className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600"
              >
                {issue}
              </span>
            ))}
          </div>
          <p className="mt-1 text-sm text-slate-600">
            El layout, la navegación y el cliente de API ya están listos. Este módulo se conectará
            al backend en las historias indicadas.
          </p>
        </div>
        <Link
          to="/"
          className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-brand-700 hover:text-brand-800"
        >
          Volver al panel
          <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-slate-900">Qué incluirá</h3>
        <ul className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {upcoming.map((item) => (
            <li
              key={item}
              className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4"
            >
              <CircleDashed className="mt-0.5 size-4 shrink-0 text-slate-400" aria-hidden="true" />
              <span className="text-sm text-slate-700">{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
