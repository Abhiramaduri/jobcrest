import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  MapPin,
  Briefcase,
  Building2,
  TrendingUp,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Code2,
  Palette,
  Megaphone,
  Coins,
  CheckCircle,
} from 'lucide-react';
import jobsApi from '../api/jobsApi';
import JobCard from '../components/jobs/JobCard';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';

export const Home = () => {
  const navigate = useNavigate();
  const [featuredJobs, setFeaturedJobs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Search Bar State
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [jobsData, catsData] = await Promise.all([
          jobsApi.getJobs({ ordering: '-created_at' }).catch(() => []),
          jobsApi.getCategories().catch(() => []),
        ]);
        const list = Array.isArray(jobsData) ? jobsData : (jobsData.results || []);
        setFeaturedJobs(list.slice(0, 6));
        setCategories(catsData || []);
      } catch (err) {
        console.error('Home load error:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (keyword.trim()) params.set('search', keyword.trim());
    if (location.trim()) params.set('location', location.trim());
    if (selectedCategory) params.set('category', selectedCategory);
    navigate(`/jobs?${params.toString()}`);
  };

  const categoryIcons = {
    Technology: Code2,
    Design: Palette,
    Marketing: Megaphone,
    Finance: Coins,
  };

  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-20 md:pb-28 overflow-hidden bg-sand-canvas">
        {/* Subtle decorative radial glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-wine-tint/70 rounded-full blur-3xl pointer-events-none -z-10" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          {/* Editorial Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-wine-tint border border-wine-burgundy/20 text-xs font-bold text-wine-deep shadow-xs animate-fade-in">
            <Sparkles className="w-3.5 h-3.5 text-wine-burgundy" />
            <span>The Curated Career Marketplace for Visionaries</span>
          </div>

          {/* Heading */}
          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-extrabold text-wine-deep tracking-tight leading-[1.12]">
            Where Exceptional Talent Meets <br className="hidden sm:inline" />
            <span className="italic font-normal text-wine-burgundy">Uncompromising Ambition.</span>
          </h1>

          {/* Subheading */}
          <p className="max-w-2xl mx-auto text-base sm:text-lg text-ink-muted leading-relaxed">
            Discover verified leadership, engineering, and creative positions with transparent compensation and high-impact teams.
          </p>

          {/* Search Bar Panel */}
          <form
            onSubmit={handleSearchSubmit}
            className="mt-10 bg-white p-3 sm:p-4 rounded-2xl shadow-wine-md border border-sand-border grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-10 gap-3 text-left max-w-4xl mx-auto"
          >
            {/* Keyword Input */}
            <div className="sm:col-span-1 lg:col-span-4 flex items-center gap-2.5 px-3 py-1.5 border-b sm:border-b-0 sm:border-r border-sand-border/80">
              <Search className="w-4 h-4 text-wine-burgundy flex-shrink-0" />
              <input
                type="text"
                placeholder="Job title, keywords, or role..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full text-xs sm:text-sm text-ink-charcoal placeholder:text-ink-subtle focus:outline-none"
              />
            </div>

            {/* Location Input */}
            <div className="sm:col-span-1 lg:col-span-3 flex items-center gap-2.5 px-3 py-1.5 border-b sm:border-b-0 sm:border-r border-sand-border/80">
              <MapPin className="w-4 h-4 text-wine-burgundy flex-shrink-0" />
              <input
                type="text"
                placeholder="City or Remote..."
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full text-xs sm:text-sm text-ink-charcoal placeholder:text-ink-subtle focus:outline-none"
              />
            </div>

            {/* Category Dropdown */}
            <div className="sm:col-span-1 lg:col-span-3 flex items-center gap-2 px-2">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full text-xs sm:text-sm text-ink-charcoal bg-transparent focus:outline-none cursor-pointer"
              >
                <option value="">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>

              <Button
                type="submit"
                variant="primary"
                size="md"
                className="flex-shrink-0 shadow-wine-sm"
              >
                Search
              </Button>
            </div>
          </form>

          {/* Quick Search Tag Suggestions */}
          <div className="pt-2 flex flex-wrap items-center justify-center gap-2 text-xs text-ink-muted">
            <span className="font-semibold text-wine-burgundy">Popular:</span>
            {['Software Engineer', 'Product Designer', 'Remote', 'Data Science', 'Engineering Manager'].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => {
                  setKeyword(t);
                  navigate(`/jobs?search=${encodeURIComponent(t)}`);
                }}
                className="px-2.5 py-1 rounded-lg bg-white border border-sand-border hover:border-wine-burgundy text-ink-charcoal hover:text-wine-deep transition-all shadow-xs"
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Stats Strip */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 bg-white p-6 sm:p-8 rounded-2xl border border-sand-border shadow-wine-sm">
          {[
            { value: '2,400+', label: 'Active Opportunities', icon: Briefcase },
            { value: '450+', label: 'Verified Companies', icon: Building2 },
            { value: '98%', label: 'Offer Transparency', icon: ShieldCheck },
            { value: '14 Days', label: 'Average Time to Hire', icon: TrendingUp },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="flex items-center gap-3.5 p-2">
                <div className="w-11 h-11 rounded-xl bg-wine-tint text-wine-deep flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-display text-xl sm:text-2xl font-bold text-wine-deep leading-tight">
                    {stat.value}
                  </h4>
                  <p className="text-xs text-ink-muted font-medium mt-0.5">
                    {stat.label}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Category Grid Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4">
          <div>
            <Badge variant="default" size="sm">
              Disciplines
            </Badge>
            <h2 className="font-display text-3xl font-bold text-wine-deep mt-2">
              Explore by Specialization
            </h2>
            <p className="text-xs sm:text-sm text-ink-muted mt-1">
              Curated roles tailored across industry disciplines and career trajectories.
            </p>
          </div>
          <Link
            to="/jobs"
            className="text-xs sm:text-sm font-bold text-wine-deep hover:text-wine-burgundy flex items-center gap-1 group"
          >
            View all categories <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {categories.length > 0
            ? categories.slice(0, 8).map((cat) => {
                const Icon = categoryIcons[cat.name] || Briefcase;
                return (
                  <Link
                    key={cat.id}
                    to={`/jobs?category=${cat.id}`}
                    className="p-5 rounded-2xl bg-white border border-sand-border hover:border-wine-burgundy hover:shadow-wine-md hover:-translate-y-1 transition-all group flex flex-col justify-between h-40"
                  >
                    <div className="w-10 h-10 rounded-xl bg-wine-tint text-wine-deep flex items-center justify-center group-hover:bg-wine-deep group-hover:text-white transition-colors">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-display text-lg font-bold text-ink-charcoal group-hover:text-wine-deep transition-colors">
                        {cat.name}
                      </h4>
                      <p className="text-xs text-ink-muted mt-1 flex items-center gap-1">
                        Explore openings &rarr;
                      </p>
                    </div>
                  </Link>
                );
              })
            : ['Engineering & Architecture', 'Product & Design', 'Sales & Growth', 'Operations & People'].map((name, i) => (
                <Link
                  key={i}
                  to="/jobs"
                  className="p-5 rounded-2xl bg-white border border-sand-border hover:border-wine-burgundy hover:shadow-wine-md hover:-translate-y-1 transition-all group flex flex-col justify-between h-40"
                >
                  <div className="w-10 h-10 rounded-xl bg-wine-tint text-wine-deep flex items-center justify-center">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-display text-lg font-bold text-ink-charcoal">
                      {name}
                    </h4>
                    <p className="text-xs text-ink-muted mt-1">
                      Explore openings &rarr;
                    </p>
                  </div>
                </Link>
              ))}
        </div>
      </section>

      {/* Featured Jobs Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4">
          <div>
            <Badge variant="wine" size="sm">
              Hand-Picked
            </Badge>
            <h2 className="font-display text-3xl font-bold text-wine-deep mt-2">
              Featured Opportunities
            </h2>
            <p className="text-xs sm:text-sm text-ink-muted mt-1">
              High-growth teams looking for standout candidates this week.
            </p>
          </div>
          <Link
            to="/jobs"
            className="text-xs sm:text-sm font-bold text-wine-deep hover:text-wine-burgundy flex items-center gap-1 group"
          >
            Explore all {featuredJobs.length} jobs <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div
                key={n}
                className="h-56 bg-white rounded-2xl border border-sand-border p-6 skeleton"
              />
            ))}
          </div>
        ) : featuredJobs.length === 0 ? (
          <div className="bg-white rounded-2xl border border-sand-border p-12 text-center space-y-3">
            <Briefcase className="w-10 h-10 text-wine-burgundy/40 mx-auto" />
            <h3 className="font-display text-lg font-bold text-ink-charcoal">
              No Published Positions At This Moment
            </h3>
            <p className="text-xs text-ink-muted max-w-sm mx-auto">
              Employers are actively creating new requisitions. Check back soon or register as an employer to publish roles.
            </p>
            <Button
              variant="primary"
              size="sm"
              onClick={() => navigate('/register?role=employer')}
            >
              Post the First Job
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredJobs.map((job) => (
              <JobCard key={job.id || job.slug} job={job} />
            ))}
          </div>
        )}
      </section>

      {/* Employer CTA Banner */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="wine-gradient-bg rounded-3xl p-8 sm:p-12 text-white relative overflow-hidden shadow-wine-lg">
          <div className="absolute right-0 top-0 translate-x-1/4 -translate-y-1/4 w-96 h-96 bg-wine-burgundy/40 rounded-full blur-2xl pointer-events-none" />

          <div className="max-w-2xl space-y-5 relative z-10">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-wine-tint bg-white/10 px-3 py-1 rounded-full backdrop-blur-sm">
              <Sparkles className="w-3.5 h-3.5" /> For Visionary Employers
            </span>
            <h2 className="font-display text-3xl sm:text-4xl font-extrabold tracking-tight text-sand-canvas">
              Hiring top-tier talent? <br />
              Post an opportunity in under 2 minutes.
            </h2>
            <p className="text-sm text-sand-border leading-relaxed">
              Reach thousands of pre-screened senior engineers, executives, and designers. Leverage full-cycle applicant tracking and integrated video interview scheduling.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-4">
              <Button
                variant="secondary"
                size="lg"
                onClick={() => navigate('/register?role=employer')}
                className="bg-white text-wine-deep hover:bg-sand-surface"
              >
                Post an Opportunity
              </Button>
              <Link
                to="/companies"
                className="text-xs font-semibold text-sand-canvas hover:underline flex items-center gap-1"
              >
                Learn more about our employer tools &rarr;
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
