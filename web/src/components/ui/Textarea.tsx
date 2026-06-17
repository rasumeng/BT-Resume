import { forwardRef, type TextareaHTMLAttributes } from 'react';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className = '', ...rest }, ref) => (
    <div className="field">
      {label && <label className="field-label">{label}</label>}
      <textarea
        ref={ref}
        className={`field-textarea ${error ? 'border-red-500' : ''} ${className}`}
        {...rest}
      />
      {error && <p className="field-error" role="alert">{error}</p>}
    </div>
  ),
);

Textarea.displayName = 'Textarea';

export default Textarea;
