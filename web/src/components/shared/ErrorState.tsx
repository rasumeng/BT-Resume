import { AlertTriangle } from 'lucide-react';
import Button from '../ui/Button';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex items-center justify-center h-full p-6">
      <div className="text-center">
        <AlertTriangle size={48} className="text-error mb-4 mx-auto" />
        <h2 className="text-lg font-bold text-cream mb-2">Something went wrong</h2>
        <p className="text-sm text-text-secondary mb-6">{message}</p>
        {onRetry && (
          <Button variant="primary" onClick={onRetry}>
            Retry
          </Button>
        )}
      </div>
    </div>
  );
}
