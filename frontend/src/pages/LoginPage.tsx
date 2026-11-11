import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldAlert, Lock, Mail, AlertCircle, ArrowRight, UserPlus, ShieldCheck } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md bg-slate-900/80 border border-slate-800 rounded-2xl p-8 shadow-2xl backdrop-blur relative z-10">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/25 mb-3">
            <ShieldAlert className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">FraudShield Enterprise</h1>
          <p className="text-xs text-slate-400 mt-1">Sign in to Fraud Intelligence & Operations Workbench</p>
        </div>

        {/* Public Visitor Notice */}
        <div className="mb-6 p-3 rounded-xl bg-cyan-950/40 border border-cyan-800/40 text-xs text-cyan-200/90 flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-white">Role-Based Access:</span>
            <p className="text-slate-300 text-[11px] mt-0.5">
              Administrators sign in here. New investigators and analysts can create an account via the registration portal.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-lg bg-red-950/80 border border-red-800/80 flex items-start gap-2.5 text-red-300 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Account Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@fraudshield.io"
                className="w-full pl-9 pr-4 py-2.5 bg-slate-950/80 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-4 py-2.5 bg-slate-950/80 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-sm rounded-lg shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In to Workbench'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-800/80 text-center text-xs text-slate-400 space-y-2">
          <div>Don't have an account?</div>
          <Link
            to="/register"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-cyan-400 hover:text-cyan-300 font-medium transition text-xs border border-slate-700"
          >
            <UserPlus className="w-3.5 h-3.5" /> Create Investigator / User Account
          </Link>
        </div>
      </div>
    </div>
  );
};
