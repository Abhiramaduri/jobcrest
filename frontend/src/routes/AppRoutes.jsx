import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import AuthLayout from '../layouts/AuthLayout';
import ProtectedRoute from './ProtectedRoute';

// Pages
import Home from '../pages/Home';
import Jobs from '../pages/Jobs';
import JobDetail from '../pages/JobDetail';
import Companies from '../pages/Companies';
import Login from '../pages/Login';
import Register from '../pages/Register';
import ForgotPassword from '../pages/ForgotPassword';

// Job Seeker Pages
import Profile from '../pages/Profile';
import Applications from '../pages/Applications';
import SavedJobs from '../pages/SavedJobs';
import Interviews from '../pages/Interviews';

// Employer Pages
import EmployerDashboard from '../pages/EmployerDashboard';
import EmployerJobs from '../pages/EmployerJobs';
import JobPostWizard from '../pages/JobPostWizard';
import EmployerInterviews from '../pages/EmployerInterviews';
import EmployerCompany from '../pages/EmployerCompany';

// 404 Component
const NotFound = () => (
  <div className="max-w-md mx-auto px-4 py-24 text-center space-y-4">
    <h1 className="font-display text-6xl font-extrabold text-wine-deep">404</h1>
    <h2 className="font-display text-2xl font-bold text-ink-charcoal">Page Not Found</h2>
    <p className="text-xs text-ink-muted">The requested path does not exist on JobCrest.</p>
    <a
      href="/"
      className="inline-flex items-center justify-center font-medium rounded-xl text-xs px-4 py-2 gap-1.5 shadow-wine-sm bg-wine-deep text-white hover:bg-wine-burgundy transition-all"
    >
      Return to Home
    </a>
  </div>
);

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Pages with Main Layout */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/:slug" element={<JobDetail />} />
        <Route path="/companies" element={<Companies />} />

        {/* Job Seeker Protected Routes */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute allowedRoles={['jobseeker']}>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/applications"
          element={
            <ProtectedRoute allowedRoles={['jobseeker']}>
              <Applications />
            </ProtectedRoute>
          }
        />
        <Route
          path="/saved-jobs"
          element={
            <ProtectedRoute allowedRoles={['jobseeker']}>
              <SavedJobs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interviews"
          element={
            <ProtectedRoute allowedRoles={['jobseeker']}>
              <Interviews />
            </ProtectedRoute>
          }
        />

        {/* Employer Protected Routes */}
        <Route
          path="/employer/dashboard"
          element={
            <ProtectedRoute allowedRoles={['employer']}>
              <EmployerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/employer/jobs"
          element={
            <ProtectedRoute allowedRoles={['employer']}>
              <EmployerJobs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/employer/jobs/new"
          element={
            <ProtectedRoute allowedRoles={['employer']}>
              <JobPostWizard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/employer/interviews"
          element={
            <ProtectedRoute allowedRoles={['employer']}>
              <EmployerInterviews />
            </ProtectedRoute>
          }
        />
        <Route
          path="/employer/company"
          element={
            <ProtectedRoute allowedRoles={['employer']}>
              <EmployerCompany />
            </ProtectedRoute>
          }
        />

        {/* Catch-all 404 */}
        <Route path="*" element={<NotFound />} />
      </Route>

      {/* Auth Layout for Login / Register / Forgot Password */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
