import LoadingSpinner from './LoadingSpinner';

interface OverlayProps {
  visible: boolean;
  message?: string;
}

export default function Overlay({ visible, message }: OverlayProps) {
  if (!visible) return null;

  return (
    <div
      className="overlay animate-fade-in"
      role="alert"
      aria-busy="true"
    >
      <LoadingSpinner size="lg" />
      {message && (
        <p className="text-sm text-text-secondary">{message}</p>
      )}
    </div>
  );
}
