import { Loader2 } from 'lucide-react';
import type { ReactNode, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'ghost';
  icon?: ReactNode;
  loading?: boolean;
  full?: boolean;
  size?: 'sm' | 'md';
  children?: ReactNode;
}

export default function Button({
  variant = 'primary',
  icon,
  loading = false,
  full = false,
  size = 'md',
  children,
  disabled,
  className = '',
  ...rest
}: ButtonProps) {
  const variantClass = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    success: 'btn-success',
    ghost: 'btn-ghost',
  }[variant];

  return (
    <button
      className={`btn ${variantClass} ${size === 'sm' ? 'btn-sm' : ''} ${full ? 'btn-full' : ''} ${className}`}
      disabled={disabled || loading}
      aria-busy={loading}
      {...rest}
    >
      {loading ? <Loader2 size={14} className="animate-spin motion-reduce:animate-none" /> : icon}
      {children && <span>{children}</span>}
    </button>
  );
}
