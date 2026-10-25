import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import CustomToaster from '../components/common/Toast';
import { useAuth } from '../context/AuthContext';
import {
  Briefcase,
  FileText,
  Calendar,
  User,
  Bookmark,
  PlusCircle,
  Building2,
  Users,
} from 'lucide-react';

export const DashboardLayout = () => {
  const { role, isJobSeeker, isEmployer } = useAuth();

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
      isActive
        ? 'bg-wine-deep text-white shadow-wine-sm'
        : 'text-ink-muted hover:text-wine-deep hover:bg-wine-tint'
    }`;

  return (
    <div className="min-h-screen flex flex-col bg-sand-canvas text-ink-charcoal">
      <CustomToaster />
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex-grow">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Dashboard Left Sidebar */}
          <aside className="lg:col-span-1">
            <div className="bg-white rounded-2xl border border-sand-border p-5 shadow-wine-sm sticky top-28 space-y-6">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-wine-burgundy">
                  {isEmployer ? 'Employer Workspace' : 'Candidate Workspace'}
                </p>
                <h3 className="font-display text-lg font-bold text-ink-charcoal mt-1">
                  Management Hub
                </h3>
              </div>

              <nav className="space-y-1.5">
                {isJobSeeker && (
                  <>
                    <NavLink to="/applications" className={linkClass}>
                      <FileText className="w-4 h-4" /> My Applications
                    </NavLink>
                    <NavLink to="/saved-jobs" className={linkClass}>
                      <Bookmark className="w-4 h-4" /> Saved Opportunities
                    </NavLink>
                    <NavLink to="/interviews" className={linkClass}>
                      <Calendar className="w-4 h-4" /> Interview Schedule
                    </NavLink>
                    <NavLink to="/profile" className={linkClass}>
                      <User className="w-4 h-4" /> Profile & Resume
                    </NavLink>
                    <NavLink to="/jobs" className={linkClass}>
                      <Briefcase className="w-4 h-4" /> Explore Jobs
                    </NavLink>
                  </>
                )}

                {isEmployer && (
                  <>
                    <NavLink to="/employer/dashboard" className={linkClass}>
                      <Briefcase className="w-4 h-4" /> Overview Dashboard
                    </NavLink>
                    <NavLink to="/employer/jobs" className={linkClass}>
                      <FileText className="w-4 h-4" /> Manage Job Postings
                    </NavLink>
                    <NavLink to="/employer/jobs/new" className={linkClass}>
                      <PlusCircle className="w-4 h-4" /> Create New Job
                    </NavLink>
                    <NavLink to="/employer/interviews" className={linkClass}>
                      <Calendar className="w-4 h-4" /> Candidate Interviews
                    </NavLink>
                    <NavLink to="/employer/company" className={linkClass}>
                      <Building2 className="w-4 h-4" /> Company Profile
                    </NavLink>
                  </>
                )}
              </nav>
            </div>
          </aside>

          {/* Main Dashboard Content Area */}
          <section className="lg:col-span-3">
            <Outlet />
          </section>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default DashboardLayout;
