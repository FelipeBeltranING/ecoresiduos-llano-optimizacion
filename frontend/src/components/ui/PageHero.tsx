import type { ReactNode } from "react";

export interface HeroKpi {
  valor: string;
  etiqueta: string;
  tono?: "claro" | "acento" | "peligro";
}

interface PageHeroProps {
  eyebrow?: string;
  title?: ReactNode;
  description?: ReactNode;
  kpis?: HeroKpi[];
  actions?: ReactNode;
  children?: ReactNode;
  className?: string;
}

const tonosKpi = {
  claro: "text-white",
  acento: "text-accent-soft",
  peligro: "text-danger-soft",
};

export function PageHero({
  eyebrow,
  title,
  description,
  kpis,
  actions,
  children,
  className = "",
}: PageHeroProps) {
  return (
    <header className={["bg-primary-dark text-white", className].join(" ")}>
      <div className="mx-auto w-full max-w-[1440px] px-4 sm:px-8">
        <div className="flex flex-col gap-5 py-6 sm:py-7 lg:flex-row lg:items-end lg:justify-between lg:gap-8">
          <div className="min-w-0">
            {eyebrow ? <p className="type-eyebrow text-primary-light">{eyebrow}</p> : null}
            {title ? (
              <h1 className="mt-2 text-[30px] font-bold leading-[36px] tracking-[-0.02em] sm:text-[44px] sm:leading-[48px]">
                {title}
              </h1>
            ) : null}
            {description ? (
              <p className="mt-1 max-w-3xl text-[13px] leading-5 text-[#b9d6c6] sm:text-sm">
                {description}
              </p>
            ) : null}
            {children}
          </div>

          {kpis?.length ? (
            <dl className="hidden shrink-0 items-end gap-10 lg:flex">
              {kpis.map((kpi) => (
                <div key={kpi.etiqueta}>
                  <dt
                    className={[
                      "text-[28px] font-bold leading-8 tracking-[-0.015em] tabular-nums",
                      tonosKpi[kpi.tono ?? "claro"],
                    ].join(" ")}
                  >
                    {kpi.valor}
                  </dt>
                  <dd className="mt-1 text-xs leading-4 text-[#b9d6c6]">{kpi.etiqueta}</dd>
                </div>
              ))}
            </dl>
          ) : null}

          {actions ? <div className="flex flex-wrap gap-3 lg:shrink-0">{actions}</div> : null}
        </div>
      </div>
    </header>
  );
}

interface PageBodyProps {
  children: ReactNode;
  className?: string;
}

export function PageBody({ children, className = "" }: PageBodyProps) {
  return (
    <div
      className={["mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-8 sm:py-8", className].join(" ")}
    >
      {children}
    </div>
  );
}
