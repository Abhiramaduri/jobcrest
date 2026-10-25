import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import {
  Briefcase,
  Compass,
  Bookmark,
  FileText,
  Calendar,
  User,
  PlusCircle,
  Building2,
  Users,
  LogOut,
  Menu,
  X,
  ChevronDown,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from './Button';
import Badge from './Badge';

export const Navbar = () => {
  const { user, role, isJobSeeker, isEmployer, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    setUserDropdownOpen(false);
    setMobileMenuOpen(false);
    await logout();
    navigate('/');
  };

  const navLinkClasses = ({ isActive }) =>
    `flex items-center gap-2 text-sm font-medium transition-colors py-1.5 px-3 rounded-lg ${
      isActive
        ? 'text-wine-deep bg-wine-tint font-semibold shadow-xs'
        : 'text-ink-muted hover:text-wine-deep hover:bg-sand-border/30'
    }`;

  return (
    <header className="sticky top-0 z-40 w-full bg-sand-canvas/90 backdrop-blur-md border-b border-sand-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl wine-gradient-bg flex items-center justify-center text-white shadow-wine-sm transition-transform duration-300 group-hover:scale-105">
            <Briefcase className="w-5 h-5 text-sand-canvas" />
          </div>
          <div className="flex flex-col">
            <span className="font-display text-2xl font-bold tracking-tight text-wine-deep leading-none">
              JobCrest
            </span>
            <span className="text-[10px] uppercase tracking-widest text-ink-muted font-semibold mt-0.5">
              Executive & Tech
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links based on Role */}
        <nav className="hidden md:flex items-center gap-1.5 lg:gap-2">
          {/* Guest Nav */}
          {!isAuthenticated && (
            <>
              <NavLink to="/jobs" className={navLinkClasses}>
                <Compass className="w-4 h-4" /> Explore Jobs
              </NavLink>
              <NavLink to="/companies" className={navLinkClasses}>
                <Building2 className="w-4 h-4" /> Companies
              </NavLink>
              <NavLink to="/register?role=employer" className={navLinkClasses}>
                <PlusCircle className="w-4 h-4" /> Post a Job
              </NavLink>
            </>
          )}

          {/* Job Seeker Nav */}
          {isAuthenticated && isJobSeeker && (
            <>
              <NavLink to="/jobs" className={navLinkClasses}>
                <Compass className="w-4 h-4" /> Find Jobs
              </NavLink>
              <NavLink to="/saved-jobs" className={navLinkClasses}>
                <Bookmark className="w-4 h-4" /> Saved Jobs
              </NavLink>
              <NavLink to="/applications" className={navLinkClasses}>
                <FileText className="w-4 h-4" /> Applications
              </NavLink>
              <NavLink to="/interviews" className={navLinkClasses}>
                <Calendar className="w-4 h-4" /> Interviews
              </NavLink>
              <NavLink to="/profile" className={navLinkClasses}>
                <User className="w-4 h-4" /> Profile
              </NavLink>
            </>
          )}

          {/* Employer Nav */}
          {isAuthenticated && isEmployer && (
            <>
              <NavLink to="/employer/dashboard" className={navLinkClasses}>
                <Briefcase className="w-4 h-4" /> Dashboard
              </NavLink>
              <NavLink to="/employer/jobs" className={navLinkClasses}>
                <FileText className="w-4 h-4" /> My Jobs
              </NavLink>
              <NavLink to="/employer/jobs/new" className={navLinkClasses}>
                <PlusCircle className="w-4 h-4" /> Post Job
              </NavLink>
              <NavLink to="/employer/interviews" className={navLinkClasses}>
                <Calendar className="w-4 h-4" /> Interviews
              </NavLink>
              <NavLink to="/employer/company" className={navLinkClasses}>
                <Building2 className="w-4 h-4" /> Company
              </NavLink>
            </>
          )}
        </nav>

        {/* Right Action / Auth Buttons */}
        <div className="hidden md:flex items-center gap-3">
          {!isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/login')}
              >
                Sign In
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => navigate('/register')}
              >
                Get Started
              </Button>
            </div>
          ) : (
            <div className="relative">
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="flex items-center gap-2.5 p-1.5 pl-2.5 rounded-xl border border-sand-border hover:border-wine-burgundy bg-white transition-all shadow-xs"
              >
                <div className="w-7 h-7 rounded-lg bg-wine-deep text-white font-bold text-xs flex items-center justify-center">
                  {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="flex flex-col text-left">
                  <span className="text-xs font-semibold text-ink-charcoal leading-tight">
                    {user?.username}
                  </span>
                  <span className="text-[10px] text-wine-burgundy font-medium capitalize">
                    {role === 'jobseeker' ? 'Job Seeker' : 'Employer'}
                  </span>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-ink-subtle ml-1" />
              </button>

              {/* User Dropdown */}
              {userDropdownOpen && (
                <>
                  <div
                    className="fixed inset-0 z-20"
                    onClick={() => setUserDropdownOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-wine-lg border border-sand-border py-2 z-30 divide-y divide-sand-border/60">
                    <div className="px-4 py-2.5">
                      <p className="text-xs text-ink-muted">Signed in as</p>
                      <p className="text-sm font-semibold text-ink-charcoal truncate">
                        {user?.email || user?.username}
                      </p>
                      <div className="mt-1.5">
                        <Badge variant="default" size="sm">
                          {role === 'jobseeker' ? 'Seeker Account' : 'Employer Portal'}
                        </Badge>
                      </div>
                    </div>

                    <div className="py-1">
                      {isJobSeeker && (
                        <>
                          <Link
                            to="/profile"
                            onClick={() => setUserDropdownOpen(false)}
                            className="flex items-center gap-2 px-4 py-2 text-xs text-ink-charcoal hover:bg-wine-tint hover:text-wine-deep"
                          >
                            <User className="w-3.5 h-3.5" /> My Profile & Resume
                          </Link>
                          <Link
                            to="/saved-jobs"
                            onClick={() => setUserDropdownOpen(false)}
                            className="flex items-center gap-2 px-4 py-2 text-xs text-ink-charcoal hover:bg-wine-tint hover:text-wine-deep"
                          >
                            <Bookmark className="w-3.5 h-3.5" /> Saved Opportunities
                          </Link>
                        </>
                      )}
                      {isEmployer && (
                        <>
                          <Link
                            to="/employer/dashboard"
                            onClick={() => setUserDropdownOpen(false)}
                            className="flex items-center gap-2 px-4 py-2 text-xs text-ink-charcoal hover:bg-wine-tint hover:text-wine-deep"
                          >
                            <Briefcase className="w-3.5 h-3.5" /> Employer Dashboard
                          </Link>
                          <Link
                            to="/employer/jobs/new"
                            onClick={() => setUserDropdownOpen(false)}
                            className="flex items-center gap-2 px-4 py-2 text-xs text-ink-charcoal hover:bg-wine-tint hover:text-wine-deep"
                          >
                            <PlusCircle className="w-3.5 h-3.5" /> Post New Job
                          </Link>
                        </>
                      )}
                    </div>

                    <div className="py-1">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-4 py-2 text-xs text-status-error hover:bg-rose-50"
                      >
                        <LogOut className="w-3.5 h-3.5" /> Sign Out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Mobile menu button */}
        <div className="flex md:hidden items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-ink-charcoal hover:bg-sand-border/50"
            aria-label="Toggle navigation"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-sand-border bg-white px-4 pt-3 pb-6 space-y-2 shadow-wine-md">
          {!isAuthenticated ? (
            <div className="flex flex-col gap-1.5 pt-2">
              <Link
                to="/jobs"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg"
              >
                Explore Jobs
              </Link>
              <Link
                to="/companies"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg"
              >
                Companies
              </Link>
              <Link
                to="/register?role=employer"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg"
              >
                Post a Job
              </Link>
              <div className="flex gap-2 pt-3 border-t border-sand-border">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-1/2"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    navigate('/login');
                  }}
                >
                  Sign In
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  className="w-1/2"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    navigate('/register');
                  }}
                >
                  Register
                </Button>
              </div>
            </div>
          ) : isJobSeeker ? (
            <div className="flex flex-col gap-1">
              <div className="p-3 bg-wine-tint/60 rounded-xl mb-2 flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-wine-deep">{user?.username}</p>
                  <p className="text-[11px] text-ink-muted">{user?.email}</p>
                </div>
                <Badge variant="default" size="sm">Job Seeker</Badge>
              </div>
              <Link to="/jobs" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Find Jobs</Link>
              <Link to="/saved-jobs" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Saved Jobs</Link>
              <Link to="/applications" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">My Applications</Link>
              <Link to="/interviews" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Interviews</Link>
              <Link to="/profile" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Profile & Resume</Link>
              <button onClick={handleLogout} className="mt-3 text-left px-3 py-2 text-sm font-medium text-status-error hover:bg-rose-50 rounded-lg">Sign Out</button>
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              <div className="p-3 bg-wine-tint/60 rounded-xl mb-2 flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-wine-deep">{user?.username}</p>
                  <p className="text-[11px] text-ink-muted">{user?.email}</p>
                </div>
                <Badge variant="default" size="sm">Employer</Badge>
              </div>
              <Link to="/employer/dashboard" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Dashboard</Link>
              <Link to="/employer/jobs" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">My Jobs</Link>
              <Link to="/employer/jobs/new" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Post New Job</Link>
              <Link to="/employer/interviews" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Interviews</Link>
              <Link to="/employer/company" onClick={() => setMobileMenuOpen(false)} className="px-3 py-2 text-sm font-medium text-ink-charcoal hover:bg-wine-tint rounded-lg">Company Settings</Link>
              <button onClick={handleLogout} className="mt-3 text-left px-3 py-2 text-sm font-medium text-status-error hover:bg-rose-50 rounded-lg">Sign Out</button>
            </div>
          )}
        </div>
      )}
    </header>
  );
};

export default Navbar;
