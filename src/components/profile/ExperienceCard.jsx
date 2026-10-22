import React, { useState } from 'react';
import { Briefcase, Pencil, Trash2, Calendar, MapPin } from 'lucide-react';
import Modal from '../common/Modal';
import Input from '../common/Input';
import Button from '../common/Button';
import Badge from '../common/Badge';
import profileApi from '../../api/profileApi';
import toast from 'react-hot-toast';

export const ExperienceCard = ({ experience, onRefresh }) => {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [formData, setFormData] = useState({
    company_name: experience.company_name || '',
    role_title: experience.role_title || '',
    start_date: experience.start_date || '',
    end_date: experience.end_date || '',
    is_current: experience.is_current || false,
    description: experience.description || '',
  });

  const handleDelete = async () => {
    if (!window.confirm('Delete this work experience?')) return;
    setIsDeleting(true);
    try {
      await profileApi.deleteExperience(experience.id);
      toast.success('Experience deleted');
      onRefresh();
    } catch {
      toast.error('Failed to delete experience');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await profileApi.updateExperience(experience.id, formData);
      toast.success('Experience updated successfully');
      setIsEditModalOpen(false);
      onRefresh();
    } catch {
      toast.error('Failed to update experience');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <div className="bg-sand-canvas/40 border border-sand-border rounded-xl p-4 flex items-start justify-between gap-4 transition-all hover:border-wine-burgundy/40">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-lg bg-wine-tint text-wine-deep flex-shrink-0 mt-0.5">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-sm text-ink-charcoal">
                {experience.role_title}
              </h4>
              {experience.is_current && (
                <Badge variant="success" size="sm">
                  Current
                </Badge>
              )}
            </div>
            <p className="text-xs text-wine-burgundy font-semibold mt-0.5">
              {experience.company_name}
            </p>
            <div className="flex items-center gap-2 text-[11px] text-ink-subtle mt-1.5">
              <Calendar className="w-3 h-3" />
              <span>
                {experience.start_date} — {experience.is_current ? 'Present' : experience.end_date}
              </span>
            </div>
            {experience.description && (
              <p className="text-xs text-ink-muted mt-2 line-clamp-3 leading-relaxed whitespace-pre-line">
                {experience.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1 flex-shrink-0">
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="p-1.5 text-ink-subtle hover:text-wine-deep hover:bg-wine-tint rounded-lg transition-colors"
            title="Edit"
          >
            <Pencil className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="p-1.5 text-ink-subtle hover:text-status-error hover:bg-rose-50 rounded-lg transition-colors"
            title="Delete"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Edit Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Experience"
      >
        <form onSubmit={handleUpdate} className="space-y-4">
          <Input
            label="Role Title"
            value={formData.role_title}
            onChange={(e) => setFormData({ ...formData, role_title: e.target.value })}
            required
          />
          <Input
            label="Company Name"
            value={formData.company_name}
            onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
            required
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Start Date"
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              required
            />
            <Input
              label="End Date"
              type="date"
              disabled={formData.is_current}
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-ink-charcoal">
            <input
              type="checkbox"
              checked={formData.is_current}
              onChange={(e) => setFormData({ ...formData, is_current: e.target.checked })}
              className="rounded accent-wine-deep"
            />
            I currently work here
          </label>
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">
              Responsibilities & Key Impact
            </label>
            <textarea
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-white border border-sand-border rounded-xl p-3 text-xs text-ink-charcoal focus:outline-none focus:border-wine-deep"
              placeholder="Describe accomplishments, technologies deployed, and team leadership..."
            />
          </div>
          <div className="flex justify-end gap-2 pt-3 border-t border-sand-border">
            <Button variant="outline" size="sm" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSaving}>
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>
    </>
  );
};

export default ExperienceCard;
