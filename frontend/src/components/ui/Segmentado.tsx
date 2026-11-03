interface SegmentadoItem {
  label: string;
  value: string;
}

interface SegmentadoProps {
  items: SegmentadoItem[];
  value: string;
  onChange: (value: string) => void;
  ariaLabel: string;
  className?: string;
}

export function Segmentado({
  items,
  value,
  onChange,
  ariaLabel,
  className = "",
}: SegmentadoProps) {
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className={[
        "inline-flex max-w-full overflow-x-auto rounded-control border border-border bg-surface scroll-fino",
        className,
      ].join(" ")}
    >
      {items.map((item) => {
        const isActive = item.value === value;
        return (
          <button
            key={item.value}
            type="button"
            aria-pressed={isActive}
            onClick={() => onChange(item.value)}
            className={[
              "whitespace-nowrap px-4 py-2 text-sm font-semibold leading-5 transition-colors",
              isActive ? "bg-primary text-white" : "text-text hover:bg-primary-soft",
            ].join(" ")}
          >
            {item.label}
          </button>
        );
      })}
    </div>
  );
}
