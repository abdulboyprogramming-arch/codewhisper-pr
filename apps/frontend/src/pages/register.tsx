// ============================================================
// CodeWhisper PR - Register Page
// ============================================================

import React from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/router';
import { useAuth } from '../src/hooks/useAuth';
import Head from 'next/head';

interface RegisterFormData {
  email: string;
  username: string;
  fullName: string;
  password: string;
  confirmPassword: string;
}

export default function Register() {
  const router = useRouter();
  const { register } = useAuth();
  const { register: formRegister, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterFormData>();

  const onSubmit = async (data: RegisterFormData) => {
    if (data.password !== data.confirmPassword) {
      return;
    }
    await register({
      email: data.email,
      username: data.username,
      fullName: data.fullName,
      password: data.password,
    });
    router.replace('/login');
  };

  return (
    <>
      <Head>
        <title>Register - CodeWhisper PR</title>
      </Head>
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="card w-full max-w-md">
          <h1 className="text-2xl font-bold text-white text-center mb-2">CodeWhisper PR</h1>
          <p className="text-center text-gray-400 mb-6">Create your account</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
              <input
                type="email"
                placeholder="you@example.com"
                className="input"
                {...formRegister('email', { required: 'Email is required', pattern: { value: /\S+@\S+\.\S+/, message: 'Invalid email' } })}
              />
              {errors.email && <p className="text-sm text-secondary-400 mt-1">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Username</label>
              <input
                type="text"
                placeholder="johndoe"
                className="input"
                {...formRegister('username', { required: 'Username is required', minLength: 3 })}
              />
              {errors.username && <p className="text-sm text-secondary-400 mt-1">{errors.username.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Full Name</label>
              <input
                type="text"
                placeholder="John Doe"
                className="input"
                {...formRegister('fullName')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
              <input
                type="password"
                placeholder="••••••••"
                className="input"
                {...formRegister('password', { required: 'Password is required', minLength: 8 })}
              />
              {errors.password && <p className="text-sm text-secondary-400 mt-1">{errors.password.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Confirm Password</label>
              <input
                type="password"
                placeholder="••••••••"
                className="input"
                {...formRegister('confirmPassword', { required: 'Please confirm password' })}
              />
              {errors.confirmPassword && <p className="text-sm text-secondary-400 mt-1">{errors.confirmPassword.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary w-full"
            >
              {isSubmitting ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-400 mt-4">
            Already have an account?{' '}
            <a href="/login" className="text-primary-400 hover:text-primary-300">Sign in</a>
          </p>
        </div>
      </div>
    </>
  );
}
