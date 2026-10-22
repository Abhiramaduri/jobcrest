import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import {
  Briefcase,
  DollarSign,
  MapPin,
  Calendar,
  Sparkles,
  ArrowLeft,
  Save,
  Send,
  X,
  Plus,
} from 'lucide-react';
import jobsApi from '../api/jobsApi';
import profileApi from '../api/profileApi';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

export const JobPostWizard = () => {
  const navigate = useNavigate();

  const [categories, setCategories] = useState([]);
  const [allSkills, setAllSkills] = useState([]);
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: '',
      category: '',
      job_type: 'full-time',
      experience_min: 2,
      experience_max: 6,
      salary_min: '',
      salary_max: '',
      salary_currency: 'INR',
      location: '',
      is_remote: false,
      vacancies: 1,
      application_deadline: '',
      description: '',
      responsibilities: '',
      requirements: '',
      status: 'published',
    },
  });

  useEffect(() => {
    Promise.all([
      jobsApi.getCategories().catch(() => []),
      profileApi.getAllSkillsRepo().catch(() => []),
    ])
      .then(([cats, sks]) => {
        setCategories(cats || []);
        setAllSkills(sks || []);
      })
      .catch((err) => console.error('Failed to load taxonomies:', err));
  }, []);

  const handleToggleSkill = (skillId) => {
    if (selectedSkills.includes(skillId)) {
      setSelectedSkills(selectedSkills.filter((id) => id !== skillId));
    } else {
      setSelectedSkills([...selectedSkills, skillId]);
    }
  };

  const onSubmit = async (data, customStatus) => {
    setIsSubmitting(true);
    try {
      const payload = {
        title: data.title,
        category: data.category ? Number(data.category) : null,
        job_type: data.job_type,
        experience_min: Number(data.experience_min) || 0,
        experience_max: data.experience_max ? Number(data.experience_max) : null,
        salary_min: data.salary_min ? Number(data.salary_min) : null,
        salary_max: data.salary_max ? Number(data.salary_max) : null,
        salary_currency: data.salary_currency || 'INR',
        location: data.location || '',
        is_remote: Boolean(data.is_remote),
        vacancies: Number(data.vacancies) || 1,
        skills_required: selectedSkills,
        application_deadline: data.application_deadline || null,
        description: data.description,
        responsibilities: data.responsibilities,
        requirements: data.requirements || '',
        status: customStatus || data.status || 'published',
      };

      await jobsApi.createJob(payload);
      toast.success(
        customStatus === 'draft'
          ? 'Draft requisition saved successfully!'
          : 'Opportunity published live on JobCrest!'
      );
      navigate('/employer/jobs');
    } catch (err) {
      console.error('Failed to create job posting:', err);
      toast.error(
        err?.response?.data?.detail ||
        err?.response?.data?.title?.[0] ||
        'Failed to save job posting. Please check your inputs.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <Link
          to="/employer/jobs"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-ink-muted hover:text-wine-deep transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Requisitions
        </Link>
      </div>

      <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-md space-y-8">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-wine-burgundy">
            Position Publishing Wizard
          </span>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep mt-1">
            Create Job Requisition
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted mt-1">
            Author a high-impact role description to attract elite talent.
          </p>
        </div>

        <form className="space-y-6">
          {/* Title & Category */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <Input
                label="Position Title"
                placeholder="e.g. Lead Distributed Systems Architect"
                {...register('title', { required: 'Job title is required' })}
                error={errors.title?.message}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold tracking-wide text-ink-muted uppercase">
                Discipline / Category
              </label>
              <select
                {...register('category')}
                className="w-full bg-white border border-sand-border rounded-xl px-3.5 py-2.5 text-sm text-ink-charcoal focus:outline-none focus:border-wine-deep focus:ring-2 focus:ring-wine-burgundy/15"
              >
                <option value="">Select category...</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Job Type & Remote Toggle */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold tracking-wide text-ink-muted uppercase">
                Employment Type
              </label>
              <select
                {...register('job_type')}
                className="w-full bg-white border border-sand-border rounded-xl px-3.5 py-2.5 text-sm text-ink-charcoal focus:outline-none focus:border-wine-deep"
              >
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="remote">Remote</option>
                <option value="internship">Internship</option>
              </select>
            </div>

            <Input
              label="Location (City, Country)"
              placeholder="e.g. Bengaluru, India or Remote"
              icon={MapPin}
              {...register('location')}
            />

            <div className="pt-6">
              <label className="flex items-center gap-2.5 p-2.5 bg-sand-canvas/50 rounded-xl border border-sand-border cursor-pointer select-none">
                <input
                  type="checkbox"
                  {...register('is_remote')}
                  className="w-4 h-4 rounded text-wine-deep accent-wine-deep"
                />
                <span className="text-xs font-semibold text-wine-deep">
                  Remote Eligible Role
                </span>
              </label>
            </div>
          </div>

          {/* Experience and Vacancies */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Input
              label="Minimum Experience (Years)"
              type="number"
              placeholder="0"
              {...register('experience_min')}
            />
            <Input
              label="Maximum Experience (Years)"
              type="number"
              placeholder="8"
              {...register('experience_max')}
            />
            <Input
              label="Number of Open Vacancies"
              type="number"
              placeholder="1"
              {...register('vacancies')}
            />
          </div>

          {/* Salary Compensation */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Input
              label="Minimum Salary (Annual)"
              type="number"
              placeholder="e.g. 1500000"
              icon={DollarSign}
              {...register('salary_min')}
            />
            <Input
              label="Maximum Salary (Annual)"
              type="number"
              placeholder="e.g. 3000000"
              icon={DollarSign}
              {...register('salary_max')}
            />
            <div className="space-y-1.5">
              <label className="text-xs font-semibold tracking-wide text-ink-muted uppercase">
                Currency
              </label>
              <select
                {...register('salary_currency')}
                className="w-full bg-white border border-sand-border rounded-xl px-3.5 py-2.5 text-sm text-ink-charcoal focus:outline-none focus:border-wine-deep"
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>

          {/* Application Deadline */}
          <div className="sm:w-1/2">
            <Input
              label="Application Closing Date"
              type="date"
              icon={Calendar}
              {...register('application_deadline')}
            />
          </div>

          {/* Skills Required Tag Multi-Select */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted block">
              Required Technical Competencies
            </label>
            <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto p-3 bg-sand-canvas/40 border border-sand-border rounded-xl">
              {allSkills.map((sk) => {
                const isSelected = selectedSkills.includes(sk.id);
                return (
                  <button
                    key={sk.id}
                    type="button"
                    onClick={() => handleToggleSkill(sk.id)}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                      isSelected
                        ? 'bg-wine-deep text-white border-wine-deep font-semibold shadow-xs'
                        : 'bg-white text-ink-charcoal border-sand-border hover:bg-wine-tint'
                    }`}
                  >
                    {sk.name}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Role Overview */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Role Summary & Mission
            </label>
            <textarea
              rows={4}
              placeholder="Outline the mission of this position, the team context, and overall objectives..."
              {...register('description', { required: 'Role description is required' })}
              className="w-full bg-white border border-sand-border rounded-xl p-3 text-sm text-ink-charcoal focus:outline-none focus:border-wine-deep"
            />
            {errors.description && (
              <p className="text-xs text-status-error">{errors.description.message}</p>
            )}
          </div>

          {/* Responsibilities */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Core Responsibilities & Deliverables
            </label>
            <textarea
              rows={4}
              placeholder="Specify day-to-day deliverables, code ownership, sprint cadence, and cross-functional partnerships..."
              {...register('responsibilities', { required: 'Responsibilities are required' })}
              className="w-full bg-white border border-sand-border rounded-xl p-3 text-sm text-ink-charcoal focus:outline-none focus:border-wine-deep"
            />
            {errors.responsibilities && (
              <p className="text-xs text-status-error">{errors.responsibilities.message}</p>
            )}
          </div>

          {/* Requirements */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Qualifications & Must-Haves
            </label>
            <textarea
              rows={4}
              placeholder="Degree requirements, specific tech stack proficiencies, architectural patterns, or communication skills..."
              {...register('requirements')}
              className="w-full bg-white border border-sand-border rounded-xl p-3 text-sm text-ink-charcoal focus:outline-none focus:border-wine-deep"
            />
          </div>

          {/* Action CTAs */}
          <div className="flex items-center justify-end gap-3 pt-6 border-t border-sand-border">
            <Button
              type="button"
              variant="outline"
              size="md"
              icon={Save}
              isLoading={isSubmitting}
              onClick={handleSubmit((data) => onSubmit(data, 'draft'))}
            >
              Save as Draft
            </Button>
            <Button
              type="button"
              variant="primary"
              size="md"
              icon={Send}
              isLoading={isSubmitting}
              onClick={handleSubmit((data) => onSubmit(data, 'published'))}
            >
              Publish Job Live
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JobPostWizard;
