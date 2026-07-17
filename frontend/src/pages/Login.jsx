import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Heart, Eye, EyeOff, ArrowRight, Shield, AlertCircle, User, Stethoscope } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/lib/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginNurse, loginPatient } = useAuth();

  const from = location.state?.from || '/roles';

  const [nurseForm, setNurseForm] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleNurseSubmit = async (e) => {
    e.preventDefault();
    if (!nurseForm.username || !nurseForm.password) {
      setError('Please fill in all fields.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await loginNurse({ username: nurseForm.username, password: nurseForm.password });
      navigate('/nurse/dashboard', { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Invalid username or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePatientSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginPatient();
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Failed to create session. Please try again.');
    } finally {
      setLoading(false);
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
            Choose how you'd like to sign in
          </p>
        </div>

        <div className="bg-card rounded-2xl border shadow-sm p-6 sm:p-8">
          <Tabs defaultValue="patient" onValueChange={() => setError('')}>
            <TabsList className="w-full mb-6">
              <TabsTrigger value="patient" className="flex-1 gap-2">
                <User className="w-4 h-4" /> Patient
              </TabsTrigger>
              <TabsTrigger value="nurse" className="flex-1 gap-2">
                <Stethoscope className="w-4 h-4" /> Nurse
              </TabsTrigger>
            </TabsList>

            <TabsContent value="patient">
              <form onSubmit={handlePatientSubmit} className="space-y-5">
                <p className="text-sm text-muted-foreground">
                  Continue anonymously with a secure session. No sign-up required.
                </p>

                {error && (
                  <div className="flex items-start gap-2 text-sm text-destructive bg-destructive/5 rounded-xl px-3 py-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    {error}
                  </div>
                )}

                <Button type="submit" className="w-full rounded-full gap-2" disabled={loading}>
                  {loading ? 'Creating session…' : <>Continue as Patient <ArrowRight className="w-4 h-4" /></>}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="nurse">
              <form onSubmit={handleNurseSubmit} className="space-y-5">
                <div className="space-y-1.5">
                  <Label htmlFor="nurse-username">Username</Label>
                  <Input
                    id="nurse-username"
                    type="text"
                    placeholder="nurse.demo"
                    value={nurseForm.username}
                    onChange={(e) => setNurseForm(f => ({ ...f, username: e.target.value }))}
                    autoComplete="username"
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="nurse-password">Password</Label>
                  </div>
                  <div className="relative">
                    <Input
                      id="nurse-password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={nurseForm.password}
                      onChange={(e) => setNurseForm(f => ({ ...f, password: e.target.value }))}
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
                  {loading ? 'Signing in…' : <>Sign in as Nurse <ArrowRight className="w-4 h-4" /></>}
                </Button>
              </form>
            </TabsContent>
          </Tabs>

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
