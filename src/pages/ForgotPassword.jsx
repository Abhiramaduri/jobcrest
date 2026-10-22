import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle2 } from 'lucide-react';
import authApi from '../api/authApi';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

export const ForgotPassword = () => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await authApi.passwordReset(data.email);
      setIsSubmitted(true);
      toast.success('Reset instructions dispatched');
    } catch {
      toast.error('Unable to send reset instructions');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-md space-y-6">
      <div className="text-center space-y-1.5">
        <h2 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep">
          Reset Password
        </h2>
        <p className="text-xs sm:text-sm text-ink-muted">
          Enter your registered email address to receive reset instructions
        </p>
      </div>

      {isSubmitted ? (
        <div className="p-6 bg-sand-canvas/50 border border-sand-border rounded-2xl text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-wine-tint text-wine-deep flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="font-display text-lg font-bold text-ink-charcoal">
            Instructions Sent
          </h3>
          <p className="text-xs text-ink-muted leading-relaxed">
            If an account is associated with that email address, you will receive a secure password reset link shortly.
          </p>
          <div className="pt-2">
            <Link to="/login">
              <Button variant="outline" size="sm" className="w-full">
                Return to Login
              </Button>
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            placeholder="you@example.com"
            icon={Mail}
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Invalid email address format',
              },
            })}
            error={errors.email?.message}
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            className="w-full mt-2"
          >
            Send Reset Instructions
          </Button>

          <div className="pt-3 text-center">
            <Link
              to="/login"
              className="inline-flex items-center gap-1 text-xs font-semibold text-ink-muted hover:text-wine-deep"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Sign In
            </Link>
          </div>
        </form>
      )}
    </div>
  );
};

export default ForgotPassword;
