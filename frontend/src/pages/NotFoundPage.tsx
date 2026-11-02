import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="grid min-h-[50vh] place-items-center text-center">
      <div>
        <p className="text-sm font-semibold text-brand-700">404</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
          Página no encontrada
        </h1>
        <p className="mt-1 text-sm text-slate-600">La ruta que busca no existe o fue movida.</p>
        <Link
          to="/"
          className="mt-6 inline-flex rounded-xl bg-brand-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-800"
        >
          Volver al panel
        </Link>
      </div>
    </section>
  );
}
