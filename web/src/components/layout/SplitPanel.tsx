import type { ReactNode } from 'react';

interface SplitPanelProps {
  left: ReactNode;
  right: ReactNode;
  leftWidth?: string;
}

export default function SplitPanel({ left, right, leftWidth = '40%' }: SplitPanelProps) {
  return (
    <div className="flex h-full">
      <div className="overflow-auto shrink-0" style={{ width: leftWidth, minWidth: 300 }}>
        {left}
      </div>
      <div className="w-px bg-surface-active shrink-0" />
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {right}
      </div>
    </div>
  );
}
