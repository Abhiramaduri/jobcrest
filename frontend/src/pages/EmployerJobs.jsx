import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Briefcase,
  PlusCircle,
  Users,
  Eye,
  Trash2,
  Calendar,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  Filter,
} from 'lucide-react';
import jobsApi from '../api/jobsApi';
import applicationsApi from '../api/applicationsApi';
import Button from '../components/common/Button';
import Badge, { StatusBadge } from '../components/common/Badge';
import Modal from '../components/common/Modal';
import ApplicantDetailModal from '../components/applications/ApplicantDetailModal';
import InterviewScheduleModal from '../components/applications/InterviewScheduleModal';
import { formatSalaryWithCurrency } from '../utils/currencies';
import toast from 'react-hot-toast';

export const EmployerJobs = () => {
  const [postings, setPostings] = useState([]);
  const [activeTab, setActiveTab] = useState('all'); // 'all' | 'published' | 'draft' | 'closed'
  const [isLoading, setIsLoading] = useState(true);

  // Selected job applicants review state
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobApplicants, setJobApplicants] = useState([]);
  const [isLoadingApplicants, setIsLoadingApplicants] = useState(false);
  const [isApplicantsModalOpen, setIsApplicantsModalOpen] = useState(false);

  // Individual applicant review modal
  const [reviewApplicantId, setReviewApplicantId] = useState(null);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);

  // Schedule interview modal
  const [interviewApp, setInterviewApp] = useState(null);
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);

  const loadPostings = async () => {
    setIsLoading(true);
    try {
      const data = await jobsApi.getMyPostings();
      setPostings(Array.isArray(data) ? data : (data.results || []));
    } catch (err) {
      console.error('Failed to load employer jobs:', err);
      toast.error('Failed to load job postings');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPostings();
  }, []);

  const handleStatusChange = async (slug, newStatus) => {
    try {
      await jobsApi.updateJobStatus(slug, newStatus);
      toast.success(`Job status changed to ${newStatus}`);
      loadPostings();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update status');
    }
  };

  const handleDeleteJob = async (slug) => {
    if (!window.confirm('Are you sure you want to delete this job posting? This cannot be undone.')) return;
    try {
      await jobsApi.deleteJob(slug);
      toast.success('Job posting deleted');
      loadPostings();
    } catch {
      toast.error('Failed to delete job posting');
    }
  };

  const handleViewApplicants = async (job) => {
    setSelectedJob(job);
    setIsApplicantsModalOpen(true);
    setIsLoadingApplicants(true);
    try {
      const apps = await applicationsApi.getApplicationsByJob(job.id);
      setJobApplicants(Array.isArray(apps) ? apps : (apps.results || []));
    } catch (err) {
      console.error('Failed to load applicants for job:', err);
      toast.error('Failed to load applicants');
    } finally {
      setIsLoadingApplicants(false);
    }
  };

  const filteredPostings = postings.filter((j) => {
    if (activeTab === 'all') return true;
    return j.status === activeTab;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-sand-border">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold text-wine-deep">
            Requisition Portfolio
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted mt-1">
            Manage your company's published openings, review candidate pipelines, and adjust status
          </p>
        </div>

        <Link to="/employer/jobs/new">
          <Button variant="primary" size="md" icon={PlusCircle}>
            Create New Requisition
          </Button>
        </Link>
      </div>

      {/* Tabs Filter */}
      <div className="flex items-center gap-2 border-b border-sand-border pb-3">
        {[
          { id: 'all', label: `All Requisitions (${postings.length})` },
          { id: 'published', label: `Active (${postings.filter((j) => j.status === 'published').length})` },
          { id: 'draft', label: `Drafts (${postings.filter((j) => j.status === 'draft').length})` },
          { id: 'closed', label: `Closed (${postings.filter((j) => j.status === 'closed').length})` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`text-xs font-bold px-4 py-2 rounded-xl transition-all ${
              activeTab === tab.id
                ? 'bg-wine-deep text-white shadow-wine-sm'
                : 'text-ink-muted hover:text-wine-deep hover:bg-wine-tint'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Jobs List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-32 bg-white rounded-2xl border border-sand-border skeleton" />
          ))}
        </div>
      ) : filteredPostings.length === 0 ? (
        <div className="bg-white rounded-3xl border border-sand-border p-12 text-center space-y-4 shadow-wine-sm">
          <Briefcase className="w-12 h-12 text-wine-burgundy/40 mx-auto" />
          <h3 className="font-display text-xl font-bold text-ink-charcoal">
            No Requisitions Found in this Category
          </h3>
          <p className="text-xs text-ink-muted max-w-sm mx-auto">
            Get started by authoring a new position requisition or change the active tab.
          </p>
          <Link to="/employer/jobs/new">
            <Button variant="primary" size="sm">
              Author Job Post
            </Button>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-sand-border shadow-wine-sm overflow-hidden divide-y divide-sand-border">
          {filteredPostings.map((job) => (
            <div
              key={job.id || job.slug}
              className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:bg-sand-canvas/30 transition-colors"
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2.5">
                  <StatusBadge status={job.status} />
                  <span className="text-xs font-semibold text-ink-muted capitalize">
                    {job.job_type}
                  </span>
                  {job.is_remote && (
                    <Badge variant="success" size="sm">
                      Remote
                    </Badge>
                  )}
                </div>

                <Link
                  to={`/jobs/${job.slug}`}
                  className="font-display text-xl font-bold text-wine-deep hover:text-wine-burgundy transition-colors block"
                >
                  {job.title}
                </Link>

                <div className="flex flex-wrap items-center gap-3 text-xs text-ink-muted">
                  <span>{job.location || 'Location Not Specified'}</span>
                  {(job.salary_min || job.salary_max) && (
                    <>
                      <span>•</span>
                      <span className="font-semibold text-wine-deep">
                        {formatSalaryWithCurrency(job.salary_min, job.salary_max, job.salary_currency)}
                      </span>
                    </>
                  )}
                  <span>•</span>
                  <span>
                    Created: {new Date(job.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* Status Selector & Actions */}
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-1.5 bg-sand-canvas p-1.5 rounded-xl border border-sand-border">
                  <span className="text-[11px] font-semibold text-ink-muted px-2">
                    Status:
                  </span>
                  <select
                    value={job.status}
                    onChange={(e) => handleStatusChange(job.slug, e.target.value)}
                    className="bg-white border border-sand-border rounded-lg text-xs font-semibold text-wine-deep px-2.5 py-1 focus:outline-none"
                  >
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  icon={Users}
                  onClick={() => handleViewApplicants(job)}
                >
                  Review Pipeline
                </Button>

                <button
                  onClick={() => handleDeleteJob(job.slug)}
                  className="p-2 text-ink-subtle hover:text-status-error hover:bg-rose-50 rounded-xl transition-colors"
                  title="Delete Posting"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Candidate Pipeline Modal per Job */}
      <Modal
        isOpen={isApplicantsModalOpen}
        onClose={() => setIsApplicantsModalOpen(false)}
        title={selectedJob ? `Candidate Pipeline: ${selectedJob.title}` : 'Pipeline'}
        subtitle="Manage applicants, evaluate qualifications, and schedule interviews"
        maxWidth="max-w-3xl"
      >
        {isLoadingApplicants ? (
          <div className="py-12 text-center text-sm text-ink-muted">
            Loading candidate records...
          </div>
        ) : jobApplicants.length === 0 ? (
          <div className="py-10 text-center space-y-2">
            <Users className="w-10 h-10 text-wine-burgundy/40 mx-auto" />
            <p className="text-sm font-bold text-ink-charcoal">
              No applications submitted yet for this position
            </p>
            <p className="text-xs text-ink-muted">
              As soon as candidates submit their profile and resume, they will appear here for evaluation.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-sand-border">
            {jobApplicants.map((app) => (
              <div
                key={app.id}
                className="py-3.5 flex items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-ink-charcoal">
                      {app.applicant_name}
                    </span>
                    <StatusBadge status={app.status} />
                  </div>
                  <p className="text-xs text-ink-muted mt-0.5">
                    Submitted: {new Date(app.applied_at).toLocaleString()}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setReviewApplicantId(app.id);
                      setIsReviewModalOpen(true);
                    }}
                  >
                    View Portfolio & Update
                  </Button>

                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setInterviewApp(app);
                      setIsScheduleModalOpen(true);
                    }}
                  >
                    Schedule Interview
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* Applicant Detail & Status History Modal */}
      {reviewApplicantId && (
        <ApplicantDetailModal
          isOpen={isReviewModalOpen}
          onClose={() => setIsReviewModalOpen(false)}
          applicationId={reviewApplicantId}
          onStatusUpdated={() => {
            if (selectedJob) handleViewApplicants(selectedJob);
          }}
          onOpenScheduleInterview={(app) => {
            setInterviewApp(app);
            setIsScheduleModalOpen(true);
          }}
        />
      )}

      {/* Interview Scheduler Modal */}
      {interviewApp && (
        <InterviewScheduleModal
          isOpen={isScheduleModalOpen}
          onClose={() => setIsScheduleModalOpen(false)}
          application={interviewApp}
          onSuccess={() => {
            if (selectedJob) handleViewApplicants(selectedJob);
          }}
        />
      )}
    </div>
  );
};

export default EmployerJobs;
