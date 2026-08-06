// ============================================================
// CodeWhisper PR - Login Page
// ============================================================

import React from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/router';
import { useAuth } from '../src/hooks/useAuth';
import Head from 'next/head';

interface LoginFormData {
  email: string;
  password: string;
}

export default function Login() {
  const router = useRouter();
  const { login } = useAuth();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    await login(data.email, data.password);
    router.replace('/dashboard');
  };

  return (
    <>
      <Head>
        <title>Login - CodeWhisper PR</title>
      </Head>
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="card w-full max-w-md">
          <h1 className="text-2xl font-bold text-white text-center mb-6">CodeWhisper PR</h1>
          <p className="text-center text-gray-400 mb-6">Sign in to your account</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
              <input
                type="email"
                placeholder="you@example.com"
                className="input"
                {...register('email', { required: 'Email is required', pattern: { value: /\S+@\S+\.\S+/, message: 'Invalid email' } })}
              />
              {errors.email && <p className="text-sm text-secondary-400 mt-1">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
              <input
                type="password"
                placeholder="••••••••"
                className="input"
                {...register('password', { required: 'Password is required' })}
              />
              {errors.password && <p className="text-sm text-secondary-400 mt-1">{errors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary w-full"
            >
              {isSubmitting ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-400 mt-4">
            Don't have an account?{' '}
            <a href="/register" className="text-primary-400 hover:text-primary-300">Sign up</a>
          </p>
        </div>
      </div>
    </>
  );
}
