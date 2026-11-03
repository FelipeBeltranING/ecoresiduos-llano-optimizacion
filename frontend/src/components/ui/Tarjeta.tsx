import type { HTMLAttributes } from "react";

interface TarjetaProps extends HTMLAttributes<HTMLDivElement> {
  relleno?: "none" | "sm" | "md" | "lg";
}

const rellenos = {
  none: "",
  sm: "p-4",
  md: "p-5",
  lg: "p-6",
};

export function Tarjeta({ relleno = "md", className = "", children, ...props }: TarjetaProps) {
  return (
    <div
      className={[
        "rounded-card border border-border bg-surface shadow-card",
        rellenos[relleno],
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </div>
  );
}
