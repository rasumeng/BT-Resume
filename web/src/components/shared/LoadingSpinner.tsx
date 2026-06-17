import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const SIZE_MAP = { sm: 16, md: 24, lg: 32 };

export default function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
  return (
    <Loader2
      size={SIZE_MAP[size]}
      className={`animate-spin motion-reduce:animate-none text-gold ${className}`}
    />
  );
}
