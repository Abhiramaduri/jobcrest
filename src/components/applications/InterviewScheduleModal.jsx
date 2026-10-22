import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Calendar, Video, MapPin, Phone, Clock, FileText } from 'lucide-react';
import Modal from '../common/Modal';
import Input from '../common/Input';
import Button from '../common/Button';
import applicationsApi from '../../api/applicationsApi';
import toast from 'react-hot-toast';

export const InterviewScheduleModal = ({
  isOpen,
  onClose,
  application,
  onSuccess,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: {
      scheduled_at: '',
      mode: 'virtual',
      meeting_link: '',
      interview_notes: '',
    },
  });

  const selectedMode = watch('mode');

  const onSubmit = async (data) => {
    if (!application?.id) return;
    setIsSubmitting(true);

    try {
      await applicationsApi.scheduleInterview({
        application: application.id,
        scheduled_at: new Date(data.scheduled_at).toISOString(),
        mode: data.mode,
        meeting_link: data.meeting_link,
        interview_notes: data.interview_notes,
      });

      toast.success('Interview successfully scheduled!');
      reset();
      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      console.error('Failed to schedule interview:', err);
      toast.error(err?.response?.data?.detail || 'Failed to schedule interview.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!application) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Schedule Interview"
      subtitle={`Candidate: ${application.applicant_name} for ${application.job_title}`}
      maxWidth="max-w-lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Date and Time */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
            Date & Time
          </label>
          <div className="relative">
            <Calendar className="w-4 h-4 absolute left-3 top-3 text-ink-subtle pointer-events-none" />
            <input
              type="datetime-local"
              {...register('scheduled_at', { required: 'Date and time is required' })}
              className="w-full bg-white border border-sand-border rounded-xl pl-9 pr-3 py-2 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
            />
          </div>
          {errors.scheduled_at && (
            <p className="text-xs text-status-error">{errors.scheduled_at.message}</p>
          )}
        </div>

        {/* Mode Selector */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
            Interview Medium
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: 'virtual', label: 'Virtual Meet', icon: Video },
              { id: 'in_person', label: 'On-site Office', icon: MapPin },
              { id: 'phone', label: 'Phone Call', icon: Phone },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <label
                  key={item.id}
                  className={`flex items-center justify-center gap-1.5 p-2.5 rounded-xl border text-xs font-semibold cursor-pointer transition-all ${
                    selectedMode === item.id
                      ? 'bg-wine-deep text-white border-wine-deep shadow-xs'
                      : 'bg-sand-canvas/40 text-ink-charcoal border-sand-border hover:bg-wine-tint'
                  }`}
                >
                  <input
                    type="radio"
                    value={item.id}
                    {...register('mode')}
                    className="hidden"
                  />
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </label>
              );
            })}
          </div>
        </div>

        {/* Meeting Link or Location Address */}
        <Input
          label={selectedMode === 'in_person' ? 'Office Location / Address' : 'Meeting URL (Google Meet / Zoom)'}
          placeholder={selectedMode === 'in_person' ? 'e.g. 5th Floor, Tower B, HQ' : 'https://meet.google.com/xyz-abc-def'}
          {...register('meeting_link', {
            required: selectedMode === 'virtual' ? 'Meeting link is required for virtual interviews' : false,
          })}
          error={errors.meeting_link?.message}
        />

        {/* Agenda and Notes */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
            Agenda / Interview Instructions
          </label>
          <textarea
            rows={3}
            placeholder="Share preparation topics, technical challenge details, or panel members..."
            {...register('interview_notes')}
            className="w-full bg-white border border-sand-border rounded-xl p-3 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-sand-border">
          <Button variant="outline" size="sm" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
            Confirm Invitation
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default InterviewScheduleModal;
