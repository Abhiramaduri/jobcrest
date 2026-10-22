import React from 'react';

export const Badge = ({
  children,
  variant = 'default', // 'default', 'wine', 'success', 'warning', 'error', 'outline', 'sand'
  size = 'md',        // 'sm', 'md', 'lg'
  className = '',
  icon: Icon,
}) => {
  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 gap-1 font-medium',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  };

  const variants = {
    default: 'bg-wine-tint text-wine-deep border border-wine-burgundy/15',
    wine: 'bg-wine-deep text-white shadow-wine-sm',
    burgundy: 'bg-wine-burgundy text-white',
    sand: 'bg-sand-border/40 text-ink-charcoal border border-sand-border',
    success: 'bg-emerald-50 text-emerald-800 border border-emerald-200',
    warning: 'bg-amber-50 text-amber-800 border border-amber-200',
    error: 'bg-rose-50 text-rose-800 border border-rose-200',
    info: 'bg-blue-50 text-blue-800 border border-blue-200',
    outline: 'border border-sand-border text-ink-muted bg-white',
  };

  return (
    <span className={`inline-flex items-center rounded-full tracking-wide transition-colors ${sizes[size]} ${variants[variant] || variants.default} ${className}`}>
      {Icon && <Icon className="w-3 h-3 flex-shrink-0" />}
      {children}
    </span>
  );
};

export const StatusBadge = ({ status }) => {
  const normalized = (status || '').toLowerCase().replace(/[\s-]/g, '_');

  switch (normalized) {
    case 'applied':
      return <Badge variant="info">Applied</Badge>;
    case 'under_review':
    case 'reviewing':
      return <Badge variant="warning">Under Review</Badge>;
    case 'interview_scheduled':
    case 'interview':
      return <Badge variant="default">Interview Scheduled</Badge>;
    case 'hired':
    case 'accepted':
    case 'offer':
      return <Badge variant="success">Hired</Badge>;
    case 'rejected':
      return <Badge variant="error">Rejected</Badge>;
    case 'published':
    case 'active':
      return <Badge variant="success">Published</Badge>;
    case 'draft':
      return <Badge variant="sand">Draft</Badge>;
    case 'closed':
    case 'expired':
      return <Badge variant="error">Closed</Badge>;
    default:
      return <Badge variant="sand">{status || 'Unknown'}</Badge>;
  }
};

export default Badge;
