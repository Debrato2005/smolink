import type { InputHTMLAttributes, ReactNode } from 'react';
import { Icon } from './Icon';
export function Field({
  label,
  hint,
  error,
  id,
  addon,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  id: string;
  label: string;
  hint?: string | undefined;
  error?: string | undefined;
  /** Control joined to the input's trailing edge, such as a submit button. */
  addon?: ReactNode;
}) {
  const input = (
    <input
      id={id}
      aria-invalid={!!error}
      aria-describedby={
        [hint ? `${id}-hint` : '', error ? `${id}-error` : '']
          .filter(Boolean)
          .join(' ') || undefined
      }
      {...props}
    />
  );
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {addon ? (
        <div className="field-joined">
          {input}
          {addon}
        </div>
      ) : (
        input
      )}
      {error && (
        <p id={`${id}-error`} className="field-error">
          <Icon name="alert" size={16} />
          {error}
        </p>
      )}
      {hint && (
        <p id={`${id}-hint`} className="field-help">
          {hint}
        </p>
      )}
    </div>
  );
}
