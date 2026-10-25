import React, { useState, useEffect } from 'react';
import { Plus, X, Sparkles, Check } from 'lucide-react';
import profileApi from '../../api/profileApi';
import Button from '../common/Button';
import toast from 'react-hot-toast';

export const SkillsEditor = ({ skills = [], onRefresh }) => {
  const [allSkillsRepo, setAllSkillsRepo] = useState([]);
  const [selectedSkillId, setSelectedSkillId] = useState('');
  const [proficiency, setProficiency] = useState('intermediate');
  const [isAdding, setIsAdding] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState(null);

  useEffect(() => {
    profileApi
      .getAllSkillsRepo()
      .then((data) => setAllSkillsRepo(data || []))
      .catch((err) => console.error('Failed to load skills repo:', err));
  }, []);

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!selectedSkillId) {
      toast.error('Please select a skill');
      return;
    }

    setIsAdding(true);
    try {
      await profileApi.addSkill({
        skill: selectedSkillId,
        proficiency,
      });
      toast.success('Skill added to profile');
      setSelectedSkillId('');
      onRefresh();
    } catch (err) {
      toast.error(err?.response?.data?.non_field_errors?.[0] || 'Failed to add skill');
    } finally {
      setIsAdding(false);
    }
  };

  const handleDeleteSkill = async (skillEntryId) => {
    setIsDeletingId(skillEntryId);
    try {
      await profileApi.deleteSkill(skillEntryId);
      toast.success('Skill removed');
      onRefresh();
    } catch {
      toast.error('Failed to remove skill');
    } finally {
      setIsDeletingId(null);
    }
  };

  // Filter out skills the user already has
  const existingSkillIds = new Set(skills.map((s) => s.skill));
  const availableSkills = allSkillsRepo.filter((s) => !existingSkillIds.has(s.id));

  return (
    <div className="space-y-6">
      {/* Current Skills Tags Cloud */}
      <div className="flex flex-wrap gap-2.5">
        {skills.length === 0 ? (
          <p className="text-xs text-ink-subtle italic">
            No technical skills added yet. Add relevant competencies below.
          </p>
        ) : (
          skills.map((item) => (
            <div
              key={item.id}
              className="inline-flex items-center gap-2 bg-wine-tint border border-wine-burgundy/20 px-3 py-1.5 rounded-xl shadow-xs transition-all hover:border-wine-burgundy"
            >
              <div className="flex flex-col">
                <span className="text-xs font-bold text-wine-deep">
                  {item.skill_name || item.name}
                </span>
                {item.proficiency && (
                  <span className="text-[10px] text-ink-muted capitalize">
                    {item.proficiency}
                  </span>
                )}
              </div>
              <button
                type="button"
                onClick={() => handleDeleteSkill(item.id)}
                disabled={isDeletingId === item.id}
                className="text-wine-burgundy hover:text-status-error p-1 rounded-md hover:bg-white transition-colors"
                title="Remove skill"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Add New Skill Bar */}
      <form
        onSubmit={handleAddSkill}
        className="pt-4 border-t border-sand-border flex flex-col sm:flex-row items-center gap-3"
      >
        <div className="w-full sm:flex-1">
          <select
            value={selectedSkillId}
            onChange={(e) => setSelectedSkillId(e.target.value)}
            className="w-full bg-white border border-sand-border rounded-xl px-3.5 py-2 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
          >
            <option value="">Select skill from repository...</option>
            {availableSkills.map((sk) => (
              <option key={sk.id} value={sk.id}>
                {sk.name}
              </option>
            ))}
          </select>
        </div>

        <div className="w-full sm:w-44">
          <select
            value={proficiency}
            onChange={(e) => setProficiency(e.target.value)}
            className="w-full bg-white border border-sand-border rounded-xl px-3 py-2 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="expert">Expert / Advanced</option>
          </select>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="sm"
          isLoading={isAdding}
          icon={Plus}
          className="w-full sm:w-auto flex-shrink-0"
        >
          Add Skill
        </Button>
      </form>
    </div>
  );
};

export default SkillsEditor;
