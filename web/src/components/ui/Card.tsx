import type { ReactNode, HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padding?: string;
}

export default function Card({ children, className = '', padding, ...rest }: CardProps) {
  return (
    <div
      className={`card ${className}`}
      style={padding ? { padding } : undefined}
      {...rest}
    >
      {children}
    </div>
  );
}
