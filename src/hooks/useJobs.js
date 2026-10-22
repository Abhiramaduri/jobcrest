import { useState, useEffect, useCallback } from 'react';
import jobsApi from '../api/jobsApi';
import toast from 'react-hot-toast';

export function useJobs(initialFilters = {}) {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);
  const [savedJobIds, setSavedJobIds] = useState(new Set());

  const fetchJobs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await jobsApi.getJobs(filters);
      setJobs(Array.isArray(data) ? data : (data.results || []));
    } catch (err) {
      console.error('Failed to load jobs:', err);
      setError(err?.response?.data?.detail || 'Failed to load jobs. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const updateFilters = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const resetFilters = () => {
    setFilters({});
  };

  const toggleSaveJob = async (job) => {
    const isSaved = savedJobIds.has(job.slug || job.id);
    try {
      if (isSaved) {
        await jobsApi.unsaveJob(job.slug);
        setSavedJobIds((prev) => {
          const next = new Set(prev);
          next.delete(job.slug || job.id);
          return next;
        });
        toast.success('Job removed from saved list');
      } else {
        await jobsApi.saveJob(job.slug);
        setSavedJobIds((prev) => {
          const next = new Set(prev);
          next.add(job.slug || job.id);
          return next;
        });
        toast.success('Job saved successfully');
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Action failed');
    }
  };

  return {
    jobs,
    isLoading,
    error,
    filters,
    updateFilters,
    resetFilters,
    refetch: fetchJobs,
    savedJobIds,
    setSavedJobIds,
    toggleSaveJob,
  };
}

export default useJobs;
