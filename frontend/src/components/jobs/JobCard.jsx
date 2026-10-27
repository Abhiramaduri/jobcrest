import React from 'react';
import { Link } from 'react-router-dom';
import {
  MapPin,
  Briefcase,
  Bookmark,
  Calendar,
  Building2,
  Sparkles,
} from 'lucide-react';
import Badge from '../common/Badge';
import { getCurrency, formatSalaryWithCurrency } from '../../utils/currencies';

export const JobCard = ({
  job,
  isSaved = false,
  onToggleSave,
  showApplyButton = true,
}) => {
  if (!job) return null;

  const company = job.company || {};
  const currencyInfo = getCurrency(job.salary_currency);
  const SalaryIcon = currencyInfo.icon;
  const formattedSalary = formatSalaryWithCurrency(job.salary_min, job.salary_max, job.salary_currency);

  const postedDate = job.created_at
    ? new Date(job.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      })
    : null;

  return (
    <div className="group relative bg-white border border-sand-border rounded-2xl p-5 sm:p-6 transition-all duration-300 hover:border-wine-burgundy hover:shadow-wine-md hover:-translate-y-1">
      {/* Top row: Company Logo & Details + Save Bookmark */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl border border-sand-border bg-sand-canvas flex items-center justify-center overflow-hidden flex-shrink-0 group-hover:border-wine-burgundy/30 transition-colors">
            {company.logo ? (
              <img
                src={company.logo}
                alt={company.name || 'Company'}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.parentElement.innerHTML = `<span class="font-display font-bold text-wine-deep">${(company.name || 'J')[0]}</span>`;
                }}
              />
            ) : (
              <span className="font-display font-bold text-wine-deep text-lg">
                {(company.name || 'J')[0]}
              </span>
            )}
          </div>
          <div>
            <h4 className="text-xs font-semibold text-ink-muted uppercase tracking-wider">
              {company.name || 'Confidential Employer'}
            </h4>
            <Link
              to={`/jobs/${job.slug}`}
              className="font-display text-lg sm:text-xl font-bold text-wine-deep group-hover:text-wine-burgundy transition-colors line-clamp-1 mt-0.5"
            >
              {job.title}
            </Link>
          </div>
        </div>

        {/* Quick Save Bookmark */}
        {onToggleSave && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onToggleSave(job);
            }}
            className={`p-2 rounded-xl transition-all ${
              isSaved
                ? 'bg-wine-deep text-white shadow-wine-sm'
                : 'text-ink-subtle hover:text-wine-deep hover:bg-wine-tint'
            }`}
            title={isSaved ? 'Remove Bookmark' : 'Save Opportunity'}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
          </button>
        )}
      </div>

      {/* Meta Pills: Job Type, Remote, Location, Category */}
      <div className="flex flex-wrap items-center gap-2 mt-4">
        <Badge variant="default" size="sm" icon={Briefcase}>
          <span className="capitalize">{job.job_type || 'Full-time'}</span>
        </Badge>

        {job.is_remote && (
          <Badge variant="success" size="sm" icon={Sparkles}>
            Remote Available
          </Badge>
        )}

        {job.location && (
          <Badge variant="outline" size="sm" icon={MapPin}>
            {job.location}
          </Badge>
        )}

        {job.category_name && (
          <Badge variant="sand" size="sm">
            {job.category_name}
          </Badge>
        )}
      </div>

      {/* Skills Pill Cloud (if available) */}
      {job.skills_required && job.skills_required.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-sand-border/60">
          {job.skills_required.slice(0, 4).map((sk) => (
            <span
              key={sk.id || sk.name}
              className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-sand-canvas text-ink-charcoal border border-sand-border/80"
            >
              {sk.name}
            </span>
          ))}
          {job.skills_required.length > 4 && (
            <span className="text-[11px] text-ink-subtle font-medium self-center pl-1">
              +{job.skills_required.length - 4} more
            </span>
          )}
        </div>
      )}

      {/* Bottom Footer: Salary and Action */}
      <div className="flex items-center justify-between gap-2 mt-5 pt-4 border-t border-sand-border/70 text-xs">
        <div className="flex items-center gap-1.5 text-wine-deep font-bold">
          {SalaryIcon ? (
            <SalaryIcon className="w-4 h-4 text-wine-burgundy flex-shrink-0" />
          ) : (
            <span className="text-xs font-bold text-wine-burgundy">
              {currencyInfo.symbol}
            </span>
          )}
          <span>{formattedSalary}</span>
        </div>

        <div className="flex items-center gap-3">
          {postedDate && (
            <span className="text-ink-subtle flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {postedDate}
            </span>
          )}
          <Link
            to={`/jobs/${job.slug}`}
            className="font-semibold text-wine-deep hover:text-wine-burgundy hover:underline inline-flex items-center"
          >
            View Details &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
};

export default JobCard;
