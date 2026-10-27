import React, { useState } from 'react';
import { GraduationCap, Pencil, Trash2, Calendar } from 'lucide-react';
import Modal from '../common/Modal';
import Input from '../common/Input';
import Button from '../common/Button';
import Badge from '../common/Badge';
import profileApi from '../../api/profileApi';
import toast from 'react-hot-toast';

export const EducationCard = ({ education, onRefresh }) => {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [formData, setFormData] = useState({
    degree: education.degree || '',
    institution: education.institution || '',
    field_of_study: education.field_of_study || '',
    start_year: education.start_year || '',
    end_year: education.end_year || '',
    is_current: education.is_current || false,
    grade: education.grade || '',
  });

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to remove this education entry?')) return;
    setIsDeleting(true);
    try {
      await profileApi.deleteEducation(education.id);
      toast.success('Education removed');
      onRefresh();
    } catch {
      toast.error('Failed to remove education');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const payload = {
        degree: formData.degree,
        institution: formData.institution,
        field_of_study: formData.field_of_study,
        start_year: Number(formData.start_year),
        end_year: formData.is_current ? null : (formData.end_year ? Number(formData.end_year) : null),
        is_current: Boolean(formData.is_current),
        grade: formData.grade,
      };
      await profileApi.updateEducation(education.id, payload);
      toast.success('Education updated successfully');
      setIsEditModalOpen(false);
      onRefresh();
    } catch {
      toast.error('Failed to update education');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <div className="bg-sand-canvas/40 border border-sand-border rounded-xl p-4 flex items-start justify-between gap-4 transition-all hover:border-wine-burgundy/40">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-lg bg-wine-tint text-wine-deep flex-shrink-0 mt-0.5">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-bold text-sm text-ink-charcoal">
                {education.degree} {education.field_of_study && `in ${education.field_of_study}`}
              </h4>
              {education.is_current && (
                <Badge variant="success" size="sm">
                  Currently Studying
                </Badge>
              )}
            </div>
            <p className="text-xs text-wine-burgundy font-semibold mt-0.5">
              {education.institution}
            </p>
            <div className="flex items-center gap-3 text-[11px] text-ink-subtle mt-1.5">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {education.start_year} — {education.is_current ? 'Present' : (education.end_year || 'Present')}
              </span>
              {education.grade && (
                <span className="font-medium text-ink-muted">Grade: {education.grade}</span>
              )}
            </div>
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
        title="Edit Education"
      >
        <form onSubmit={handleUpdate} className="space-y-4">
          <Input
            label="Degree"
            value={formData.degree}
            onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
            required
          />
          <Input
            label="Institution / University"
            value={formData.institution}
            onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
            required
          />
          <Input
            label="Field of Study"
            value={formData.field_of_study}
            onChange={(e) => setFormData({ ...formData, field_of_study: e.target.value })}
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Start Year"
              type="number"
              value={formData.start_year}
              onChange={(e) => setFormData({ ...formData, start_year: e.target.value })}
              required
            />
            <Input
              label="End Year"
              type="number"
              disabled={formData.is_current}
              placeholder={formData.is_current ? 'Present' : '2024'}
              value={formData.is_current ? '' : formData.end_year}
              onChange={(e) => setFormData({ ...formData, end_year: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-ink-charcoal select-none">
            <input
              type="checkbox"
              checked={formData.is_current}
              onChange={(e) => {
                const checked = e.target.checked;
                setFormData({
                  ...formData,
                  is_current: checked,
                  end_year: checked ? '' : formData.end_year,
                });
              }}
              className="w-4 h-4 rounded text-wine-deep accent-wine-deep cursor-pointer"
            />
            <span>Currently studying here</span>
          </label>
          <Input
            label="Grade / GPA"
            value={formData.grade}
            onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
          />
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

export default EducationCard;
