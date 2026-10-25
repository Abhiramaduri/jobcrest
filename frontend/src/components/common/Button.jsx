import React from 'react';
import { Loader2 } from 'lucide-react';

export const Button = ({
  children,
  variant = 'primary', // 'primary', 'secondary', 'outline', 'ghost', 'danger'
  size = 'md',        // 'sm', 'md', 'lg'
  isLoading = false,
  disabled = false,
  className = '',
  icon: Icon,
  type = 'button',
  onClick,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none disabled:active:scale-100 focus:outline-none focus:ring-2 focus:ring-wine-burgundy/30';

  const sizes = {
    sm: 'text-xs px-3.5 py-1.5 gap-1.5 shadow-sm',
    md: 'text-sm px-5 py-2.5 gap-2 shadow-wine-sm',
    lg: 'text-base px-6 py-3.5 gap-2.5 shadow-wine-md',
  };

  const variants = {
    primary: 'bg-wine-deep text-white hover:bg-wine-burgundy shadow-wine-sm hover:shadow-wine-md',
    secondary: 'bg-wine-tint text-wine-deep hover:bg-wine-light font-semibold',
    outline: 'border border-sand-border bg-white text-ink-charcoal hover:border-wine-burgundy hover:text-wine-deep hover:bg-sand-surface',
    ghost: 'text-ink-charcoal hover:bg-sand-border/50 hover:text-wine-deep',
    danger: 'bg-status-error text-white hover:bg-red-800 shadow-sm',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`${baseStyles} ${sizes[size]} ${variants[variant]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-current" />
      ) : Icon ? (
        <Icon className="w-4 h-4 flex-shrink-0" />
      ) : null}
      {children}
    </button>
  );
};

export default Button;
