import { useEffect } from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

interface NotificationToastProps {
  type: 'success' | 'error' | 'info';
  title: string;
  message: string;
  onClose: () => void;
  duration?: number;
}

const ICON_MAP = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
};

const STYLE_MAP = {
  success: 'border-success/30 bg-success/10',
  error: 'border-error/30 bg-error/10',
  info: 'border-gold/30 bg-gold/10',
};

const ICON_COLOR_MAP = {
  success: 'text-success',
  error: 'text-error',
  info: 'text-gold',
};

export default function NotificationToast({
  type,
  title,
  message,
  onClose,
  duration = 4000,
}: NotificationToastProps) {
  const Icon = ICON_MAP[type];

  useEffect(() => {
    if (duration <= 0) return;
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div
      role="alert"
      className={`fixed top-4 right-4 z-[200] border rounded-xl p-4 shadow-card min-w-[300px] max-w-[420px] animate-slide-up ${STYLE_MAP[type]}`}
    >
      <div className="flex gap-3">
        <Icon size={20} className={`shrink-0 mt-0.5 ${ICON_COLOR_MAP[type]}`} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-cream">{title}</p>
          <p className="text-xs text-text-secondary mt-0.5">{message}</p>
        </div>
        <button
          onClick={onClose}
          className="text-text-tertiary hover:text-cream shrink-0"
          aria-label="Close notification"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
