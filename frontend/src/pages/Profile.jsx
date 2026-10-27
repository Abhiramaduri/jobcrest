import React, { useState, useEffect } from 'react';
import {
  User,
  FileText,
  GraduationCap,
  Briefcase,
  Sparkles,
  Plus,
  Linkedin,
  Github,
  MapPin,
  Save,
  CheckCircle2,
  Calendar,
} from 'lucide-react';
import profileApi from '../api/profileApi';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import ResumeUploader from '../components/profile/ResumeUploader';
import EducationCard from '../components/profile/EducationCard';
import ExperienceCard from '../components/profile/ExperienceCard';
import SkillsEditor from '../components/profile/SkillsEditor';
import toast from 'react-hot-toast';

export const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [educations, setEducations] = useState([]);
  const [experiences, setExperiences] = useState([]);
  const [skills, setSkills] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingBasic, setIsSavingBasic] = useState(false);

  // Modals for adding Education and Experience
  const [isAddEduOpen, setIsAddEduOpen] = useState(false);
  const [isAddExpOpen, setIsAddExpOpen] = useState(false);
  const [newEdu, setNewEdu] = useState({
    degree: '',
    institution: '',
    field_of_study: '',
    start_year: '',
    end_year: '',
    is_current: false,
    grade: '',
  });
  const [newExp, setNewExp] = useState({
    company_name: '',
    role_title: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
  });

  const loadAllProfileData = async () => {
    setIsLoading(true);
    try {
      const [profData, eduData, expData, skillData] = await Promise.all([
        profileApi.getProfile(),
        profileApi.getEducation().catch(() => []),
        profileApi.getExperience().catch(() => []),
        profileApi.getSkills().catch(() => []),
      ]);
      setProfile(profData);
      setEducations(eduData || []);
      setExperiences(expData || []);
      setSkills(skillData || []);
    } catch (err) {
      console.error('Failed to load seeker profile:', err);
      toast.error('Failed to load profile data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllProfileData();
  }, []);

  // Calculate Profile Completeness Percentage
  const calculateCompleteness = () => {
    if (!profile) return 0;
    let score = 0;
    if (profile.full_name) score += 15;
    if (profile.headline) score += 15;
    if (profile.bio) score += 15;
    if (profile.resume) score += 20;
    if (profile.location) score += 5;
    if (educations.length > 0) score += 10;
    if (experiences.length > 0) score += 10;
    if (skills.length > 0) score += 10;
    return Math.min(score, 100);
  };

  const completeness = calculateCompleteness();

  const handleUpdateBasicProfile = async (e) => {
    e.preventDefault();
    setIsSavingBasic(true);
    try {
      const updated = await profileApi.updateProfile({
        full_name: profile.full_name,
        headline: profile.headline,
        bio: profile.bio,
        location: profile.location,
        experience_years: profile.experience_years || 0,
        current_ctc: profile.current_ctc || null,
        expected_ctc: profile.expected_ctc || null,
        linkedin_url: profile.linkedin_url,
        github_url: profile.github_url,
        is_open_to_work: profile.is_open_to_work,
      });
      setProfile(updated);
      toast.success('Profile details updated successfully');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsSavingBasic(false);
    }
  };

  const handleAddEducation = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        degree: newEdu.degree,
        institution: newEdu.institution,
        field_of_study: newEdu.field_of_study,
        start_year: Number(newEdu.start_year),
        end_year: newEdu.is_current ? null : (newEdu.end_year ? Number(newEdu.end_year) : null),
        is_current: Boolean(newEdu.is_current),
        grade: newEdu.grade,
      };
      await profileApi.addEducation(payload);
      toast.success('Education added');
      setIsAddEduOpen(false);
      setNewEdu({ degree: '', institution: '', field_of_study: '', start_year: '', end_year: '', is_current: false, grade: '' });
      const edus = await profileApi.getEducation();
      setEducations(edus);
    } catch {
      toast.error('Failed to add education');
    }
  };

  const handleAddExperience = async (e) => {
    e.preventDefault();
    try {
      await profileApi.addExperience(newExp);
      toast.success('Experience added');
      setIsAddExpOpen(false);
      setNewExp({ company_name: '', role_title: '', start_date: '', end_date: '', is_current: false, description: '' });
      const exps = await profileApi.getExperience();
      setExperiences(exps);
    } catch {
      toast.error('Failed to add experience');
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 space-y-6">
        <div className="h-32 bg-white rounded-2xl border border-sand-border skeleton" />
        <div className="h-96 bg-white rounded-2xl border border-sand-border skeleton" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Profile Header & Completeness Card */}
      <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl wine-gradient-bg text-white flex items-center justify-center font-display font-bold text-2xl shadow-wine-sm">
              {(profile?.full_name || 'U')[0]}
            </div>
            <div>
              <h1 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep">
                {profile?.full_name || 'Your Profile'}
              </h1>
              <p className="text-xs sm:text-sm text-ink-muted mt-0.5">
                {profile?.headline || 'No headline set yet'}
              </p>
            </div>
          </div>

          <label className="flex items-center gap-2.5 p-2.5 bg-sand-canvas rounded-xl border border-sand-border cursor-pointer select-none">
            <input
              type="checkbox"
              checked={profile?.is_open_to_work ?? true}
              onChange={(e) => setProfile({ ...profile, is_open_to_work: e.target.checked })}
              className="w-4 h-4 rounded text-wine-deep accent-wine-deep"
            />
            <span className="text-xs font-semibold text-wine-deep">
              Open to Opportunities
            </span>
          </label>
        </div>

        {/* Completeness Bar */}
        <div className="p-4 bg-sand-canvas/50 border border-sand-border rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-xs font-bold">
            <span className="text-ink-charcoal flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-wine-burgundy" /> Profile Completeness
            </span>
            <span className="text-wine-deep">{completeness}%</span>
          </div>
          <div className="w-full bg-sand-border/70 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-wine-deep h-2.5 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${completeness}%` }}
            />
          </div>
          <p className="text-[11px] text-ink-muted">
            Profiles with 80%+ completeness receive up to 4x more direct interview requests.
          </p>
        </div>
      </div>

      {/* Primary Details Form */}
      <section className="bg-white rounded-3xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-sand-border">
          <div>
            <h3 className="font-display text-xl font-bold text-wine-deep">
              Candidate Profile Information
            </h3>
            <p className="text-xs text-ink-muted mt-0.5">
              Personalized details shared with prospective hiring executives
            </p>
          </div>
        </div>

        <form onSubmit={handleUpdateBasicProfile} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Full Name"
              value={profile?.full_name || ''}
              onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
              required
            />
            <Input
              label="Professional Headline"
              placeholder="e.g. Staff Full Stack Engineer | Python & React"
              value={profile?.headline || ''}
              onChange={(e) => setProfile({ ...profile, headline: e.target.value })}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Executive Bio & Background
            </label>
            <textarea
              rows={4}
              placeholder="Highlight technical philosophy, key accomplishments, domain expertise, and leadership principles..."
              value={profile?.bio || ''}
              onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
              className="w-full bg-white border border-sand-border rounded-xl p-3 text-xs text-ink-charcoal placeholder:text-ink-subtle focus:outline-none focus:border-wine-deep"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Input
              label="Current Location"
              icon={MapPin}
              placeholder="City, Country"
              value={profile?.location || ''}
              onChange={(e) => setProfile({ ...profile, location: e.target.value })}
            />
            <Input
              label="Total Experience (Years)"
              type="number"
              placeholder="5"
              value={profile?.experience_years ?? ''}
              onChange={(e) => setProfile({ ...profile, experience_years: e.target.value })}
            />
            <Input
              label="Expected CTC (₹ / Annum)"
              type="number"
              placeholder="e.g. 2400000"
              value={profile?.expected_ctc ?? ''}
              onChange={(e) => setProfile({ ...profile, expected_ctc: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="LinkedIn Profile URL"
              icon={Linkedin}
              placeholder="https://linkedin.com/in/username"
              value={profile?.linkedin_url || ''}
              onChange={(e) => setProfile({ ...profile, linkedin_url: e.target.value })}
            />
            <Input
              label="GitHub Portfolio URL"
              icon={Github}
              placeholder="https://github.com/username"
              value={profile?.github_url || ''}
              onChange={(e) => setProfile({ ...profile, github_url: e.target.value })}
            />
          </div>

          <div className="flex justify-end pt-2">
            <Button
              type="submit"
              variant="primary"
              size="md"
              icon={Save}
              isLoading={isSavingBasic}
            >
              Save Profile Changes
            </Button>
          </div>
        </form>
      </section>

      {/* Resume Management */}
      <section className="bg-white rounded-3xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
        <div>
          <h3 className="font-display text-xl font-bold text-wine-deep">
            Resume & Portfolio Document
          </h3>
          <p className="text-xs text-ink-muted mt-0.5">
            Attach your verified PDF resume for instant 1-click job submissions
          </p>
        </div>

        <ResumeUploader
          resumeUrl={profile?.resume}
          onUploadSuccess={loadAllProfileData}
        />
      </section>

      {/* Skills Tag Cloud Section */}
      <section className="bg-white rounded-3xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
        <div>
          <h3 className="font-display text-xl font-bold text-wine-deep">
            Core Skills & Domain Expertise
          </h3>
          <p className="text-xs text-ink-muted mt-0.5">
            Add skills to receive personalized AI job recommendations matching your profile
          </p>
        </div>

        <SkillsEditor
          skills={skills}
          onRefresh={loadAllProfileData}
        />
      </section>

      {/* Work Experience Section */}
      <section className="bg-white rounded-3xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-sand-border">
          <div>
            <h3 className="font-display text-xl font-bold text-wine-deep">
              Work Experience Timeline
            </h3>
            <p className="text-xs text-ink-muted mt-0.5">
              Highlight professional roles, contributions, and leadership
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            icon={Plus}
            onClick={() => setIsAddExpOpen(true)}
          >
            Add Experience
          </Button>
        </div>

        <div className="space-y-3">
          {experiences.length === 0 ? (
            <p className="text-xs text-ink-subtle italic py-2">
              No work experience added yet. Click 'Add Experience' to showcase your career timeline.
            </p>
          ) : (
            experiences.map((exp) => (
              <ExperienceCard
                key={exp.id}
                experience={exp}
                onRefresh={loadAllProfileData}
              />
            ))
          )}
        </div>
      </section>

      {/* Education Section */}
      <section className="bg-white rounded-3xl border border-sand-border p-6 sm:p-8 shadow-wine-sm space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-sand-border">
          <div>
            <h3 className="font-display text-xl font-bold text-wine-deep">
              Education & Academics
            </h3>
            <p className="text-xs text-ink-muted mt-0.5">
              Degrees, universities, fields of study, and honors
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            icon={Plus}
            onClick={() => setIsAddEduOpen(true)}
          >
            Add Education
          </Button>
        </div>

        <div className="space-y-3">
          {educations.length === 0 ? (
            <p className="text-xs text-ink-subtle italic py-2">
              No academic records recorded. Click 'Add Education' to include your degrees.
            </p>
          ) : (
            educations.map((edu) => (
              <EducationCard
                key={edu.id}
                education={edu}
                onRefresh={loadAllProfileData}
              />
            ))
          )}
        </div>
      </section>

      {/* Add Education Modal */}
      <Modal
        isOpen={isAddEduOpen}
        onClose={() => setIsAddEduOpen(false)}
        title="Add Education Degree"
      >
        <form onSubmit={handleAddEducation} className="space-y-4">
          <Input
            label="Degree (e.g. B.Tech, M.S., MBA)"
            value={newEdu.degree}
            onChange={(e) => setNewEdu({ ...newEdu, degree: e.target.value })}
            required
          />
          <Input
            label="Institution / University"
            value={newEdu.institution}
            onChange={(e) => setNewEdu({ ...newEdu, institution: e.target.value })}
            required
          />
          <Input
            label="Field of Study"
            value={newEdu.field_of_study}
            onChange={(e) => setNewEdu({ ...newEdu, field_of_study: e.target.value })}
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Start Year"
              type="number"
              placeholder="2020"
              value={newEdu.start_year}
              onChange={(e) => setNewEdu({ ...newEdu, start_year: e.target.value })}
              required
            />
            <Input
              label="End Year (or Expected)"
              type="number"
              placeholder={newEdu.is_current ? 'Present' : '2024'}
              disabled={newEdu.is_current}
              value={newEdu.is_current ? '' : newEdu.end_year}
              onChange={(e) => setNewEdu({ ...newEdu, end_year: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-ink-charcoal select-none">
            <input
              type="checkbox"
              checked={newEdu.is_current}
              onChange={(e) => {
                const checked = e.target.checked;
                setNewEdu({
                  ...newEdu,
                  is_current: checked,
                  end_year: checked ? '' : newEdu.end_year,
                });
              }}
              className="w-4 h-4 rounded text-wine-deep accent-wine-deep cursor-pointer"
            />
            <span>Currently studying here</span>
          </label>
          <Input
            label="Grade / GPA"
            placeholder="e.g. 3.8 / 4.0 or 8.5 CGPA"
            value={newEdu.grade}
            onChange={(e) => setNewEdu({ ...newEdu, grade: e.target.value })}
          />
          <div className="flex justify-end gap-2 pt-3 border-t border-sand-border">
            <Button variant="outline" size="sm" onClick={() => setIsAddEduOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm">
              Save Education
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add Experience Modal */}
      <Modal
        isOpen={isAddExpOpen}
        onClose={() => setIsAddExpOpen(false)}
        title="Add Work Experience"
      >
        <form onSubmit={handleAddExperience} className="space-y-4">
          <Input
            label="Role Title"
            placeholder="e.g. Senior Frontend Engineer"
            value={newExp.role_title}
            onChange={(e) => setNewExp({ ...newExp, role_title: e.target.value })}
            required
          />
          <Input
            label="Company Name"
            placeholder="e.g. Stripe, Acme Corp"
            value={newExp.company_name}
            onChange={(e) => setNewExp({ ...newExp, company_name: e.target.value })}
            required
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Start Date"
              type="date"
              value={newExp.start_date}
              onChange={(e) => setNewExp({ ...newExp, start_date: e.target.value })}
              required
            />
            <Input
              label="End Date"
              type="date"
              disabled={newExp.is_current}
              value={newExp.end_date}
              onChange={(e) => setNewExp({ ...newExp, end_date: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-ink-charcoal">
            <input
              type="checkbox"
              checked={newExp.is_current}
              onChange={(e) => setNewExp({ ...newExp, is_current: e.target.checked })}
              className="rounded accent-wine-deep"
            />
            I currently work here
          </label>
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Description & Highlights
            </label>
            <textarea
              rows={4}
              placeholder="Architected micro-frontends, scaled systems, mentored juniors..."
              value={newExp.description}
              onChange={(e) => setNewExp({ ...newExp, description: e.target.value })}
              className="w-full bg-white border border-sand-border rounded-xl p-3 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
            />
          </div>
          <div className="flex justify-end gap-2 pt-3 border-t border-sand-border">
            <Button variant="outline" size="sm" onClick={() => setIsAddExpOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm">
              Save Experience
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Profile;
