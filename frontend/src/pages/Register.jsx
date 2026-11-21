import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { User, Mail, Lock, Phone, Building2, AlertCircle, ShieldCheck, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import authApi from '../api/authApi';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

// Step enum
const STEP = { FORM: 'form', OTP: 'otp' };

export const Register = () => {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialRole = searchParams.get('role') === 'employer' ? 'employer' : 'jobseeker';

  const [activeTab, setActiveTab] = useState(initialRole);
  const [step, setStep] = useState(STEP.FORM);
  const [isLoading, setIsLoading] = useState(false);
  const [isSendingOtp, setIsSendingOtp] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState(null);
  const [otp, setOtp] = useState('');
  const [userEmail, setUserEmail] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: { username: '', email: '', phone_number: '', password: '', passwordConfirm: '' },
  });

  const passwordVal = watch('password');

  // Step 1: Send OTP to email
  const onSubmit = async (data) => {
    setIsSendingOtp(true);
    setErrorMessage('');
    try {
      await authApi.sendRegistrationOtp(data.email);
      setFormData({ ...data, role: activeTab });
      setUserEmail(data.email);
      setStep(STEP.OTP);
      toast.success(`OTP sent to ${data.email}`);
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to send OTP. Please try again.';
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setIsSendingOtp(false);
    }
  };

  // Step 2: Verify OTP & complete registration
  const onVerifyOtp = async (e) => {
    e.preventDefault();
    if (otp.length !== 6) {
      toast.error('Please enter the 6-digit OTP.');
      return;
    }
    setIsLoading(true);
    setErrorMessage('');
    try {
      const user = await registerUser({ ...formData, otp });
      toast.success('Account created successfully! Welcome to JobCrest 🎉');
      navigate(activeTab === 'employer' ? '/employer/dashboard' : '/profile');
    } catch (err) {
      const res = err?.response?.data;
      let msg = 'Verification failed. Please check your OTP.';
      if (res?.detail) msg = res.detail;
      else if (res?.non_field_errors) msg = res.non_field_errors.join(' ');
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const resendOtp = async () => {
    setIsSendingOtp(true);
    try {
      await authApi.sendRegistrationOtp(userEmail);
      toast.success('New OTP sent!');
    } catch {
      toast.error('Could not resend OTP.');
    } finally {
      setIsSendingOtp(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-md space-y-6">
      <div className="text-center space-y-1.5">
        <h2 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep">
          {step === STEP.OTP ? 'Verify Your Email' : 'Join JobCrest'}
        </h2>
        <p className="text-xs sm:text-sm text-ink-muted">
          {step === STEP.OTP
            ? `Enter the 6-digit OTP sent to ${userEmail}`
            : 'Choose your account type to get started'}
        </p>
      </div>

      {/* ── STEP 1: Registration Form ── */}
      {step === STEP.FORM && (
        <>
          {/* Role Switcher */}
          <div className="grid grid-cols-2 p-1.5 bg-sand-canvas border border-sand-border rounded-2xl">
            <button
              type="button"
              onClick={() => setActiveTab('jobseeker')}
              className={`flex items-center justify-center gap-2 py-2.5 text-xs font-bold rounded-xl transition-all ${
                activeTab === 'jobseeker' ? 'bg-wine-deep text-white shadow-wine-sm' : 'text-ink-muted hover:text-wine-deep'
              }`}
            >
              <User className="w-4 h-4" />
              <span>I'm a Job Seeker</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('employer')}
              className={`flex items-center justify-center gap-2 py-2.5 text-xs font-bold rounded-xl transition-all ${
                activeTab === 'employer' ? 'bg-wine-deep text-white shadow-wine-sm' : 'text-ink-muted hover:text-wine-deep'
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>I'm an Employer</span>
            </button>
          </div>

          {errorMessage && (
            <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Username"
              placeholder="e.g. alexander_dev"
              icon={User}
              {...register('username', { required: 'Username is required', minLength: { value: 3, message: 'Minimum 3 characters' } })}
              error={errors.username?.message}
            />
            <Input
              label="Corporate / Personal Email"
              type="email"
              placeholder={activeTab === 'employer' ? 'alex@company.com' : 'alex@example.com'}
              icon={Mail}
              {...register('email', {
                required: 'Email address is required',
                pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email address' },
              })}
              error={errors.email?.message}
            />
            <Input
              label="Phone Number"
              type="tel"
              placeholder="+91 9876543210"
              icon={Phone}
              {...register('phone_number')}
              error={errors.phone_number?.message}
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••••••"
              icon={Lock}
              {...register('password', { required: 'Password is required', minLength: { value: 6, message: 'Minimum 6 characters' } })}
              error={errors.password?.message}
            />
            <Input
              label="Confirm Password"
              type="password"
              placeholder="••••••••••••"
              icon={Lock}
              {...register('passwordConfirm', {
                required: 'Please confirm your password',
                validate: (val) => val === passwordVal || 'Passwords do not match',
              })}
              error={errors.passwordConfirm?.message}
            />
            <Button type="submit" variant="primary" size="lg" isLoading={isSendingOtp} className="w-full mt-2">
              Continue — Verify Email
            </Button>
          </form>
        </>
      )}

      {/* ── STEP 2: OTP Verification ── */}
      {step === STEP.OTP && (
        <>
          {/* OTP icon */}
          <div className="flex items-center justify-center">
            <div className="w-16 h-16 rounded-full bg-wine-tint flex items-center justify-center">
              <ShieldCheck className="w-8 h-8 text-wine-deep" />
            </div>
          </div>

          {errorMessage && (
            <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={onVerifyOtp} className="space-y-4">
            {/* 6-digit OTP input */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-ink-muted">6-Digit OTP</label>
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                placeholder="Enter OTP"
                className="w-full text-center text-2xl font-mono tracking-[0.5em] bg-white border border-sand-border rounded-xl px-4 py-3 text-ink-charcoal focus:outline-none focus:border-wine-deep"
              />
              <p className="text-xs text-ink-muted text-center">OTP expires in 10 minutes</p>
            </div>

            <Button type="submit" variant="primary" size="lg" isLoading={isLoading} className="w-full">
              Verify & Create Account
            </Button>
          </form>

          <div className="flex items-center justify-between pt-1">
            <button
              type="button"
              onClick={() => { setStep(STEP.FORM); setOtp(''); setErrorMessage(''); }}
              className="text-xs text-ink-muted hover:text-wine-deep font-semibold"
            >
              ← Change Email
            </button>
            <button
              type="button"
              onClick={resendOtp}
              disabled={isSendingOtp}
              className="flex items-center gap-1 text-xs font-semibold text-wine-deep hover:text-wine-burgundy disabled:opacity-50"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              {isSendingOtp ? 'Sending...' : 'Resend OTP'}
            </button>
          </div>
        </>
      )}

      <div className="pt-4 border-t border-sand-border text-center text-xs text-ink-muted">
        Already registered on JobCrest?{' '}
        <Link to="/login" className="font-bold text-wine-deep hover:text-wine-burgundy hover:underline">
          Sign in here
        </Link>
      </div>
    </div>
  );
};

export default Register;
