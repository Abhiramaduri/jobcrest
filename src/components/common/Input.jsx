import React, { forwardRef } from 'react';

export const Input = forwardRef(({
  label,
  error,
  helperText,
  icon: Icon,
  className = '',
  containerClassName = '',
  id,
  type = 'text',
  ...props
}, ref) => {
  const inputId = id || props.name || Math.random().toString(36).substring(2, 9);

  return (
    <div className={`w-full flex flex-col gap-1.5 ${containerClassName}`}>
      {label && (
        <label htmlFor={inputId} className="text-xs font-semibold tracking-wide text-ink-muted uppercase">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {Icon && (
          <div className="absolute left-3.5 text-ink-subtle pointer-events-none flex items-center justify-center">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          id={inputId}
          ref={ref}
          type={type}
          className={`w-full bg-white border border-sand-border rounded-xl px-4 py-2.5 text-sm text-ink-charcoal placeholder:text-ink-subtle/70
            transition-all duration-200 outline-none
            focus:border-wine-deep focus:ring-2 focus:ring-wine-burgundy/15
            disabled:bg-sand-canvas disabled:cursor-not-allowed
            ${Icon ? 'pl-10' : ''}
            ${error ? 'border-status-error focus:border-status-error focus:ring-status-error/15' : ''}
            ${className}`}
          {...props}
        />
      </div>
      {error && (
        <span className="text-xs text-status-error font-medium flex items-center gap-1">
          {error}
        </span>
      )}
      {!error && helperText && (
        <span className="text-xs text-ink-subtle">
          {helperText}
        </span>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
