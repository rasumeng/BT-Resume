import type { BackendStatus } from '../../types';

interface StatusBannerProps {
  status: BackendStatus;
  message: string;
}

const STATUS_CONFIG: Record<BackendStatus, { bg: string; text: string; label: string }> = {
  disconnected: { bg: 'bg-surface-active', text: 'text-text-secondary', label: 'Connecting...' },
  connecting: { bg: 'bg-surface-active', text: 'text-warning', label: 'Connecting...' },
  ready: { bg: 'bg-surface-active', text: 'text-success', label: 'Connected' },
  error: { bg: 'bg-error/10', text: 'text-error', label: 'Connection Error' },
};

export default function StatusBanner({ status, message }: StatusBannerProps) {
  if (status === 'ready') return null;

  const config = STATUS_CONFIG[status];

  return (
    <div
      role="alert"
      className={`${config.bg} px-3 py-1.5 text-[11px] font-medium ${config.text}`}
    >
      {message || config.label}
    </div>
  );
}
