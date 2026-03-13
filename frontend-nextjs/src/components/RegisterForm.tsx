'use client'

import { useState, type FormEvent } from 'react';
import { useAuthStore } from '@/stores/authStore';

interface RegisterFormProps {
  onSwitchToLogin?: () => void;
}

export function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationError, setValidationError] = useState('');
  const { register, isLoading, error, clearError } = useAuthStore();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    setValidationError('');

    if (!username.trim()) {
      setValidationError('Username is required');
      return;
    }

    if (username.length < 3) {
      setValidationError('Username must be at least 3 characters');
      return;
    }

    if (!password) {
      setValidationError('Password is required');
      return;
    }

    if (password.length < 6) {
      setValidationError('Password must be at least 6 characters');
      return;
    }

    if (password !== confirmPassword) {
      setValidationError('Passwords do not match');
      return;
    }

    try {
      await register(username, password);
    } catch (err) {
      console.error('Registration failed:', err);
    }
  };

  const handleInputChange = () => {
    if (error) clearError();
    if (validationError) setValidationError('');
  };

  const displayError = validationError || error;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-slate-700">
            Username
          </label>
          <input
            id="username"
            type="text"
            placeholder="Choose a username"
            value={username}
            onChange={(e) => {
              setUsername(e.target.value);
              handleInputChange();
            }}
            disabled={isLoading}
            required
            className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-black/5 focus:border-black disabled:bg-slate-50 disabled:cursor-not-allowed text-sm transition-all"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium text-slate-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            placeholder="Choose a password (min 6 characters)"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              handleInputChange();
            }}
            disabled={isLoading}
            required
            className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-black/5 focus:border-black disabled:bg-slate-50 disabled:cursor-not-allowed text-sm transition-all"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-700">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              handleInputChange();
            }}
            disabled={isLoading}
            required
            className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-black/5 focus:border-black disabled:bg-slate-50 disabled:cursor-not-allowed text-sm transition-all"
          />
        </div>

        {displayError && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
            {displayError}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !username.trim() || !password || !confirmPassword}
          className="w-full px-6 py-3 bg-black text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium text-sm"
        >
          {isLoading ? 'Creating account...' : 'Create account'}
        </button>

        {onSwitchToLogin && (
          <div className="text-center text-sm text-slate-600">
            Already have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="font-medium text-black hover:underline"
            >
              Sign in
            </button>
          </div>
        )}
      </form>
    </div>
  );
}