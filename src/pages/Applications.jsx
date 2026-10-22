import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Building2,
  Calendar,
  Clock,
  ArrowRight,
  Video,
  Trash2,
  AlertCircle,
  Briefcase,
} from 'lucide-react';
import applicationsApi from '../api/applicationsApi';
import { StatusBadge } from '../components/common/Badge';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

export const Applications = () => {
  const [applications, setApplications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeletingId, setIsDeletingId] = useState(null);

  const loadApplications = async () => {
    setIsLoading(true);
    try {
      const data = await applicationsApi.getMyApplications();
      setApplications(Array.isArray(data) ? data : (data.results || []));
    } catch (err) {
      console.error('Failed to load applications:', err);
      toast.error('Failed to load your applications');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadApplications();
  }, []);

  const handleWithdraw = async (appId) => {
    if (!window.confirm('Are you sure you want to withdraw this application?')) return;
    setIsDeletingId(appId);
    try {
      await applicationsApi.withdrawApplication(appId);
      toast.success('Application withdrawn successfully');
      loadApplications();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to withdraw application');
    } finally {
      setIsDeletingId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-sand-border">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold text-wine-deep">
            My Applications
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted mt-1">
            Track status updates, review stages, and interview schedules for your submissions
          </p>
        </div>

        <Link to="/jobs">
          <Button variant="primary" size="sm" icon={Briefcase}>
            Explore More Jobs
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              className="h-28 bg-white rounded-2xl border border-sand-border p-6 skeleton"
            />
          ))}
        </div>
      ) : applications.length === 0 ? (
        <div className="bg-white rounded-3xl border border-sand-border p-12 text-center space-y-4 shadow-wine-sm">
          <FileText className="w-12 h-12 text-wine-burgundy/40 mx-auto" />
          <h3 className="font-display text-xl font-bold text-ink-charcoal">
            No active job applications
          </h3>
          <p className="text-xs text-ink-muted max-w-sm mx-auto">
            You haven't submitted any applications yet. Explore openings tailored to your skills and submit with 1-click.
          </p>
          <Link to="/jobs">
            <Button variant="primary" size="sm">
              Browse Open Positions
            </Button>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-sand-border shadow-wine-sm overflow-hidden">
          <div className="divide-y divide-sand-border">
            {applications.map((app) => (
              <div
                key={app.id}
                className="p-5 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-sand-canvas/30 transition-colors"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-wine-burgundy">
                      {app.company_name || 'Employer'}
                    </span>
                    <StatusBadge status={app.status} />
                  </div>

                  <h3 className="font-display text-lg font-bold text-ink-charcoal">
                    {app.job_title}
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-ink-muted">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      Applied: {new Date(app.applied_at).toLocaleDateString()}
                    </span>

                    {app.status === 'interview_scheduled' && (
                      <Link
                        to="/interviews"
                        className="inline-flex items-center gap-1 text-wine-deep font-semibold hover:underline"
                      >
                        <Video className="w-3.5 h-3.5 text-wine-burgundy" /> View Scheduled Interview
                      </Link>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0 self-end md:self-center">
                  <button
                    onClick={() => handleWithdraw(app.id)}
                    disabled={isDeletingId === app.id}
                    className="p-2 rounded-xl text-ink-subtle hover:text-status-error hover:bg-rose-50 transition-colors"
                    title="Withdraw Application"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>

                  <Link to={`/jobs/${app.job}`}>
                    <Button variant="outline" size="sm">
                      View Job Post &rarr;
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Applications;
