import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { FileText, Upload, CheckCircle2, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import Modal from '../common/Modal';
import Button from '../common/Button';
import applicationsApi from '../../api/applicationsApi';
import profileApi from '../../api/profileApi';

export const ApplyModal = ({ isOpen, onClose, job, onApplicationSuccess }) => {
  const [profile, setProfile] = useState(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [resumeMode, setResumeMode] = useState('profile'); // 'profile' | 'new'
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      cover_letter: '',
    },
  });

  const selectedFile = watch('new_resume');

  useEffect(() => {
    if (isOpen) {
      reset();
      setIsLoadingProfile(true);
      profileApi
        .getProfile()
        .then((data) => {
          setProfile(data);
          if (!data?.resume) {
            setResumeMode('new');
          } else {
            setResumeMode('profile');
          }
        })
        .catch(() => {
          setResumeMode('new');
        })
        .finally(() => {
          setIsLoadingProfile(false);
        });
    }
  }, [isOpen, reset]);

  const onSubmit = async (data) => {
    if (!job?.id) return;
    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('job', job.id);
      formData.append('cover_letter', data.cover_letter || '');

      if (resumeMode === 'new') {
        if (!data.new_resume || data.new_resume.length === 0) {
          toast.error('Please upload a PDF resume');
          setIsSubmitting(false);
          return;
        }
        formData.append('resume', data.new_resume[0]);
      }

      await applicationsApi.applyToJob(formData);
      toast.success(`Application submitted for ${job.title}!`);
      if (onApplicationSuccess) onApplicationSuccess();
      onClose();
    } catch (err) {
      console.error('Apply error:', err);
      const detail =
        err?.response?.data?.non_field_errors?.[0] ||
        err?.response?.data?.detail ||
        err?.response?.data?.job?.[0] ||
        'Unable to submit application. Please check requirements.';
      toast.error(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!job) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Apply to ${job.title}`}
      subtitle={`Posting by ${job.company?.name || 'Company'}`}
      maxWidth="max-w-xl"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        {/* Resume Selection */}
        <div className="space-y-3">
          <label className="text-xs font-bold uppercase tracking-wider text-ink-muted block">
            Select Resume Document
          </label>

          {profile?.resume && (
            <div className="space-y-2">
              <label className="flex items-center gap-3 p-3.5 rounded-xl border border-sand-border cursor-pointer hover:border-wine-burgundy bg-sand-canvas/40 transition-colors">
                <input
                  type="radio"
                  name="resume_choice"
                  value="profile"
                  checked={resumeMode === 'profile'}
                  onChange={() => setResumeMode('profile')}
                  className="w-4 h-4 text-wine-deep accent-wine-deep"
                />
                <FileText className="w-5 h-5 text-wine-deep" />
                <div className="flex flex-col text-xs">
                  <span className="font-semibold text-ink-charcoal">
                    Use saved profile resume
                  </span>
                  <span className="text-ink-subtle">
                    Already attached to your candidate profile
                  </span>
                </div>
              </label>
            </div>
          )}

          {/* Option: Upload new resume */}
          <div>
            <label className="flex items-center gap-3 p-3.5 rounded-xl border border-sand-border cursor-pointer hover:border-wine-burgundy bg-sand-canvas/40 transition-colors">
              <input
                type="radio"
                name="resume_choice"
                value="new"
                checked={resumeMode === 'new'}
                onChange={() => setResumeMode('new')}
                className="w-4 h-4 text-wine-deep accent-wine-deep"
              />
              <Upload className="w-5 h-5 text-wine-deep" />
              <div className="flex flex-col text-xs">
                <span className="font-semibold text-ink-charcoal">
                  Upload tailored PDF resume
                </span>
                <span className="text-ink-subtle">
                  Customized specifically for this vacancy (PDF only)
                </span>
              </div>
            </label>

            {resumeMode === 'new' && (
              <div className="mt-3 pl-7">
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  {...register('new_resume', {
                    required: resumeMode === 'new' ? 'PDF resume is required' : false,
                  })}
                  className="block w-full text-xs text-ink-muted file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-wine-deep file:text-white hover:file:bg-wine-burgundy cursor-pointer"
                />
                {errors.new_resume && (
                  <p className="text-xs text-status-error mt-1">
                    {errors.new_resume.message}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Cover Letter Textarea */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold uppercase tracking-wider text-ink-muted flex items-center justify-between">
            <span>Cover Note & Introduction</span>
            <span className="text-[11px] font-normal text-ink-subtle lowercase">
              (Optional)
            </span>
          </label>
          <textarea
            rows={4}
            placeholder="Share why you are an exceptional match for this opportunity, key achievements, and availability..."
            {...register('cover_letter')}
            className="w-full bg-white border border-sand-border rounded-xl p-3 text-xs text-ink-charcoal placeholder:text-ink-subtle focus:outline-none focus:border-wine-deep focus:ring-2 focus:ring-wine-burgundy/15 transition-all resize-y"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-sand-border">
          <Button variant="outline" size="sm" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            size="sm"
            isLoading={isSubmitting}
          >
            Submit Application
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default ApplyModal;
