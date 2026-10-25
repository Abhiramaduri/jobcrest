import React, { useState } from 'react';
import { FileText, Upload, CheckCircle2, Download, AlertCircle, RefreshCw } from 'lucide-react';
import profileApi from '../../api/profileApi';
import Button from '../common/Button';
import toast from 'react-hot-toast';

export const ResumeUploader = ({ resumeUrl, onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = async (file) => {
    if (!file) return;

    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      toast.error('Only PDF documents are supported for resumes.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size exceeds 10MB limit.');
      return;
    }

    setIsUploading(true);
    try {
      await profileApi.uploadResume(file);
      toast.success('Resume uploaded successfully!');
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      console.error('Resume upload failed:', err);
      toast.error(err?.response?.data?.detail || 'Failed to upload resume.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="space-y-4">
      {/* Existing Resume Preview Card */}
      {resumeUrl ? (
        <div className="p-4 rounded-xl border border-wine-burgundy/30 bg-wine-tint/40 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-wine-deep text-white shadow-wine-sm">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-wine-deep flex items-center gap-1.5">
                Primary PDF Resume
                <CheckCircle2 className="w-3.5 h-3.5 text-status-success" />
              </p>
              <p className="text-[11px] text-ink-muted">
                Active document attached to your job applications
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={resumeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 rounded-lg border border-sand-border bg-white text-xs font-semibold text-wine-deep hover:bg-sand-surface flex items-center gap-1.5 shadow-xs transition-colors"
            >
              <Download className="w-3.5 h-3.5" /> View / Download
            </a>
          </div>
        </div>
      ) : (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center gap-2.5 text-xs text-amber-800">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>You haven't uploaded a master resume yet. Employers favor profiles with verified PDF resumes.</span>
        </div>
      )}

      {/* Upload Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all ${
          dragActive
            ? 'border-wine-deep bg-wine-tint/60 scale-[1.01]'
            : 'border-sand-border hover:border-wine-burgundy/50 bg-white'
        }`}
      >
        <div className="max-w-sm mx-auto space-y-3 flex flex-col items-center">
          <div className="w-12 h-12 rounded-xl bg-sand-canvas flex items-center justify-center text-wine-deep">
            {isUploading ? (
              <RefreshCw className="w-5 h-5 animate-spin" />
            ) : (
              <Upload className="w-5 h-5" />
            )}
          </div>
          <div>
            <p className="text-xs font-bold text-ink-charcoal">
              {isUploading ? 'Uploading Resume...' : 'Drop your PDF resume here, or browse'}
            </p>
            <p className="text-[11px] text-ink-subtle mt-0.5">
              Supports PDF documents up to 10MB
            </p>
          </div>

          <label className="cursor-pointer">
            <span className="inline-flex items-center justify-center font-medium rounded-xl text-xs px-4 py-2 gap-1.5 shadow-wine-sm bg-wine-deep text-white hover:bg-wine-burgundy transition-all">
              Choose File
            </span>
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleChange}
              disabled={isUploading}
              className="hidden"
            />
          </label>
        </div>
      </div>
    </div>
  );
};

export default ResumeUploader;
