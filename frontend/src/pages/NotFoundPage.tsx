import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="grid min-h-[60vh] place-items-center px-4 text-center">
      <div>
        <p className="type-eyebrow text-primary">404</p>
        <h1 className="mt-2 text-[30px] font-bold leading-9 tracking-[-0.02em] text-text sm:text-[44px] sm:leading-[48px]">
          Página no encontrada
        </h1>
        <p className="mt-1 text-sm leading-5 text-muted">La ruta que busca no existe o fue movida.</p>
        <Link
          to="/"
          className="mt-6 inline-flex rounded-control bg-primary px-4 py-2 text-sm font-semibold leading-5 text-white transition-colors hover:bg-primary-dark"
        >
          Volver al panel
        </Link>
      </div>
    </section>
  );
}
