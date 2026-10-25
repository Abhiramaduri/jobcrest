import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, User, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import toast from 'react-hot-toast';

export const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectPath = searchParams.get('redirect');

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const user = await login(data);
      toast.success(`Welcome back, ${user.username}!`);

      if (redirectPath) {
        navigate(redirectPath);
      } else if (user.user_type === 'employer') {
        navigate('/employer/dashboard');
      } else {
        navigate('/jobs');
      }
    } catch (err) {
      console.error('Login error:', err);
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.non_field_errors?.[0] ||
        'Invalid credentials. Please verify your username and password.';
      setErrorMessage(detail);
      toast.error(detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-sand-border p-6 sm:p-10 shadow-wine-md space-y-6">
      <div className="text-center space-y-1.5">
        <h2 className="font-display text-2xl sm:text-3xl font-extrabold text-wine-deep">
          Welcome to JobCrest
        </h2>
        <p className="text-xs sm:text-sm text-ink-muted">
          Access your executive hiring or career portal
        </p>
      </div>

      {errorMessage && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Username or Email"
          placeholder="your.username or email"
          icon={User}
          {...register('username', { required: 'Username or email is required' })}
          error={errors.username?.message}
        />

        <div className="space-y-1">
          <Input
            label="Password"
            type="password"
            placeholder="••••••••••••"
            icon={Lock}
            {...register('password', { required: 'Password is required' })}
            error={errors.password?.message}
          />
          <div className="flex justify-end pt-1">
            <Link
              to="/forgot-password"
              className="text-xs font-semibold text-wine-burgundy hover:text-wine-deep hover:underline"
            >
              Forgot password?
            </Link>
          </div>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isLoading}
          className="w-full mt-2"
        >
          Sign In to Account
        </Button>
      </form>

      <div className="pt-4 border-t border-sand-border text-center text-xs text-ink-muted">
        Don't have a JobCrest account yet?{' '}
        <Link
          to="/register"
          className="font-bold text-wine-deep hover:text-wine-burgundy hover:underline inline-flex items-center gap-0.5"
        >
          Create an account <ArrowRight className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
};

export default Login;
