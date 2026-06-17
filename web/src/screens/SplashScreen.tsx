import type { BackendStatus } from '../types';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import Button from '../components/ui/Button';

interface SplashScreenProps {
  status: BackendStatus;
  message: string;
  onRetry: () => void;
}

export default function SplashScreen({ status, message, onRetry }: SplashScreenProps) {
  return (
    <div className="h-full flex flex-col items-center justify-center gap-6 p-6">
      {/* Logo */}
      <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-gold to-gold-light flex items-center justify-center text-3xl font-bold text-background animate-pulse motion-reduce:animate-none">
        B
      </div>

      <div className="text-center">
        <h1 className="text-xl font-bold text-cream mb-1">Beyond The Resume</h1>
        <p className="text-sm text-text-secondary">AI-Powered Resume Builder</p>
      </div>

      {status !== 'ready' && (
        <div className="flex flex-col items-center gap-3">
          <LoadingSpinner size="md" />
          <p className="text-xs text-text-tertiary">
            {status === 'error' ? 'Could not connect to backend' : message || 'Connecting to backend...'}
          </p>
          {status === 'error' && (
            <Button variant="primary" size="sm" onClick={onRetry}>
              Retry
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
