interface CircularGaugeProps {
  score: number;
  size?: number;
  label?: string;
  maxScore?: number;
}

export function getScoreColor(score: number): string {
  if (score >= 85) return '#27AE60';
  if (score >= 70) return '#C9A84C';
  if (score >= 60) return '#F39C12';
  return '#E74C3C';
}

export function getScoreLabel(score: number): string {
  if (score >= 85) return 'Excellent';
  if (score >= 70) return 'Good';
  if (score >= 60) return 'Fair';
  return 'Needs Work';
}

export default function CircularGauge({ score, size = 90, label }: CircularGaugeProps) {
  const clampedScore = Math.max(0, Math.min(100, score));
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clampedScore / 100) * circumference;
  const color = getScoreColor(clampedScore);
  const displayLabel = label ?? getScoreLabel(clampedScore);

  return (
    <div
      className="flex flex-col items-center gap-1"
      role="meter"
      aria-valuenow={clampedScore}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Score: ${clampedScore} - ${displayLabel}`}
    >
      <svg width={size} height={size} viewBox="0 0 80 80">
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="#2A2A24"
          strokeWidth="6"
        />
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 40 40)"
          className="transition-all duration-1000 motion-reduce:transition-none"
        />
        <text
          x="40"
          y="38"
          textAnchor="middle"
          fill="#C9A84C"
          fontSize="20"
          fontWeight="700"
          fontFamily="'Poppins', sans-serif"
        >
          {clampedScore}
        </text>
        <text
          x="40"
          y="52"
          textAnchor="middle"
          fill="#8B8680"
          fontSize="8"
          fontFamily="'Poppins', sans-serif"
        >
          /100
        </text>
      </svg>
      <span className="text-[10px] font-bold text-gold uppercase tracking-wide">{displayLabel}</span>
    </div>
  );
}
