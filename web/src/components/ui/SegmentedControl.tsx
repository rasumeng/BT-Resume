interface SegmentedControlProps<T extends string> {
  value: T;
  options: { label: string; value: T }[];
  onChange: (value: T) => void;
  variant?: 'pill' | 'block';
  ariaLabel?: string;
}

export default function SegmentedControl<T extends string>({
  value,
  options,
  onChange,
  variant = 'block',
  ariaLabel,
}: SegmentedControlProps<T>) {
  return (
    <div
      role="radiogroup"
      aria-label={ariaLabel}
      className={`flex ${variant === 'block' ? 'gap-1' : 'gap-0.5'} bg-surface-active p-0.5 rounded-lg`}
    >
      {options.map((opt) => {
        const isActive = value === opt.value;
        return (
          <button
            key={opt.value}
            role="radio"
            aria-checked={isActive}
            className={`flex-1 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              isActive
                ? 'bg-gold text-background shadow-sm'
                : 'text-text-secondary hover:text-cream'
            }`}
            onClick={() => onChange(opt.value)}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
