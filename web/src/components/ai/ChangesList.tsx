import { Check, Diamond } from 'lucide-react';

interface ChangesListProps {
  changes: string[];
}

export default function ChangesList({ changes }: ChangesListProps) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-full bg-success/15 flex items-center justify-center">
          <Check size={12} className="text-success" />
        </div>
        <span className="text-[10px] font-bold text-success uppercase tracking-wide">Improvements Applied</span>
        <span className="badge badge-green" role="status" aria-label={`${changes.length} changes`}>
          {changes.length}
        </span>
      </div>

      <div className="flex flex-col gap-1.5">
        {changes.map((change, i) => (
          <div
            key={i}
            className="bg-surface-active border border-success/20 rounded px-2.5 py-1.5 flex gap-2 items-start animate-fade-in"
            style={{ animationDelay: `${i * 50}ms` }}
          >
            <Diamond size={10} className="text-success shrink-0 mt-0.5" />
            <span className="text-xs text-cream">{change}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
