import React, { useState, useEffect } from 'react';
import { Filter, RotateCcw, Search, MapPin, Briefcase, DollarSign, Check, X } from 'lucide-react';
import jobsApi from '../../api/jobsApi';
import Button from '../common/Button';

export const JobFilterSidebar = ({ filters = {}, onFilterChange, onResetFilters }) => {
  const [categories, setCategories] = useState([]);
  const [allSkills, setAllSkills] = useState([]);
  const [skillInput, setSkillInput] = useState('');

  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const [cats, sks] = await Promise.all([
          jobsApi.getCategories().catch(() => []),
          jobsApi.getSkills().catch(() => []),
        ]);
        setCategories(cats);
        setAllSkills(sks);
      } catch (err) {
        console.error('Failed to load filter metadata:', err);
      }
    };
    loadMetadata();
  }, []);

  const selectedSkills = filters.skills
    ? filters.skills.split(',').filter(Boolean)
    : [];

  const handleToggleSkill = (skillName) => {
    let next;
    if (selectedSkills.includes(skillName)) {
      next = selectedSkills.filter((s) => s !== skillName);
    } else {
      next = [...selectedSkills, skillName];
    }
    onFilterChange({ skills: next.join(',') });
  };

  const handleJobTypeChange = (type) => {
    onFilterChange({ job_type: filters.job_type === type ? '' : type });
  };

  return (
    <div className="bg-white rounded-2xl border border-sand-border p-5 sm:p-6 shadow-wine-sm space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-sand-border">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-wine-deep" />
          <h3 className="font-display text-lg font-bold text-wine-deep">
            Filter Opportunities
          </h3>
        </div>
        <button
          type="button"
          onClick={onResetFilters}
          className="text-xs font-semibold text-ink-muted hover:text-wine-deep flex items-center gap-1 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" /> Reset
        </button>
      </div>

      {/* Keyword Search */}
      <div className="space-y-2">
        <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
          Keyword Search
        </label>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-ink-subtle pointer-events-none" />
          <input
            type="text"
            placeholder="Job title, keywords, or role..."
            value={filters.search || ''}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            className="w-full bg-sand-canvas/50 border border-sand-border rounded-xl pl-9 pr-3 py-2 text-xs text-ink-charcoal placeholder:text-ink-subtle focus:outline-none focus:border-wine-deep focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Location Filter */}
      <div className="space-y-2">
        <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
          Location
        </label>
        <div className="relative">
          <MapPin className="w-4 h-4 absolute left-3 top-3 text-ink-subtle pointer-events-none" />
          <input
            type="text"
            placeholder="City, region, or country..."
            value={filters.location || ''}
            onChange={(e) => onFilterChange({ location: e.target.value })}
            className="w-full bg-sand-canvas/50 border border-sand-border rounded-xl pl-9 pr-3 py-2 text-xs text-ink-charcoal placeholder:text-ink-subtle focus:outline-none focus:border-wine-deep focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Remote Only Toggle */}
      <div className="pt-2">
        <label className="flex items-center gap-3 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={filters.is_remote === 'true' || filters.is_remote === true}
            onChange={(e) => onFilterChange({ is_remote: e.target.checked ? 'true' : '' })}
            className="w-4 h-4 rounded text-wine-deep focus:ring-wine-burgundy/30 accent-wine-deep"
          />
          <span className="text-xs font-semibold text-ink-charcoal">
            Remote Only Positions
          </span>
        </label>
      </div>

      {/* Job Type Pills */}
      <div className="space-y-2.5">
        <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
          Employment Type
        </label>
        <div className="flex flex-wrap gap-1.5">
          {[
            { id: 'full-time', label: 'Full-time' },
            { id: 'part-time', label: 'Part-time' },
            { id: 'contract', label: 'Contract' },
            { id: 'remote', label: 'Remote' },
            { id: 'internship', label: 'Internship' },
          ].map((item) => {
            const isSelected = filters.job_type === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleJobTypeChange(item.id)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                  isSelected
                    ? 'bg-wine-deep text-white border-wine-deep font-semibold shadow-xs'
                    : 'bg-sand-canvas/50 text-ink-charcoal border-sand-border hover:border-wine-burgundy hover:bg-wine-tint/40'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Category Dropdown */}
      <div className="space-y-2">
        <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
          Specialization / Category
        </label>
        <select
          value={filters.category || ''}
          onChange={(e) => onFilterChange({ category: e.target.value })}
          className="w-full bg-sand-canvas/50 border border-sand-border rounded-xl px-3 py-2 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep focus:bg-white"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      {/* Minimum Salary Filter */}
      <div className="space-y-2">
        <label className="text-xs font-bold uppercase tracking-wider text-ink-muted flex items-center justify-between">
          <span>Minimum Salary</span>
          {filters.salary_min && (
            <span className="text-wine-deep font-semibold">₹ {Number(filters.salary_min).toLocaleString()}</span>
          )}
        </label>
        <div className="relative">
          <DollarSign className="w-4 h-4 absolute left-3 top-3 text-ink-subtle pointer-events-none" />
          <input
            type="number"
            placeholder="e.g. 500000"
            value={filters.salary_min || ''}
            onChange={(e) => onFilterChange({ salary_min: e.target.value })}
            className="w-full bg-sand-canvas/50 border border-sand-border rounded-xl pl-9 pr-3 py-2 text-xs text-ink-charcoal placeholder:text-ink-subtle focus:outline-none focus:border-wine-deep focus:bg-white"
          />
        </div>
      </div>

      {/* Skills Multi-select Cloud */}
      <div className="space-y-2">
        <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
          Required Skills
        </label>

        {/* Selected skills pills */}
        {selectedSkills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-2">
            {selectedSkills.map((sk) => (
              <span
                key={sk}
                className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-wine-deep text-white shadow-xs"
              >
                {sk}
                <X
                  className="w-3 h-3 cursor-pointer hover:text-sand-muted"
                  onClick={() => handleToggleSkill(sk)}
                />
              </span>
            ))}
          </div>
        )}

        {/* Quick select from available skills */}
        <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto pt-1">
          {allSkills.slice(0, 15).map((sk) => {
            const isSelected = selectedSkills.includes(sk.name);
            return (
              <button
                key={sk.id || sk.name}
                type="button"
                onClick={() => handleToggleSkill(sk.name)}
                className={`text-[11px] px-2 py-0.5 rounded-md border transition-all ${
                  isSelected
                    ? 'bg-wine-deep text-white border-wine-deep font-medium'
                    : 'bg-white text-ink-charcoal border-sand-border hover:bg-wine-tint'
                }`}
              >
                {sk.name}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default JobFilterSidebar;
