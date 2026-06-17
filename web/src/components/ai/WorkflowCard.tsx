import type { ReactNode } from 'react';
import Card from '../ui/Card';

interface WorkflowCardProps {
  eyebrow: string;
  title?: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
}

export default function WorkflowCard({
  eyebrow,
  title,
  description,
  children,
  footer,
}: WorkflowCardProps) {
  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <span className="text-[11px] font-bold text-gold uppercase tracking-wide">{eyebrow}</span>
          {title && (
            <h2 className="mt-1 text-sm font-semibold text-cream">{title}</h2>
          )}
          {description && (
            <p className="mt-0.5 text-[11px] text-text-secondary">{description}</p>
          )}
        </div>
      </div>

      <div className="flex flex-col gap-3">{children}</div>

      {footer ? <div className="pt-1">{footer}</div> : null}
    </Card>
  );
}