import React, { forwardRef } from 'react';

export const Input = forwardRef(({
  label,
  error,
  helperText,
  icon: Icon,
  prefix,
  className = '',
  containerClassName = '',
  id,
  type = 'text',
  ...props
}, ref) => {
  const inputId = id || props.name || Math.random().toString(36).substring(2, 9);
  const hasLeading = Boolean(Icon || prefix);

  const renderLeading = () => {
    if (prefix !== undefined && prefix !== null && prefix !== '') {
      if (typeof prefix === 'string' || typeof prefix === 'number') {
        return (
          <span className="font-semibold text-xs text-wine-deep select-none">
            {prefix}
          </span>
        );
      }
      if (React.isValidElement(prefix)) {
        return prefix;
      }
      const PrefixComponent = prefix;
      return <PrefixComponent className="w-4 h-4" />;
    }

    if (!Icon) return null;

    if (React.isValidElement(Icon)) {
      return Icon;
    }

    if (typeof Icon === 'string' || typeof Icon === 'number') {
      return (
        <span className="font-bold text-xs text-ink-charcoal select-none">
          {Icon}
        </span>
      );
    }

    // Lucide icons and forwardRef components are objects with $$typeof: Symbol(react.forward_ref)
    const Component = Icon;
    return <Component className="w-4 h-4" />;
  };

  return (
    <div className={`w-full flex flex-col gap-1.5 ${containerClassName}`}>
      {label && (
        <label htmlFor={inputId} className="text-xs font-semibold tracking-wide text-ink-muted uppercase">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {hasLeading && (
          <div className="absolute left-3.5 text-ink-subtle pointer-events-none flex items-center justify-center min-w-[1rem]">
            {renderLeading()}
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
            ${hasLeading ? 'pl-10' : ''}
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
