import React from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-sand-canvas border-t border-sand-border pt-16 pb-12 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-5 gap-10 pb-12 border-b border-sand-border">
          {/* Brand Column */}
          <div className="lg:col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl wine-gradient-bg flex items-center justify-center text-white shadow-wine-sm">
                <Briefcase className="w-4 h-4 text-sand-canvas" />
              </div>
              <span className="font-display text-2xl font-bold tracking-tight text-wine-deep">
                JobCrest
              </span>
            </Link>
            <p className="text-sm text-ink-muted leading-relaxed max-w-sm">
              The premier career marketplace connecting visionary organizations with top-tier technology, design, and executive talent.
            </p>
            <div className="flex items-center gap-2 pt-2 text-xs font-semibold text-wine-burgundy">
              <ShieldCheck className="w-4 h-4 text-wine-deep" />
              <span>Verified Employers & Curated Compensation</span>
            </div>
          </div>

          {/* Candidates */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-wine-deep">
              For Job Seekers
            </h4>
            <ul className="space-y-2 text-sm text-ink-muted">
              <li>
                <Link to="/jobs" className="hover:text-wine-deep transition-colors">
                  Browse All Jobs
                </Link>
              </li>
              <li>
                <Link to="/jobs?job_type=remote" className="hover:text-wine-deep transition-colors">
                  Remote Positions
                </Link>
              </li>
              <li>
                <Link to="/companies" className="hover:text-wine-deep transition-colors">
                  Top Companies
                </Link>
              </li>
              <li>
                <Link to="/register" className="hover:text-wine-deep transition-colors">
                  Create Seeker Profile
                </Link>
              </li>
            </ul>
          </div>

          {/* Employers */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-wine-deep">
              For Employers
            </h4>
            <ul className="space-y-2 text-sm text-ink-muted">
              <li>
                <Link to="/register?role=employer" className="hover:text-wine-deep transition-colors">
                  Post an Opportunity
                </Link>
              </li>
              <li>
                <Link to="/employer/dashboard" className="hover:text-wine-deep transition-colors">
                  Hiring Dashboard
                </Link>
              </li>
              <li>
                <Link to="/employer/jobs" className="hover:text-wine-deep transition-colors">
                  Candidate Pipeline
                </Link>
              </li>
              <li>
                <Link to="/login" className="hover:text-wine-deep transition-colors">
                  Recruiter Sign In
                </Link>
              </li>
            </ul>
          </div>

          {/* Editorial Newsletter */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-wine-deep flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-wine-burgundy" />
              Talent Dispatch
            </h4>
            <p className="text-xs text-ink-muted">
              Receive a weekly digest of hand-picked roles and executive career market insights.
            </p>
            <form onSubmit={(e) => { e.preventDefault(); alert('Subscribed to JobCrest Talent Dispatch!'); }} className="space-y-2">
              <div className="relative">
                <input
                  type="email"
                  placeholder="Enter your email"
                  required
                  className="w-full bg-white border border-sand-border rounded-xl px-3.5 py-2 text-xs text-ink-charcoal placeholder:text-ink-subtle focus:outline-none focus:border-wine-deep"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-wine-deep text-white text-xs font-medium py-2 rounded-xl hover:bg-wine-burgundy transition-all flex items-center justify-center gap-1.5 shadow-wine-sm"
              >
                Subscribe <ArrowRight className="w-3 h-3" />
              </button>
            </form>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-ink-subtle gap-4">
          <p>© {new Date().getFullYear()} JobCrest Inc. Powered by Django REST Framework & Vite + React.</p>
          <div className="flex items-center gap-6">
            <span className="hover:text-wine-deep cursor-pointer">Privacy Policy</span>
            <span className="hover:text-wine-deep cursor-pointer">Terms of Service</span>
            <span className="hover:text-wine-deep cursor-pointer">Security Standards</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
