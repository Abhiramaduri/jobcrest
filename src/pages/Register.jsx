import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { User, Mail, Lock, Phone, Briefcase, Building2, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

export const Register = () => {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialRole = searchParams.get('role') === 'employer' ? 'employer' : 'jobseeker';

  const [activeTab, setActiveTab] = useState(initialRole); // 'jobseeker' | 'employer'
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: {
      username: '',
      email: '',
      phone_number: '',
      password: '',
      passwordConfirm: '',
    },
  });

  const passwordVal = watch('password');

  const onSubmit = async (data) => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      const payload = {
        username: data.username,
        email: data.email,
        phone_number: data.phone_number,
        password: data.password,
        passwordConfirm: data.passwordConfirm,
        role: activeTab,
      };

      const user = await registerUser(payload);
      toast.success('Registration successful! Welcome to JobCrest.');

      if (activeTab === 'employer') {
        navigate('/employer/dashboard');
      } else {
        navigate('/profile');
      }
    } catch (err) {
      console.error('Registration error:', err);
      const res = err?.response?.data;
      let msg = 'Registration failed. Please check your information.';
      if (res) {
        if (typeof res === 'string') msg = res;
        else if (res.username) msg = `Username: ${res.username.join(' ')}`;
        else if (res.email) msg = `Email: ${res.email.join(' ')}`;
        else if (res.password) msg = `Password: ${res.password.join(' ')}`;
        else if (res.detail) msg = res.detail;
        else if (res.non_field_errors) msg = res.non_field_errors.join(' ');
      }
      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-md space-y-6">
      <div className="text-center space-y-1.5">
        <h2 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep">
          Join JobCrest
        </h2>
        <p className="text-xs sm:text-sm text-ink-muted">
          Choose your account type to get started
        </p>
      </div>

      {/* Dual Tab Role Switcher */}
      <div className="grid grid-cols-2 p-1.5 bg-sand-canvas border border-sand-border rounded-2xl">
        <button
          type="button"
          onClick={() => setActiveTab('jobseeker')}
          className={`flex items-center justify-center gap-2 py-2.5 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'jobseeker'
              ? 'bg-wine-deep text-white shadow-wine-sm'
              : 'text-ink-muted hover:text-wine-deep'
          }`}
        >
          <User className="w-4 h-4" />
          <span>I'm a Job Seeker</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('employer')}
          className={`flex items-center justify-center gap-2 py-2.5 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'employer'
              ? 'bg-wine-deep text-white shadow-wine-sm'
              : 'text-ink-muted hover:text-wine-deep'
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
          {...register('username', {
            required: 'Username is required',
            minLength: { value: 3, message: 'Minimum 3 characters' },
          })}
          error={errors.username?.message}
        />

        <Input
          label="Corporate / Personal Email"
          type="email"
          placeholder={activeTab === 'employer' ? 'alex@company.com' : 'alex@example.com'}
          icon={Mail}
          {...register('email', {
            required: 'Email address is required',
            pattern: {
              value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
              message: 'Invalid email address format',
            },
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
          {...register('password', {
            required: 'Password is required',
            minLength: { value: 6, message: 'Password must be at least 6 characters' },
          })}
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

        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isLoading}
          className="w-full mt-2"
        >
          Create {activeTab === 'employer' ? 'Employer' : 'Candidate'} Account
        </Button>
      </form>

      <div className="pt-4 border-t border-sand-border text-center text-xs text-ink-muted">
        Already registered on JobCrest?{' '}
        <Link
          to="/login"
          className="font-bold text-wine-deep hover:text-wine-burgundy hover:underline"
        >
          Sign in here
        </Link>
      </div>
    </div>
  );
};

export default Register;
