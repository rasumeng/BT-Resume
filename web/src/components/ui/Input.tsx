import { forwardRef, type InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...rest }, ref) => (
    <div className="field">
      {label && <label className="field-label">{label}</label>}
      <input
        ref={ref}
        className={`field-input ${error ? 'border-red-500' : ''} ${className}`}
        {...rest}
      />
      {error && <p className="field-error" role="alert">{error}</p>}
    </div>
  ),
);

Input.displayName = 'Input';

export default Input;
