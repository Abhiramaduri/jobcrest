import React, { useState, useEffect } from 'react';
import {
  FileText,
  Calendar,
  Clock,
  CheckCircle2,
  Download,
  Send,
  User,
  History,
  Video,
} from 'lucide-react';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { StatusBadge } from '../common/Badge';
import applicationsApi from '../../api/applicationsApi';
import toast from 'react-hot-toast';

export const ApplicantDetailModal = ({
  isOpen,
  onClose,
  applicationId,
  onStatusUpdated,
  onOpenScheduleInterview,
}) => {
  const [application, setApplication] = useState(null);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newStatus, setNewStatus] = useState('');
  const [notes, setNotes] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    if (isOpen && applicationId) {
      setIsLoading(true);
      Promise.all([
        applicationsApi.getApplicationDetail(applicationId),
        applicationsApi.getApplicationHistory(applicationId).catch(() => []),
      ])
        .then(([appData, histData]) => {
          setApplication(appData);
          setNewStatus(appData.status);
          setHistory(histData);
        })
        .catch((err) => {
          toast.error('Failed to load application details');
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [isOpen, applicationId]);

  const handleStatusChange = async (e) => {
    e.preventDefault();
    if (!newStatus || newStatus === application?.status) {
      toast.error('Select a different status to update');
      return;
    }

    setIsUpdating(true);
    try {
      const updated = await applicationsApi.updateApplicationStatus(
        applicationId,
        newStatus,
        notes
      );
      setApplication(updated);
      toast.success(`Candidate status updated to ${newStatus}`);
      setNotes('');
      // Refresh history
      const histData = await applicationsApi.getApplicationHistory(applicationId);
      setHistory(histData);
      if (onStatusUpdated) onStatusUpdated();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update status');
    } finally {
      setIsUpdating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={application ? `Candidate: ${application.applicant_name}` : 'Application Details'}
      subtitle={application?.job?.title}
      maxWidth="max-w-2xl"
    >
      {isLoading ? (
        <div className="py-12 text-center text-sm text-ink-muted">
          Loading candidate portfolio...
        </div>
      ) : application ? (
        <div className="space-y-6">
          {/* Top Status & Quick Schedule Banner */}
          <div className="p-4 bg-sand-canvas/50 border border-sand-border rounded-xl flex items-center justify-between gap-4">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-ink-muted">
                Current Pipeline Status
              </p>
              <div className="mt-1">
                <StatusBadge status={application.status} />
              </div>
            </div>

            <Button
              variant="primary"
              size="sm"
              icon={Video}
              onClick={() => {
                onClose();
                if (onOpenScheduleInterview) onOpenScheduleInterview(application);
              }}
            >
              Schedule Interview
            </Button>
          </div>

          {/* Attached Resume */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Submitted Resume
            </h4>
            {application.resume ? (
              <div className="flex items-center justify-between p-3.5 bg-white border border-sand-border rounded-xl">
                <div className="flex items-center gap-2.5">
                  <FileText className="w-5 h-5 text-wine-deep" />
                  <span className="text-xs font-semibold text-ink-charcoal">
                    Candidate Resume (PDF)
                  </span>
                </div>
                <a
                  href={application.resume}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-sand-border text-xs font-semibold text-wine-deep hover:bg-wine-tint transition-colors"
                >
                  <Download className="w-3.5 h-3.5" /> Download / View PDF
                </a>
              </div>
            ) : (
              <p className="text-xs text-ink-subtle italic">No separate resume PDF uploaded.</p>
            )}
          </div>

          {/* Cover Letter */}
          {application.cover_letter && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-ink-muted">
                Cover Note
              </h4>
              <div className="p-3.5 bg-white border border-sand-border rounded-xl text-xs text-ink-charcoal leading-relaxed whitespace-pre-line">
                {application.cover_letter}
              </div>
            </div>
          )}

          {/* Status Update Form */}
          <form onSubmit={handleStatusChange} className="p-4 bg-wine-tint/30 border border-wine-burgundy/20 rounded-xl space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-wine-deep">
              Update Candidate Status
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-semibold text-ink-muted block mb-1">
                  Change Pipeline Stage
                </label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full bg-white border border-sand-border rounded-xl px-3 py-2 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
                >
                  <option value="applied">Applied</option>
                  <option value="under_review">Under Review</option>
                  <option value="interview_scheduled">Interview Scheduled</option>
                  <option value="hired">Hired / Offer Extended</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-ink-muted block mb-1">
                  Evaluation Note (Internal / Candidate Log)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Cleared technical screening..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full bg-white border border-sand-border rounded-xl px-3 py-2 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={isUpdating}
                disabled={newStatus === application.status}
              >
                Update Status
              </Button>
            </div>
          </form>

          {/* Status Timeline History */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-ink-muted flex items-center gap-1.5">
              <History className="w-3.5 h-3.5 text-wine-burgundy" />
              Application Audit Timeline
            </h4>
            {history.length === 0 ? (
              <p className="text-xs text-ink-subtle">No stage changes recorded yet.</p>
            ) : (
              <div className="space-y-2 border-l-2 border-sand-border ml-2 pl-3">
                {history.map((item) => (
                  <div key={item.id} className="relative text-xs">
                    <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-wine-deep" />
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-wine-deep capitalize">
                        {item.new_status?.replace('_', ' ')}
                      </span>
                      <span className="text-[11px] text-ink-subtle">
                        by {item.changed_by_username || 'System'} • {new Date(item.changed_at).toLocaleString()}
                      </span>
                    </div>
                    {item.notes && (
                      <p className="text-ink-muted text-[11px] mt-0.5">{item.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </Modal>
  );
};

export default ApplicantDetailModal;
