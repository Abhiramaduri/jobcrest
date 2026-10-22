import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Users,
  Calendar,
  PlusCircle,
  TrendingUp,
  ArrowRight,
  Eye,
  CheckCircle2,
  Clock,
  Building2,
  Video,
} from 'lucide-react';
import jobsApi from '../api/jobsApi';
import applicationsApi from '../api/applicationsApi';
import companyApi from '../api/companyApi';
import Button from '../components/common/Button';
import Badge, { StatusBadge } from '../components/common/Badge';
import ApplicantDetailModal from '../components/applications/ApplicantDetailModal';
import InterviewScheduleModal from '../components/applications/InterviewScheduleModal';
import toast from 'react-hot-toast';

export const EmployerDashboard = () => {
  const navigate = useNavigate();

  const [postings, setPostings] = useState([]);
  const [interviews, setInterviews] = useState([]);
  const [company, setCompany] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Applicant review and interview scheduling modal state
  const [selectedApplicantId, setSelectedApplicantId] = useState(null);
  const [isApplicantModalOpen, setIsApplicantModalOpen] = useState(false);
  const [interviewApplication, setInterviewApplication] = useState(null);
  const [isInterviewModalOpen, setIsInterviewModalOpen] = useState(false);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [jobsData, ivData, compData] = await Promise.all([
        jobsApi.getMyPostings().catch(() => []),
        applicationsApi.getEmployerInterviews().catch(() => []),
        companyApi.getEmployerProfile().catch(() => null),
      ]);
      setPostings(Array.isArray(jobsData) ? jobsData : (jobsData.results || []));
      setInterviews(Array.isArray(ivData) ? ivData : (ivData.results || []));
      if (compData?.company) setCompany(compData.company);
    } catch (err) {
      console.error('Failed to load employer dashboard:', err);
      toast.error('Failed to load dashboard metrics');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const activeJobs = postings.filter((j) => j.status === 'published');
  const draftJobs = postings.filter((j) => j.status === 'draft');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Welcome Banner */}
      <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-8 shadow-wine-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <Badge variant="default" size="sm">
            Recruiter Workspace
          </Badge>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep">
            Employer Command Center
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted">
            {company?.name ? `Managing requisitions for ${company.name}` : 'Post openings, review candidate portfolios, and manage interviews.'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/employer/company">
            <Button variant="outline" size="sm" icon={Building2}>
              Company Settings
            </Button>
          </Link>
          <Link to="/employer/jobs/new">
            <Button variant="primary" size="sm" icon={PlusCircle}>
              Post Opportunity
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl border border-sand-border p-6 shadow-wine-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Published Requisitions
            </p>
            <h3 className="font-display text-3xl font-bold text-wine-deep mt-1">
              {activeJobs.length}
            </h3>
            <span className="text-[11px] text-ink-subtle">
              {draftJobs.length} drafts in progress
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-wine-tint text-wine-deep flex items-center justify-center">
            <Briefcase className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-sand-border p-6 shadow-wine-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Scheduled Interviews
            </p>
            <h3 className="font-display text-3xl font-bold text-wine-deep mt-1">
              {interviews.length}
            </h3>
            <span className="text-[11px] text-emerald-700 font-medium">
              Upcoming sessions
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-wine-tint text-wine-deep flex items-center justify-center">
            <Calendar className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-sand-border p-6 shadow-wine-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Total Job Postings
            </p>
            <h3 className="font-display text-3xl font-bold text-wine-deep mt-1">
              {postings.length}
            </h3>
            <span className="text-[11px] text-wine-burgundy font-medium">
              Across all categories
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-wine-tint text-wine-deep flex items-center justify-center">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Grid: Posted Jobs Management + Upcoming Interviews */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2 cols): My Requisitions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-3xl border border-sand-border p-6 shadow-wine-sm space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-sand-border">
              <div>
                <h3 className="font-display text-lg font-bold text-wine-deep">
                  Active Requisitions & Postings
                </h3>
                <p className="text-xs text-ink-muted">
                  Overview of your posted jobs and direct applicant review
                </p>
              </div>

              <Link to="/employer/jobs" className="text-xs font-bold text-wine-deep hover:underline flex items-center gap-1">
                View all <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((n) => (
                  <div key={n} className="h-20 bg-sand-canvas/50 rounded-xl skeleton" />
                ))}
              </div>
            ) : postings.length === 0 ? (
              <div className="py-10 text-center space-y-3">
                <Briefcase className="w-10 h-10 text-wine-burgundy/40 mx-auto" />
                <h4 className="font-display font-bold text-sm text-ink-charcoal">
                  No Requisitions Created Yet
                </h4>
                <p className="text-xs text-ink-muted max-w-xs mx-auto">
                  Create your first job posting to attract high-caliber candidates.
                </p>
                <Link to="/employer/jobs/new">
                  <Button variant="primary" size="sm">
                    Post a Job Now
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-sand-border">
                {postings.slice(0, 5).map((job) => (
                  <div
                    key={job.id || job.slug}
                    className="py-3.5 flex items-center justify-between gap-4"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/jobs/${job.slug}`}
                          className="font-bold text-sm text-ink-charcoal hover:text-wine-deep transition-colors line-clamp-1"
                        >
                          {job.title}
                        </Link>
                        <StatusBadge status={job.status} />
                      </div>
                      <p className="text-xs text-ink-muted mt-0.5">
                        {job.location || 'Remote'} • {job.job_type} • Posted {new Date(job.created_at).toLocaleDateString()}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                      <Link to={`/employer/jobs`}>
                        <Button variant="outline" size="sm">
                          Manage
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Upcoming Interviews */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-sand-border p-6 shadow-wine-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-sand-border">
              <h3 className="font-display text-lg font-bold text-wine-deep">
                Interviews Agenda
              </h3>
              <Link to="/employer/interviews" className="text-xs font-bold text-wine-deep hover:underline">
                All &rarr;
              </Link>
            </div>

            {interviews.length === 0 ? (
              <p className="text-xs text-ink-muted italic py-6 text-center">
                No scheduled candidate interviews. Schedule interviews directly from the applicant portfolio view.
              </p>
            ) : (
              <div className="space-y-3">
                {interviews.slice(0, 4).map((iv) => (
                  <div
                    key={iv.id}
                    className="p-3 bg-sand-canvas/40 border border-sand-border rounded-xl space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-wine-deep capitalize">
                        {iv.mode} Interview
                      </span>
                      <span className="text-[11px] text-ink-subtle font-medium">
                        {new Date(iv.scheduled_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-xs text-ink-charcoal font-medium">
                      App #{iv.application}
                    </p>
                    {iv.meeting_link && (
                      <a
                        href={iv.meeting_link.startsWith('http') ? iv.meeting_link : `https://${iv.meeting_link}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-semibold text-wine-burgundy hover:underline inline-flex items-center gap-1"
                      >
                        <Video className="w-3.5 h-3.5" /> Meeting Link &rarr;
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Applicant Review Modal */}
      {selectedApplicantId && (
        <ApplicantDetailModal
          isOpen={isApplicantModalOpen}
          onClose={() => setIsApplicantModalOpen(false)}
          applicationId={selectedApplicantId}
          onStatusUpdated={loadDashboardData}
          onOpenScheduleInterview={(app) => {
            setInterviewApplication(app);
            setIsInterviewModalOpen(true);
          }}
        />
      )}

      {/* Interview Schedule Modal */}
      {interviewApplication && (
        <InterviewScheduleModal
          isOpen={isInterviewModalOpen}
          onClose={() => setIsInterviewModalOpen(false)}
          application={interviewApplication}
          onSuccess={loadDashboardData}
        />
      )}
    </div>
  );
};

export default EmployerDashboard;
