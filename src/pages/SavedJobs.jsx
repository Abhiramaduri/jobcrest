import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bookmark, Briefcase, Trash2, ArrowRight } from 'lucide-react';
import jobsApi from '../api/jobsApi';
import JobCard from '../components/jobs/JobCard';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

export const SavedJobs = () => {
  const [savedJobs, setSavedJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadSavedJobs = async () => {
    setIsLoading(true);
    try {
      const data = await jobsApi.getSavedJobs();
      setSavedJobs(Array.isArray(data) ? data : (data.results || []));
    } catch (err) {
      console.error('Failed to load saved jobs:', err);
      toast.error('Failed to load saved jobs');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSavedJobs();
  }, []);

  const handleUnsave = async (job) => {
    try {
      await jobsApi.unsaveJob(job.slug);
      toast.success('Opportunity removed from saved list');
      setSavedJobs((prev) => prev.filter((item) => item.job?.slug !== job.slug));
    } catch {
      toast.error('Failed to unsave job');
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-sand-border">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl font-extrabold text-wine-deep">
            Saved Opportunities
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted mt-1">
            Revisit bookmarked roles and submit applications at your own pace
          </p>
        </div>

        <Link to="/jobs">
          <Button variant="outline" size="sm" icon={Briefcase}>
            Browse More Roles
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-56 bg-white rounded-2xl border border-sand-border skeleton" />
          ))}
        </div>
      ) : savedJobs.length === 0 ? (
        <div className="bg-white rounded-3xl border border-sand-border p-12 text-center space-y-4 shadow-wine-sm">
          <Bookmark className="w-12 h-12 text-wine-burgundy/40 mx-auto" />
          <h3 className="font-display text-xl font-bold text-ink-charcoal">
            Your saved list is empty
          </h3>
          <p className="text-xs text-ink-muted max-w-sm mx-auto">
            Click the bookmark icon on any job card to save opportunities you're interested in for later.
          </p>
          <Link to="/jobs">
            <Button variant="primary" size="sm">
              Discover Jobs
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedJobs.map((item) => (
            <JobCard
              key={item.id}
              job={item.job}
              isSaved={true}
              onToggleSave={handleUnsave}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default SavedJobs;
