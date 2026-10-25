import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Briefcase,
  Search,
  SlidersHorizontal,
  ChevronDown,
  Sparkles,
  ArrowUpDown,
  RotateCcw,
} from 'lucide-react';
import jobsApi from '../api/jobsApi';
import { useAuth } from '../context/AuthContext';
import JobCard from '../components/jobs/JobCard';
import JobFilterSidebar from '../components/jobs/JobFilterSidebar';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

export const Jobs = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated, isJobSeeker } = useAuth();

  const [jobs, setJobs] = useState([]);
  const [savedSlugs, setSavedSlugs] = useState(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  // Parse filters from searchParams
  const filters = {
    search: searchParams.get('search') || '',
    location: searchParams.get('location') || '',
    category: searchParams.get('category') || '',
    job_type: searchParams.get('job_type') || '',
    skills: searchParams.get('skills') || '',
    salary_min: searchParams.get('salary_min') || '',
    is_remote: searchParams.get('is_remote') || '',
    ordering: searchParams.get('ordering') || '-created_at',
  };

  // Fetch jobs whenever filters change
  useEffect(() => {
    const fetchJobs = async () => {
      setIsLoading(true);
      try {
        const data = await jobsApi.getJobs(filters);
        setJobs(Array.isArray(data) ? data : (data.results || []));
      } catch (err) {
        console.error('Failed to load jobs:', err);
        toast.error('Failed to load jobs');
      } finally {
        setIsLoading(false);
      }
    };
    fetchJobs();
  }, [searchParams]);

  // If seeker is logged in, fetch saved jobs to show bookmark state
  useEffect(() => {
    if (isAuthenticated && isJobSeeker) {
      jobsApi
        .getSavedJobs()
        .then((data) => {
          const list = Array.isArray(data) ? data : (data.results || []);
          const slugs = new Set(list.map((item) => item.job?.slug).filter(Boolean));
          setSavedSlugs(slugs);
        })
        .catch(() => {});
    }
  }, [isAuthenticated, isJobSeeker]);

  const updateFilters = (newFilters) => {
    const next = new URLSearchParams(searchParams);
    Object.entries(newFilters).forEach(([key, val]) => {
      if (val === '' || val === null || val === undefined) {
        next.delete(key);
      } else {
        next.set(key, val);
      }
    });
    setSearchParams(next);
  };

  const handleResetFilters = () => {
    setSearchParams(new URLSearchParams());
  };

  const handleToggleSave = async (job) => {
    if (!isAuthenticated) {
      toast.error('Please sign in as a job seeker to bookmark jobs.');
      return;
    }
    if (!isJobSeeker) {
      toast.error('Only job seekers can bookmark opportunities.');
      return;
    }

    const isSaved = savedSlugs.has(job.slug);
    try {
      if (isSaved) {
        await jobsApi.unsaveJob(job.slug);
        setSavedSlugs((prev) => {
          const next = new Set(prev);
          next.delete(job.slug);
          return next;
        });
        toast.success('Removed from saved list');
      } else {
        await jobsApi.saveJob(job.slug);
        setSavedSlugs((prev) => {
          const next = new Set(prev);
          next.add(job.slug);
          return next;
        });
        toast.success('Job saved successfully');
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update saved job');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Title & Sort Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-sand-border">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold text-wine-deep">
            Explore Opportunities
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted mt-1">
            Browse through {jobs.length} curated, high-impact career openings.
          </p>
        </div>

        {/* Sort & Mobile Filter Toggle */}
        <div className="flex items-center gap-3">
          {/* Mobile Filter Button */}
          <Button
            variant="outline"
            size="sm"
            icon={SlidersHorizontal}
            onClick={() => setMobileFilterOpen(!mobileFilterOpen)}
            className="lg:hidden"
          >
            Filters
          </Button>

          {/* Ordering Dropdown */}
          <div className="flex items-center gap-2 bg-white border border-sand-border rounded-xl px-3 py-2 text-xs text-ink-charcoal shadow-xs">
            <ArrowUpDown className="w-3.5 h-3.5 text-wine-burgundy" />
            <span className="text-ink-subtle hidden sm:inline">Sort by:</span>
            <select
              value={filters.ordering}
              onChange={(e) => updateFilters({ ordering: e.target.value })}
              className="bg-transparent font-semibold text-wine-deep focus:outline-none cursor-pointer"
            >
              <option value="-created_at">Newest First</option>
              <option value="-salary_min">Highest Compensation</option>
              <option value="-views_count">Most Popular</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid: Filters Sidebar + Job Listings */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Filter Sidebar */}
        <aside className={`lg:block ${mobileFilterOpen ? 'block' : 'hidden'}`}>
          <div className="sticky top-28">
            <JobFilterSidebar
              filters={filters}
              onFilterChange={updateFilters}
              onResetFilters={handleResetFilters}
            />
          </div>
        </aside>

        {/* Right Job Cards Column */}
        <div className="lg:col-span-3 space-y-5">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((n) => (
                <div
                  key={n}
                  className="h-44 bg-white rounded-2xl border border-sand-border p-6 skeleton"
                />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="bg-white rounded-2xl border border-sand-border p-12 text-center space-y-4">
              <Briefcase className="w-12 h-12 text-wine-burgundy/40 mx-auto" />
              <h3 className="font-display text-xl font-bold text-ink-charcoal">
                No matching opportunities found
              </h3>
              <p className="text-xs text-ink-muted max-w-md mx-auto">
                Try loosening your filters, adjusting the location or salary requirements, or clearing your search term.
              </p>
              <Button
                variant="outline"
                size="sm"
                icon={RotateCcw}
                onClick={handleResetFilters}
              >
                Clear All Filters
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <JobCard
                  key={job.id || job.slug}
                  job={job}
                  isSaved={savedSlugs.has(job.slug)}
                  onToggleSave={handleToggleSave}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Jobs;
