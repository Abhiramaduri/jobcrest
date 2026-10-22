import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Briefcase, ArrowLeft } from 'lucide-react';
import CustomToaster from '../components/common/Toast';

export const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-sand-canvas flex flex-col justify-between py-10 px-4 sm:px-6 lg:px-8 selection:bg-wine-deep selection:text-white">
      <CustomToaster />
      {/* Top Bar with back link and logo */}
      <div className="max-w-md w-full mx-auto flex items-center justify-between mb-8">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-ink-muted hover:text-wine-deep transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </Link>
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg wine-gradient-bg flex items-center justify-center text-white shadow-wine-sm">
            <Briefcase className="w-4 h-4 text-sand-canvas" />
          </div>
          <span className="font-display text-xl font-bold text-wine-deep">
            JobCrest
          </span>
        </Link>
      </div>

      {/* Main Form Content */}
      <div className="max-w-md w-full mx-auto">
        <Outlet />
      </div>

      {/* Footer footnote */}
      <div className="text-center text-xs text-ink-subtle mt-8">
        Secured with SimpleJWT & Django REST Framework
      </div>
    </div>
  );
};

export default AuthLayout;
