import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Video,
  MapPin,
  ExternalLink,
  Users,
  Search,
} from 'lucide-react';
import applicationsApi from '../api/applicationsApi';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import toast from 'react-hot-toast';

export const EmployerInterviews = () => {
  const [interviews, setInterviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadInterviews = async () => {
    setIsLoading(true);
    try {
      const data = await applicationsApi.getEmployerInterviews();
      setInterviews(Array.isArray(data) ? data : (data.results || []));
    } catch (err) {
      console.error('Failed to load employer interviews:', err);
      toast.error('Failed to load interview agenda');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadInterviews();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="pb-6 border-b border-sand-border">
        <h1 className="font-display text-3xl sm:text-4xl font-extrabold text-wine-deep">
          Candidate Evaluation Agenda
        </h1>
        <p className="text-xs sm:text-sm text-ink-muted mt-1">
          Confirmed interview rounds across all your active requisitions
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-28 bg-white rounded-2xl border border-sand-border skeleton" />
          ))}
        </div>
      ) : interviews.length === 0 ? (
        <div className="bg-white rounded-3xl border border-sand-border p-12 text-center space-y-4 shadow-wine-sm">
          <Calendar className="w-12 h-12 text-wine-burgundy/40 mx-auto" />
          <h3 className="font-display text-xl font-bold text-ink-charcoal">
            No Interviews Scheduled Yet
          </h3>
          <p className="text-xs text-ink-muted max-w-sm mx-auto">
            Open any applicant in your candidate pipeline and click "Schedule Interview" to issue meeting invites.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {interviews.map((iv) => {
            const dateObj = new Date(iv.scheduled_at);
            const isPast = dateObj < new Date();

            return (
              <div
                key={iv.id}
                className="bg-white border border-sand-border rounded-2xl p-6 shadow-wine-sm flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-wine-burgundy/40 transition-colors"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2.5">
                    <Badge variant="default" size="sm">
                      <span className="capitalize">{iv.mode || 'Virtual'} Session</span>
                    </Badge>
                    {isPast ? (
                      <Badge variant="sand" size="sm">Concluded</Badge>
                    ) : (
                      <Badge variant="success" size="sm">Confirmed</Badge>
                    )}
                  </div>

                  <h3 className="font-display text-lg font-bold text-ink-charcoal">
                    Candidate Application #{iv.application}
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-ink-muted">
                    <span className="flex items-center gap-1 font-semibold text-wine-deep">
                      <Calendar className="w-3.5 h-3.5" />
                      {dateObj.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {dateObj.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  {iv.interview_notes && (
                    <p className="text-xs text-ink-muted bg-sand-canvas/50 p-2.5 rounded-lg border border-sand-border mt-1.5 max-w-lg">
                      <span className="font-bold text-ink-charcoal">Instructions: </span>
                      {iv.interview_notes}
                    </p>
                  )}
                </div>

                <div className="flex-shrink-0 self-end md:self-center">
                  {iv.meeting_link ? (
                    <a
                      href={iv.meeting_link.startsWith('http') ? iv.meeting_link : `https://${iv.meeting_link}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button variant="primary" size="sm" icon={ExternalLink}>
                        Join Video Call
                      </Button>
                    </a>
                  ) : (
                    <span className="text-xs text-ink-subtle italic">On-site meeting</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default EmployerInterviews;
