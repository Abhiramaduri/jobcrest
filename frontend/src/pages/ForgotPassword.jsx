import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle2, ShieldCheck, Lock, AlertCircle, RefreshCw } from 'lucide-react';
import authApi from '../api/authApi';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

const STEP = { EMAIL: 'email', OTP: 'otp', NEW_PASSWORD: 'new_password', DONE: 'done' };

export const ForgotPassword = () => {
  const [step, setStep] = useState(STEP.EMAIL);
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const {
    register: registerEmail,
    handleSubmit: handleEmailSubmit,
    formState: { errors: emailErrors },
  } = useForm();

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    watch,
    formState: { errors: passwordErrors },
  } = useForm();

  const newPasswordVal = watch('new_password');

  // ── Step 1: Request OTP ──
  const onRequestOtp = async (data) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      await authApi.passwordReset(data.email);
      setEmail(data.email);
      setStep(STEP.OTP);
      toast.success(`OTP sent to ${data.email}`);
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Unable to send OTP. Please try again.';
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  // ── Step 2: Verify OTP ──
  const onVerifyOtp = async (e) => {
    e.preventDefault();
    if (otp.length !== 6) {
      toast.error('Please enter the 6-digit OTP.');
      return;
    }
    setIsLoading(true);
    setErrorMessage('');
    try {
      await authApi.passwordResetVerifyOtp({ email, otp });
      setStep(STEP.NEW_PASSWORD);
      toast.success('OTP verified! Set your new password.');
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Invalid OTP. Please try again.';
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  // ── Step 3: Set New Password ──
  const onSetPassword = async (data) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      await authApi.passwordResetConfirm({
        email,
        otp,
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      });
      setStep(STEP.DONE);
      toast.success('Password reset successfully!');
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Failed to reset password. Please try again.';
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const resendOtp = async () => {
    setIsLoading(true);
    try {
      await authApi.passwordReset(email);
      toast.success('New OTP sent!');
    } catch {
      toast.error('Could not resend OTP.');
    } finally {
      setIsLoading(false);
    }
  };

  const stepTitles = {
    [STEP.EMAIL]: { title: 'Reset Password', sub: 'Enter your registered email to receive an OTP' },
    [STEP.OTP]: { title: 'Enter OTP', sub: `We sent a 6-digit code to ${email}` },
    [STEP.NEW_PASSWORD]: { title: 'New Password', sub: 'Choose a strong new password for your account' },
    [STEP.DONE]: { title: 'Password Reset!', sub: 'Your password has been updated successfully' },
  };

  return (
    <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-md space-y-6">
      {/* Header */}
      <div className="text-center space-y-1.5">
        <h2 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep">
          {stepTitles[step].title}
        </h2>
        <p className="text-xs sm:text-sm text-ink-muted">{stepTitles[step].sub}</p>
      </div>

      {/* Progress indicator */}
      {step !== STEP.DONE && (
        <div className="flex items-center gap-2">
          {[STEP.EMAIL, STEP.OTP, STEP.NEW_PASSWORD].map((s, i) => (
            <React.Fragment key={s}>
              <div className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-all ${
                step === s ? 'bg-wine-deep text-white' :
                [STEP.OTP, STEP.NEW_PASSWORD, STEP.DONE].indexOf(step) > i ? 'bg-wine-tint text-wine-deep' :
                'bg-sand-canvas text-ink-muted border border-sand-border'
              }`}>
                {i + 1}
              </div>
              {i < 2 && <div className="flex-1 h-px bg-sand-border" />}
            </React.Fragment>
          ))}
        </div>
      )}

      {errorMessage && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* ── Step 1: Email ── */}
      {step === STEP.EMAIL && (
        <form onSubmit={handleEmailSubmit(onRequestOtp)} className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            placeholder="you@example.com"
            icon={Mail}
            {...registerEmail('email', {
              required: 'Email is required',
              pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email address' },
            })}
            error={emailErrors.email?.message}
          />
          <Button type="submit" variant="primary" size="lg" isLoading={isLoading} className="w-full mt-2">
            Send OTP
          </Button>
          <div className="pt-1 text-center">
            <Link to="/login" className="inline-flex items-center gap-1 text-xs font-semibold text-ink-muted hover:text-wine-deep">
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Sign In
            </Link>
          </div>
        </form>
      )}

      {/* ── Step 2: OTP ── */}
      {step === STEP.OTP && (
        <>
          <div className="flex items-center justify-center">
            <div className="w-16 h-16 rounded-full bg-wine-tint flex items-center justify-center">
              <ShieldCheck className="w-8 h-8 text-wine-deep" />
            </div>
          </div>
          <form onSubmit={onVerifyOtp} className="space-y-4">
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
              Verify OTP
            </Button>
          </form>
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => { setStep(STEP.EMAIL); setOtp(''); setErrorMessage(''); }}
              className="text-xs text-ink-muted hover:text-wine-deep font-semibold"
            >
              ← Change Email
            </button>
            <button
              type="button"
              onClick={resendOtp}
              disabled={isLoading}
              className="flex items-center gap-1 text-xs font-semibold text-wine-deep hover:text-wine-burgundy disabled:opacity-50"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              {isLoading ? 'Sending...' : 'Resend OTP'}
            </button>
          </div>
        </>
      )}

      {/* ── Step 3: New Password ── */}
      {step === STEP.NEW_PASSWORD && (
        <form onSubmit={handlePasswordSubmit(onSetPassword)} className="space-y-4">
          <Input
            label="New Password"
            type="password"
            placeholder="••••••••••••"
            icon={Lock}
            {...registerPassword('new_password', {
              required: 'New password is required',
              minLength: { value: 8, message: 'Minimum 8 characters' },
            })}
            error={passwordErrors.new_password?.message}
          />
          <Input
            label="Confirm New Password"
            type="password"
            placeholder="••••••••••••"
            icon={Lock}
            {...registerPassword('confirm_password', {
              required: 'Please confirm your password',
              validate: (val) => val === newPasswordVal || 'Passwords do not match',
            })}
            error={passwordErrors.confirm_password?.message}
          />
          <Button type="submit" variant="primary" size="lg" isLoading={isLoading} className="w-full">
            Reset Password
          </Button>
        </form>
      )}

      {/* ── Step 4: Done ── */}
      {step === STEP.DONE && (
        <div className="p-6 bg-sand-canvas/50 border border-sand-border rounded-2xl text-center space-y-4">
          <div className="w-14 h-14 rounded-full bg-wine-tint text-wine-deep flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <p className="text-xs text-ink-muted leading-relaxed">
            Your password has been reset. You can now sign in with your new password.
          </p>
          <Link to="/login">
            <Button variant="primary" size="sm" className="w-full">
              Sign In Now
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
};

export default ForgotPassword;
