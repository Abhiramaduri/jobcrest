import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import {
  Building2,
  Globe,
  MapPin,
  Users,
  Calendar,
  Save,
  Plus,
  ShieldCheck,
  UserCheck,
} from 'lucide-react';
import companyApi from '../api/companyApi';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Badge from '../components/common/Badge';
import toast from 'react-hot-toast';

export const EmployerCompany = () => {
  const [profile, setProfile] = useState(null);
  const [company, setCompany] = useState(null);
  const [recruiters, setRecruiters] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Add Recruiter Modal
  const [isAddRecruiterOpen, setIsAddRecruiterOpen] = useState(false);
  const [recruiterData, setRecruiterData] = useState({
    username: '',
    designation: '',
    is_company_admin: false,
  });

  const loadData = async () => {
    setIsLoading(true);
    try {
      const empData = await companyApi.getEmployerProfile();
      setProfile(empData);
      if (empData?.company) {
        setCompany(empData.company);
        if (empData.company.slug) {
          const recs = await companyApi.getCompanyRecruiters(empData.company.slug).catch(() => []);
          setRecruiters(recs || []);
        }
      }
    } catch (err) {
      console.error('Failed to load employer company:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdateCompany = async (e) => {
    e.preventDefault();
    if (!company) return;
    setIsSaving(true);
    try {
      if (company.slug) {
        await companyApi.updateCompany(company.slug, company);
        toast.success('Company details updated successfully!');
      } else {
        const created = await companyApi.createCompany(company);
        setCompany(created);
        toast.success('Company profile initialized!');
      }
      loadData();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update company');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddRecruiter = async (e) => {
    e.preventDefault();
    if (!company?.slug) return;
    try {
      await companyApi.addRecruiter(company.slug, recruiterData);
      toast.success('Recruiter added to company');
      setIsAddRecruiterOpen(false);
      setRecruiterData({ username: '', designation: '', is_company_admin: false });
      loadData();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to add recruiter');
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 space-y-6">
        <div className="h-64 bg-white rounded-3xl border border-sand-border skeleton" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div className="pb-6 border-b border-sand-border">
        <h1 className="font-display text-3xl sm:text-4xl font-extrabold text-wine-deep">
          Company Settings & Identity
        </h1>
        <p className="text-xs sm:text-sm text-ink-muted mt-1">
          Manage your organization profile, corporate branding, and authorized recruiting teammates
        </p>
      </div>

      {/* Company Form Card */}
      <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-sm space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-sand-canvas border border-sand-border flex items-center justify-center font-display font-bold text-wine-deep text-2xl">
            {(company?.name || 'C')[0]}
          </div>
          <div>
            <h3 className="font-display text-2xl font-bold text-ink-charcoal">
              {company?.name || 'Set Up Organization Profile'}
            </h3>
            <p className="text-xs text-ink-muted">
              {company?.slug ? `jobcrest.com/companies/${company.slug}` : 'Complete organization details to display on your postings'}
            </p>
          </div>
        </div>

        <form onSubmit={handleUpdateCompany} className="space-y-4 pt-4 border-t border-sand-border">
          <Input
            label="Organization Legal Name"
            placeholder="e.g. Stripe, Razorpay, TechCorp"
            value={company?.name || ''}
            onChange={(e) => setCompany({ ...company, name: e.target.value })}
            required
          />

          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Company Mission & Culture Description
            </label>
            <textarea
              rows={4}
              placeholder="Describe your organization's mission, values, work culture, and milestones..."
              value={company?.description || ''}
              onChange={(e) => setCompany({ ...company, description: e.target.value })}
              className="w-full bg-white border border-sand-border rounded-xl p-3 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Official Website URL"
              icon={Globe}
              placeholder="https://company.com"
              value={company?.website || ''}
              onChange={(e) => setCompany({ ...company, website: e.target.value })}
            />
            <Input
              label="Industry / Domain"
              placeholder="e.g. Fintech, SaaS, Healthcare"
              value={company?.industry || ''}
              onChange={(e) => setCompany({ ...company, industry: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold tracking-wide text-ink-muted uppercase">
                Company Size
              </label>
              <select
                value={company?.company_size || '11-50'}
                onChange={(e) => setCompany({ ...company, company_size: e.target.value })}
                className="w-full bg-white border border-sand-border rounded-xl px-3.5 py-2.5 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
              >
                <option value="1-10">1-10 employees</option>
                <option value="11-50">11-50 employees</option>
                <option value="51-200">51-200 employees</option>
                <option value="201-500">201-500 employees</option>
                <option value="500+">500+ employees</option>
              </select>
            </div>

            <Input
              label="Founded Year"
              type="number"
              placeholder="2018"
              value={company?.founded_year || ''}
              onChange={(e) => setCompany({ ...company, founded_year: e.target.value })}
            />

            <Input
              label="HQ Location"
              icon={MapPin}
              placeholder="City, Country"
              value={company?.location || ''}
              onChange={(e) => setCompany({ ...company, location: e.target.value })}
            />
          </div>

          <div className="flex justify-end pt-4">
            <Button
              type="submit"
              variant="primary"
              size="md"
              icon={Save}
              isLoading={isSaving}
            >
              Save Organization Settings
            </Button>
          </div>
        </form>
      </div>

      {/* Authorized Recruiters Section */}
      {company?.slug && (
        <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-sm space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-sand-border">
            <div>
              <h3 className="font-display text-xl font-bold text-wine-deep">
                Authorized Recruiting Team
              </h3>
              <p className="text-xs text-ink-muted">
                Colleagues with access to post jobs and review candidates for {company.name}
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              icon={Plus}
              onClick={() => setIsAddRecruiterOpen(true)}
            >
              Add Recruiter
            </Button>
          </div>

          <div className="space-y-3">
            {recruiters.length === 0 ? (
              <p className="text-xs text-ink-subtle italic py-2">
                No extra recruiters added. You are the primary administrator.
              </p>
            ) : (
              recruiters.map((rec, i) => (
                <div
                  key={i}
                  className="p-3.5 bg-sand-canvas/40 border border-sand-border rounded-xl flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <UserCheck className="w-5 h-5 text-wine-deep" />
                    <div>
                      <p className="text-xs font-bold text-ink-charcoal">
                        {rec.user?.username || rec.username || 'Recruiter'}
                      </p>
                      <p className="text-[11px] text-ink-muted">
                        {rec.designation || 'Hiring Manager'}
                      </p>
                    </div>
                  </div>

                  {rec.is_company_admin && (
                    <Badge variant="default" size="sm">
                      Company Admin
                    </Badge>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Add Recruiter Modal */}
      <Modal
        isOpen={isAddRecruiterOpen}
        onClose={() => setIsAddRecruiterOpen(false)}
        title="Add Recruiter Teammate"
      >
        <form onSubmit={handleAddRecruiter} className="space-y-4">
          <Input
            label="User Identifier / Username"
            placeholder="Username of existing user"
            value={recruiterData.username}
            onChange={(e) => setRecruiterData({ ...recruiterData, username: e.target.value })}
            required
          />
          <Input
            label="Designation / Role in Company"
            placeholder="e.g. Lead Tech Recruiter, Head of People"
            value={recruiterData.designation}
            onChange={(e) => setRecruiterData({ ...recruiterData, designation: e.target.value })}
          />
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-ink-charcoal">
            <input
              type="checkbox"
              checked={recruiterData.is_company_admin}
              onChange={(e) => setRecruiterData({ ...recruiterData, is_company_admin: e.target.checked })}
              className="rounded accent-wine-deep"
            />
            Grant Company Admin Privileges
          </label>
          <div className="flex justify-end gap-2 pt-3 border-t border-sand-border">
            <Button variant="outline" size="sm" onClick={() => setIsAddRecruiterOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm">
              Confirm Addition
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default EmployerCompany;
