'use client'

import { useState, type FormEvent } from 'react';
import { useAuthStore } from '@/stores/authStore';

interface LoginFormProps {
  onSwitchToRegister?: () => void;
}

export function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error, clearError } = useAuthStore();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      return;
    }

    try {
      await login(username, password);
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleUsernameChange = (value: string) => {
    setUsername(value);
    if (error) clearError();
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (error) clearError();
  };

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
            placeholder="Enter your username"
            value={username}
            onChange={(e) => handleUsernameChange(e.target.value)}
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
            placeholder="Enter your password"
            value={password}
            onChange={(e) => handlePasswordChange(e.target.value)}
            disabled={isLoading}
            required
            className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-black/5 focus:border-black disabled:bg-slate-50 disabled:cursor-not-allowed text-sm transition-all"
          />
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !username.trim() || !password.trim()}
          className="w-full px-6 py-3 bg-black text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium text-sm"
        >
          {isLoading ? 'Signing in...' : 'Sign in'}
        </button>

        {onSwitchToRegister && (
          <div className="text-center text-sm text-slate-600">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToRegister}
              className="font-medium text-black hover:underline"
            >
              Create account
            </button>
          </div>
        )}
      </form>
    </div>
  );
}