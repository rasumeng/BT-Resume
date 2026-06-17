import type { ReactNode } from 'react';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full p-6 text-center">
      {icon && (
        <div className="mb-3 text-text-tertiary">
          {icon}
        </div>
      )}
      <p className="text-sm font-semibold text-text-secondary mb-1">
        {title}
      </p>
      <p className="text-xs text-text-tertiary max-w-[200px]">
        {description}
      </p>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
