import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Heart, Eye, EyeOff, ArrowRight, Shield, AlertCircle, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/lib/AuthContext';
import { getMe } from '@/api/apiClient';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginNurse, loginPatient, login, setUser, setIsAuthenticated, user } = useAuth();

  const [form, setForm] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [anonymousLoading, setAnonymousLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) {
      setError('Please fill in all fields.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      let loggedInUser = await login({ username: form.username, password: form.password });
      // Safety net: if a legacy/stale token didn't carry gender, try to recover via getMe
      if (loggedInUser.role !== 'nurse' && !loggedInUser.gender) {
        try {
          const meData = await getMe();
          if (meData?.gender) {
            const updatedUser = { ...loggedInUser, gender: meData.gender };
            loggedInUser = updatedUser;
            localStorage.setItem('nurucare_patient', JSON.stringify(updatedUser));
            setUser(updatedUser);
          }
        } catch (e) {
          console.warn('Could not fetch user details via getMe', e);
        }
      }
      // Route based on role and gender
      if (loggedInUser.role === 'nurse') {
        navigate('/nurse/dashboard', { replace: true });
      } else if (loggedInUser.role === 'admin') {
        navigate('/admin/dashboard', { replace: true });
      } else if (loggedInUser.gender === 'female') {
        navigate('/patient/female/dashboard', { replace: true });
      } else if (loggedInUser.gender === 'male') {
        navigate('/patient/male/dashboard', { replace: true });
      } else {
        // Incomplete profile (e.g. legacy account with no gender) — continue through
        // the role/intake flow so the user can finish onboarding.
        navigate(location.state?.from || '/roles', { replace: true });
      }
    } catch (err) {
      // Fallback to loginNurse if needed
      try {
        await loginNurse({ username: form.username, password: form.password });
        navigate('/nurse/dashboard', { replace: true });
      } catch (nurseErr) {
        setError(err.response?.data?.detail || err.message || 'Invalid username or password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAnonymousLogin = async (e) => {
    e.preventDefault();
    setError('');
    setAnonymousLoading(true);
    try {
      await loginPatient();
      navigate(location.state?.from || '/roles', { replace: true });
    } catch (err) {
      setError(err.message || 'Failed to create session. Please try again.');
    } finally {
      setAnonymousLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-4">
            <Heart className="w-7 h-7 text-accent" />
          </div>
          <h1 className="font-heading font-bold text-2xl">Welcome back</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Sign in to continue your health journey
          </p>
        </div>

        <div className="bg-card rounded-2xl border shadow-sm p-6 sm:p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="nurse.demo"
                value={form.username}
                onChange={(e) => setForm(f => ({ ...f, username: e.target.value }))}
                autoComplete="username"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))}
                  autoComplete="current-password"
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="flex items-start gap-2 text-sm text-destructive bg-destructive/5 rounded-xl px-3 py-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                {error}
              </div>
            )}

            <Button type="submit" className="w-full rounded-full gap-2" disabled={loading}>
              {loading ? 'Signing in…' : <>Sign in <ArrowRight className="w-4 h-4" /></>}
            </Button>

            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">Or continue as</span>
              </div>
            </div>

            <Button type="button" variant="outline" className="w-full rounded-full gap-2" onClick={handleAnonymousLogin} disabled={anonymousLoading}>
              {anonymousLoading ? 'Creating session…' : <> <User className="w-4 h-4" /> Anonymous Patient</>}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Don't have an account?{' '}
            <Link to="/signup" className="text-primary font-medium hover:underline">
              Create one
            </Link>
          </p>
        </div>

        <p className="text-xs text-center text-muted-foreground mt-4">
          <Shield className="w-3 h-3 inline mr-1" />
          Your data is encrypted and protected under Kenya's Data Protection Act 2019.
        </p>
      </motion.div>
    </div>
  );
}
