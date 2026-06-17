interface ProgressBarProps {
  value: number;
  maxValue?: number;
  color?: string;
  height?: 'sm' | 'md' | 'lg';
  ariaLabel?: string;
}

export default function ProgressBar({
  value,
  maxValue = 100,
  color = 'var(--color-gold)',
  height = 'md',
  ariaLabel,
}: ProgressBarProps) {
  const clampedValue = Math.max(0, Math.min(value, maxValue));
  const percent = maxValue > 0 ? (clampedValue / maxValue) * 100 : 0;
  const h = height === 'sm' ? 'h-1' : height === 'lg' ? 'h-2.5' : 'h-1.5';

  return (
    <div
      className={`w-full bg-surface-active rounded-full ${h}`}
      role="progressbar"
      aria-valuenow={clampedValue}
      aria-valuemin={0}
      aria-valuemax={maxValue}
      aria-label={ariaLabel}
    >
      <div
        className={`${h} rounded-full transition-all duration-500 motion-reduce:transition-none`}
        style={{ width: `${percent}%`, background: color }}
      />
    </div>
  );
}
