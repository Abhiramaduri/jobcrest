import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Building2,
  Globe,
  MapPin,
  Users,
  Search,
  ExternalLink,
  Briefcase,
} from 'lucide-react';
import companyApi from '../api/companyApi';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';

export const Companies = () => {
  const [companies, setCompanies] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    companyApi
      .getCompanies()
      .then((data) => {
        setCompanies(Array.isArray(data) ? data : (data.results || []));
      })
      .catch((err) => console.error('Failed to load companies:', err))
      .finally(() => setIsLoading(false));
  }, []);

  const filteredCompanies = companies.filter((c) =>
    (c.name || '').toLowerCase().includes(search.toLowerCase()) ||
    (c.industry || '').toLowerCase().includes(search.toLowerCase()) ||
    (c.location || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-sand-border">
        <div>
          <Badge variant="default" size="sm">
            Verified Directory
          </Badge>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold text-wine-deep mt-1">
            Featured Companies Hiring
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted mt-1">
            Discover premier tech giants, high-growth startups, and visionary studios
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 absolute left-3 top-3 text-ink-subtle pointer-events-none" />
          <input
            type="text"
            placeholder="Search by company or industry..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white border border-sand-border rounded-xl pl-9 pr-3 py-2 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep shadow-xs"
          />
        </div>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="h-56 bg-white rounded-2xl border border-sand-border skeleton" />
          ))}
        </div>
      ) : filteredCompanies.length === 0 ? (
        <div className="bg-white rounded-3xl border border-sand-border p-12 text-center space-y-3 shadow-wine-sm">
          <Building2 className="w-10 h-10 text-wine-burgundy/40 mx-auto" />
          <h3 className="font-display text-lg font-bold text-ink-charcoal">
            No Companies Found
          </h3>
          <p className="text-xs text-ink-muted">
            Try adjusting your search query or check back soon as more employers join JobCrest.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCompanies.map((c) => (
            <div
              key={c.id || c.slug}
              className="bg-white rounded-2xl border border-sand-border p-6 shadow-wine-sm hover:border-wine-burgundy hover:shadow-wine-md hover:-translate-y-1 transition-all flex flex-col justify-between h-64"
            >
              <div className="space-y-3">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-xl bg-sand-canvas border border-sand-border flex items-center justify-center font-display font-bold text-wine-deep text-lg flex-shrink-0">
                    {c.logo ? (
                      <img src={c.logo} alt={c.name} className="w-full h-full object-cover rounded-xl" />
                    ) : (
                      (c.name || 'C')[0]
                    )}
                  </div>
                  <div>
                    <h3 className="font-display text-lg font-bold text-ink-charcoal line-clamp-1">
                      {c.name}
                    </h3>
                    <p className="text-xs text-wine-burgundy font-semibold">
                      {c.industry || 'Technology'}
                    </p>
                  </div>
                </div>

                {c.description && (
                  <p className="text-xs text-ink-muted leading-relaxed line-clamp-3">
                    {c.description}
                  </p>
                )}
              </div>

              <div className="pt-4 border-t border-sand-border/70 flex items-center justify-between text-xs text-ink-subtle">
                <div className="flex items-center gap-3">
                  {c.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5" /> {c.location}
                    </span>
                  )}
                  {c.company_size && (
                    <span className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" /> {c.company_size}
                    </span>
                  )}
                </div>

                <Link
                  to={`/jobs?search=${encodeURIComponent(c.name)}`}
                  className="font-bold text-wine-deep hover:text-wine-burgundy hover:underline flex items-center gap-0.5"
                >
                  Jobs &rarr;
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Companies;
