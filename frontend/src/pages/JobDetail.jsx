import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  MapPin,
  Briefcase,
  Calendar,
  Building2,
  Globe,
  Users,
  Eye,
  Bookmark,
  Sparkles,
  ArrowLeft,
  CheckCircle2,
  Share2,
} from 'lucide-react';
import jobsApi from '../api/jobsApi';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import ApplyModal from '../components/jobs/ApplyModal';
import { getCurrency, formatSalaryWithCurrency } from '../utils/currencies';
import toast from 'react-hot-toast';

export const JobDetail = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isJobSeeker } = useAuth();

  const [job, setJob] = useState(null);
  const [recommendedJobs, setRecommendedJobs] = useState([]);
  const [isSaved, setIsSaved] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);

  useEffect(() => {
    const fetchJob = async () => {
      setIsLoading(true);
      try {
        const jobData = await jobsApi.getJobDetail(slug);
        setJob(jobData);

        // Fetch similar / recommended jobs
        const allJobs = await jobsApi.getJobs({ category: jobData.category?.id || '' }).catch(() => []);
        const list = Array.isArray(allJobs) ? allJobs : (allJobs.results || []);
        setRecommendedJobs(list.filter((j) => j.slug !== slug).slice(0, 3));
      } catch (err) {
        console.error('Failed to load job detail:', err);
        toast.error('Job opportunity not found');
      } finally {
        setIsLoading(false);
      }
    };
    fetchJob();
  }, [slug]);

  // Check saved state
  useEffect(() => {
    if (isAuthenticated && isJobSeeker && job?.slug) {
      jobsApi
        .getSavedJobs()
        .then((data) => {
          const list = Array.isArray(data) ? data : (data.results || []);
          const hasSaved = list.some((item) => item.job?.slug === job.slug);
          setIsSaved(hasSaved);
        })
        .catch(() => {});
    }
  }, [isAuthenticated, isJobSeeker, job]);

  const handleToggleSave = async () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to save opportunities');
      return;
    }
    if (!isJobSeeker) {
      toast.error('Only job seekers can bookmark opportunities');
      return;
    }

    try {
      if (isSaved) {
        await jobsApi.unsaveJob(job.slug);
        setIsSaved(false);
        toast.success('Removed from saved list');
      } else {
        await jobsApi.saveJob(job.slug);
        setIsSaved(true);
        toast.success('Job saved to your bookmarks');
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Action failed');
    }
  };

  const handleApplyClick = () => {
    if (!isAuthenticated) {
      navigate(`/login?redirect=/jobs/${slug}`);
      return;
    }
    if (!isJobSeeker) {
      toast.error('Employers cannot apply for jobs. Please use a Job Seeker account.');
      return;
    }
    setIsApplyModalOpen(true);
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Link copied to clipboard!');
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="h-64 bg-white rounded-2xl border border-sand-border skeleton mb-8" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 h-96 bg-white rounded-2xl border border-sand-border skeleton" />
          <div className="h-96 bg-white rounded-2xl border border-sand-border skeleton" />
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-4">
        <Briefcase className="w-12 h-12 text-wine-burgundy/40 mx-auto" />
        <h2 className="font-display text-2xl font-bold text-wine-deep">Job Posting Not Found</h2>
        <p className="text-xs text-ink-muted">The vacancy you are searching for might have expired or been removed.</p>
        <Button variant="primary" size="sm" onClick={() => navigate('/jobs')}>
          Back to All Jobs
        </Button>
      </div>
    );
  }

  const company = job.company || {};
  const currencyInfo = getCurrency(job.salary_currency);
  const formattedSalary = formatSalaryWithCurrency(job.salary_min, job.salary_max, job.salary_currency);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Back Link */}
      <Link
        to="/jobs"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-ink-muted hover:text-wine-deep transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Search Results
      </Link>

      {/* Main Job Hero Header Card */}
      <div className="bg-white border border-sand-border rounded-3xl p-6 sm:p-8 shadow-wine-md relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start sm:items-center gap-5">
            <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl border border-sand-border bg-sand-canvas flex items-center justify-center overflow-hidden flex-shrink-0 shadow-xs">
              {company.logo ? (
                <img
                  src={company.logo}
                  alt={company.name || 'Company'}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.parentElement.innerHTML = `<span class="font-display font-bold text-wine-deep text-2xl">${(company.name || 'J')[0]}</span>`;
                  }}
                />
              ) : (
                <span className="font-display font-bold text-wine-deep text-2xl">
                  {(company.name || 'J')[0]}
                </span>
              )}
            </div>

            <div className="space-y-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-wine-burgundy">
                {company.name || 'Confidential Employer'}
              </span>
              <h1 className="font-display text-2xl sm:text-3xl lg:text-4xl font-extrabold text-wine-deep">
                {job.title}
              </h1>
              <div className="flex flex-wrap items-center gap-3 text-xs text-ink-muted pt-1">
                {job.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-wine-burgundy" /> {job.location}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5 text-wine-burgundy" /> <span className="capitalize">{job.job_type || 'Full-time'}</span>
                </span>
                {job.is_remote && (
                  <Badge variant="success" size="sm" icon={Sparkles}>
                    Remote
                  </Badge>
                )}
                {job.views_count !== undefined && (
                  <span className="flex items-center gap-1 text-ink-subtle">
                    <Eye className="w-3.5 h-3.5" /> {job.views_count} views
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <button
              onClick={handleShare}
              className="p-3 rounded-xl border border-sand-border text-ink-muted hover:text-wine-deep hover:bg-wine-tint transition-all"
              title="Share Link"
            >
              <Share2 className="w-4 h-4" />
            </button>
            <button
              onClick={handleToggleSave}
              className={`p-3 rounded-xl border transition-all ${
                isSaved
                  ? 'bg-wine-deep text-white border-wine-deep shadow-wine-sm'
                  : 'border-sand-border text-ink-muted hover:text-wine-deep hover:bg-wine-tint'
              }`}
              title={isSaved ? 'Bookmarked' : 'Save Opportunity'}
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
            </button>
            <Button
              variant="primary"
              size="lg"
              onClick={handleApplyClick}
              className="shadow-wine-md text-sm sm:text-base px-7"
            >
              Apply Now
            </Button>
          </div>
        </div>
      </div>

      {/* Grid: Details & Requirements on Left, Company & Sidebar on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Job Description, Responsibilities, Requirements */}
        <div className="lg:col-span-2 space-y-8">
          {/* Overview & Description */}
          <section className="bg-white rounded-2xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
            <h3 className="font-display text-xl font-bold text-wine-deep">
              Role Overview
            </h3>
            <div className="text-sm text-ink-charcoal leading-relaxed whitespace-pre-line font-normal">
              {job.description}
            </div>
          </section>

          {/* Responsibilities */}
          {job.responsibilities && (
            <section className="bg-white rounded-2xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
              <h3 className="font-display text-xl font-bold text-wine-deep">
                Key Responsibilities & Deliverables
              </h3>
              <div className="text-sm text-ink-charcoal leading-relaxed whitespace-pre-line font-normal">
                {job.responsibilities}
              </div>
            </section>
          )}

          {/* Requirements */}
          {job.requirements && (
            <section className="bg-white rounded-2xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
              <h3 className="font-display text-xl font-bold text-wine-deep">
                Experience & Qualifications
              </h3>
              <div className="text-sm text-ink-charcoal leading-relaxed whitespace-pre-line font-normal">
                {job.requirements}
              </div>
            </section>
          )}

          {/* Required Skills Cloud */}
          {job.skills_required && job.skills_required.length > 0 && (
            <section className="bg-white rounded-2xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
              <h3 className="font-display text-xl font-bold text-wine-deep">
                Target Competencies & Tech Stack
              </h3>
              <div className="flex flex-wrap gap-2">
                {job.skills_required.map((sk) => (
                  <Badge key={sk.id || sk.name} variant="default" size="md">
                    {sk.name}
                  </Badge>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Right Column: Key Facts Card & Company Card & Recommendations */}
        <div className="space-y-6">
          {/* Quick Facts Card */}
          <div className="bg-white rounded-2xl border border-sand-border p-6 shadow-wine-sm space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-wine-deep">
              Opportunity Breakdown
            </h4>

            <div className="space-y-3.5 text-xs divide-y divide-sand-border/60">
              <div className="pt-2 flex items-center justify-between">
                <span className="text-ink-muted">Compensation</span>
                <div className="flex items-center gap-1.5 font-bold text-wine-deep">
                  <span>{formattedSalary}</span>
                  {job.salary_currency && (
                    <span className="text-[10px] font-semibold text-wine-burgundy bg-wine-tint px-1.5 py-0.5 rounded border border-wine-burgundy/15">
                      {currencyInfo.code}
                    </span>
                  )}
                </div>
              </div>
              <div className="pt-3.5 flex items-center justify-between">
                <span className="text-ink-muted">Employment Type</span>
                <span className="font-semibold text-ink-charcoal capitalize">{job.job_type}</span>
              </div>
              <div className="pt-3.5 flex items-center justify-between">
                <span className="text-ink-muted">Experience Required</span>
                <span className="font-semibold text-ink-charcoal">
                  {job.experience_min} {job.experience_max ? `- ${job.experience_max} yrs` : '+ yrs'}
                </span>
              </div>
              <div className="pt-3.5 flex items-center justify-between">
                <span className="text-ink-muted">Open Vacancies</span>
                <span className="font-semibold text-ink-charcoal">{job.vacancies || 1}</span>
              </div>
              {job.application_deadline && (
                <div className="pt-3.5 flex items-center justify-between">
                  <span className="text-ink-muted">Application Deadline</span>
                  <span className="font-semibold text-wine-burgundy">{job.application_deadline}</span>
                </div>
              )}
            </div>

            <Button
              variant="primary"
              size="md"
              onClick={handleApplyClick}
              className="w-full mt-2"
            >
              Apply to Opportunity
            </Button>
          </div>

          {/* Company Profile Card */}
          {company && (
            <div className="bg-white rounded-2xl border border-sand-border p-6 shadow-wine-sm space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-wine-deep">
                About the Organization
              </h4>

              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-sand-canvas border border-sand-border flex items-center justify-center font-display font-bold text-wine-deep text-lg">
                  {(company.name || 'C')[0]}
                </div>
                <div>
                  <h5 className="font-bold text-sm text-ink-charcoal">
                    {company.name}
                  </h5>
                  {company.industry && (
                    <p className="text-xs text-ink-muted">{company.industry}</p>
                  )}
                </div>
              </div>

              {company.description && (
                <p className="text-xs text-ink-muted leading-relaxed line-clamp-4">
                  {company.description}
                </p>
              )}

              <div className="space-y-2 text-xs text-ink-muted pt-2 border-t border-sand-border">
                {company.company_size && (
                  <div className="flex items-center gap-2">
                    <Users className="w-3.5 h-3.5 text-wine-burgundy" />
                    <span>{company.company_size} employees</span>
                  </div>
                )}
                {company.website && (
                  <div className="flex items-center gap-2">
                    <Globe className="w-3.5 h-3.5 text-wine-burgundy" />
                    <a
                      href={company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-wine-deep hover:underline truncate"
                    >
                      {company.website}
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Similar Recommended Jobs */}
          {recommendedJobs.length > 0 && (
            <div className="bg-white rounded-2xl border border-sand-border p-6 shadow-wine-sm space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-wine-deep">
                Similar Openings
              </h4>
              <div className="space-y-3">
                {recommendedJobs.map((recJob) => (
                  <Link
                    key={recJob.id || recJob.slug}
                    to={`/jobs/${recJob.slug}`}
                    className="block p-3 rounded-xl border border-sand-border hover:border-wine-burgundy hover:bg-wine-tint/30 transition-all"
                  >
                    <h6 className="font-bold text-xs text-wine-deep hover:text-wine-burgundy line-clamp-1">
                      {recJob.title}
                    </h6>
                    <p className="text-[11px] text-ink-muted mt-0.5">
                      {recJob.company?.name} • {recJob.location || 'Remote'}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Apply Modal */}
      <ApplyModal
        isOpen={isApplyModalOpen}
        onClose={() => setIsApplyModalOpen(false)}
        job={job}
        onApplicationSuccess={() => {
          navigate('/applications');
        }}
      />
    </div>
  );
};

export default JobDetail;
