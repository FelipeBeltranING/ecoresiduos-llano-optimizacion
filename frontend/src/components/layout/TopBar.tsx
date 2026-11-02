import { Fragment } from "react";
import { Link, NavLink } from "react-router-dom";

import { allNavItems } from "@/navigation";

export function TopBar() {
  return (
    <header className="sticky top-0 z-30 bg-primary-dark">
      <div className="mx-auto flex h-16 w-full max-w-[1440px] items-center justify-between gap-4 px-4 sm:px-8 xl:h-[78px]">
        <Link
          to="/"
          className="shrink-0 text-base font-bold tracking-[-0.01em] text-white sm:text-lg"
        >
          EcoResiduos del Llano
        </Link>

        <nav
          aria-label="Navegación principal"
          className="hidden flex-1 items-center justify-center gap-1 xl:flex"
        >
          {allNavItems.map((item, index) => (
            <Fragment key={item.to}>
              {index > 0 ? (
                <span aria-hidden="true" className="h-px w-4 shrink-0 bg-white/25" />
              ) : null}
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    "flex shrink-0 items-center gap-2 whitespace-nowrap text-[13px] leading-5 transition-colors",
                    isActive ? "font-semibold text-white" : "font-normal text-white/80",
                  ].join(" ")
                }
              >
                {({ isActive }) => (
                  <>
                    <span
                      aria-hidden="true"
                      className={[
                        "size-2 rounded-full border",
                        isActive
                          ? "border-primary-light bg-primary-light"
                          : "border-white/70 bg-transparent",
                      ].join(" ")}
                    />
                    {item.label}
                  </>
                )}
              </NavLink>
            </Fragment>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-3">
          <span className="inline-flex items-center rounded-full bg-white px-2 py-1 text-xs font-medium leading-4 text-primary-dark xl:hidden">
            Red validada
          </span>
          <Link
            to="/exacto"
            className="hidden rounded-control bg-white px-4 py-2 text-sm font-semibold leading-5 text-primary-dark transition-colors hover:bg-primary-soft xl:inline-flex"
          >
            Ejecutar modelo exacto
          </Link>
        </div>
      </div>
    </header>
  );
}
