import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, Eye, EyeOff, ArrowRight, Shield, X, CheckCircle, AlertCircle, User, Stethoscope } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/lib/AuthContext';

// ─── Consent Modal ────────────────────────────────────────────────────────────
function ConsentModal({ onAccept, onDecline }) {
  const [scrolledToBottom, setScrolledToBottom] = useState(false);

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (scrollHeight - scrollTop - clientHeight < 40) {
      setScrolledToBottom(true);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-card rounded-2xl border shadow-xl w-full max-w-lg flex flex-col max-h-[90vh]"
      >
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Shield className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="font-heading font-bold text-lg leading-tight">Data Consent & Privacy Notice</h2>
            <p className="text-xs text-muted-foreground mt-0.5">Please read carefully before continuing</p>
          </div>
        </div>

        {/* Scrollable body */}
        <div
          onScroll={handleScroll}
          className="overflow-y-auto flex-1 p-6 space-y-5 text-sm leading-relaxed"
        >
          <p className="text-muted-foreground">
            NuruCare collects and processes certain personal and health-related information to provide you
            with personalised reproductive health guidance. By creating an account you agree to the
            following terms regarding your data.
          </p>

          <section>
            <h3 className="font-semibold mb-1">What data we collect</h3>
            <ul className="list-disc list-inside text-muted-foreground space-y-1">
              <li>Name, age, and contact email</li>
              <li>Reproductive and menstrual health information you enter during intake</li>
              <li>Blood pressure and other biometric data you provide</li>
              <li>Conversation history with our AI health assistant</li>
              <li>Session metadata (timestamps, device type)</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold mb-1">How we use your data</h3>
            <ul className="list-disc list-inside text-muted-foreground space-y-1">
              <li>To generate personalised contraceptive recommendations</li>
              <li>To enable partner-sync features when you consent to share</li>
              <li>To help healthcare providers (nurses) look up your session with your permission</li>
              <li>To improve NuruCare's AI models using anonymised, aggregated data</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold mb-1">Data sharing</h3>
            <p className="text-muted-foreground">
              Your identifiable data is <strong>never sold</strong> to third parties. De-identified
              data may be used for research in accordance with applicable health-data regulations
              (Kenya's Data Protection Act 2019). Healthcare providers can only access your record
              using a session key <em>you</em> generate and share.
            </p>
          </section>

          <section>
            <h3 className="font-semibold mb-1">Your rights</h3>
            <ul className="list-disc list-inside text-muted-foreground space-y-1">
              <li>Access or download a copy of your data at any time</li>
              <li>Request correction of inaccurate information</li>
              <li>Request deletion of your account and all associated data</li>
              <li>Withdraw consent — this will disable personalised features</li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold mb-1">Data security</h3>
            <p className="text-muted-foreground">
              All health data is encrypted in transit (TLS 1.3) and at rest (AES-256). Session keys
              expire after 15 minutes and are single-use.
            </p>
          </section>

          <p className="text-muted-foreground text-xs">
            For questions contact <span className="text-primary">privacy@nurucare.org</span>.
            Last updated: June 2026.
          </p>

          {!scrolledToBottom && (
            <p className="text-xs text-center text-muted-foreground animate-pulse pt-2">
              ↓ Scroll to the bottom to continue
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="p-6 border-t flex gap-3">
          <Button
            variant="outline"
            className="flex-1 rounded-full"
            onClick={onDecline}
          >
            <X className="w-4 h-4 mr-2" /> Decline
          </Button>
          <Button
            className="flex-1 rounded-full"
            disabled={!scrolledToBottom}
            onClick={onAccept}
          >
            <CheckCircle className="w-4 h-4 mr-2" /> I Agree
          </Button>
        </div>
      </motion.div>
    </div>
  );
}

// ─── Sign Up Page ─────────────────────────────────────────────────────────────
export default function SignUp() {
  const navigate = useNavigate();
  const { signUp, loginNurse, loginPatient } = useAuth();

  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [role, setRole] = useState('patient'); // 'patient' or 'nurse'
  const [showPassword, setShowPassword] = useState(false);
  const [showConsent, setShowConsent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const validate = () => {
    if (role === 'patient' && !form.name.trim()) return 'Please enter your name.';
    if (role === 'patient' && !form.email.includes('@')) return 'Please enter a valid email address.';
    if (form.password.length < 8) return 'Password must be at least 8 characters.';
    if (form.password !== form.confirm) return 'Passwords do not match.';
    return null;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const err = validate();
    if (err) { setError(err); return; }
    setError('');
    if (role === 'patient') {
      setShowConsent(true);
    } else {
      handleConsentAccept(); // Nurses can skip consent for now (since they are using demo accounts)
    }
  };

  const handleConsentAccept = async () => {
    setShowConsent(false);
    setLoading(true);
    try {
      if (role === 'nurse') {
        // For nurses, we'll just do loginNurse since we have hardcoded accounts
        await loginNurse({ username: form.email, password: form.password });
        navigate('/nurse/dashboard');
      } else {
        await signUp({ name: form.name, email: form.email, password: form.password, consentGiven: true });
        navigate('/roles');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Sign up failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <AnimatePresence>
        {showConsent && (
          <ConsentModal
            onAccept={handleConsentAccept}
            onDecline={() => setShowConsent(false)}
          />
        )}
      </AnimatePresence>

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
            <h1 className="font-heading font-bold text-2xl">Create your account</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Your health journey starts here. Your data stays yours.
            </p>
          </div>

          <div className="bg-card rounded-2xl border shadow-sm p-6 sm:p-8">
            <Tabs defaultValue="patient" value={role} onValueChange={setRole} className="w-full">
              <TabsList className="w-full mb-6">
                <TabsTrigger value="patient" className="flex-1 gap-2">
                  <User className="w-4 h-4" /> Patient
                </TabsTrigger>
                <TabsTrigger value="nurse" className="flex-1 gap-2">
                  <Stethoscope className="w-4 h-4" /> Nurse
                </TabsTrigger>
              </TabsList>

              <TabsContent value="patient">
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="space-y-1.5">
                    <Label htmlFor="name">Full name</Label>
                    <Input
                      id="name"
                      placeholder="Amina Wanjiru"
                      value={form.name}
                      onChange={set('name')}
                      autoComplete="name"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="email">Email address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={form.email}
                      onChange={set('email')}
                      autoComplete="email"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="password">Password</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Min. 8 characters"
                        value={form.password}
                        onChange={set('password')}
                        autoComplete="new-password"
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

                  <div className="space-y-1.5">
                    <Label htmlFor="confirm">Confirm password</Label>
                    <Input
                      id="confirm"
                      type="password"
                      placeholder="Re-enter password"
                      value={form.confirm}
                      onChange={set('confirm')}
                      autoComplete="new-password"
                    />
                  </div>

                  {error && (
                    <div className="flex items-start gap-2 text-sm text-destructive bg-destructive/5 rounded-xl px-3 py-2">
                      <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      {error}
                    </div>
                  )}

                  <Button type="submit" className="w-full rounded-full gap-2" disabled={loading}>
                    {loading ? 'Creating account…' : <>Continue <ArrowRight className="w-4 h-4" /></>}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="nurse">
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="space-y-1.5">
                    <Label htmlFor="nurse-username">Username</Label>
                    <Input
                      id="nurse-username"
                      placeholder="nurse.demo"
                      value={form.email}
                      onChange={set('email')}
                      autoComplete="username"
                    />
                    <p className="text-xs text-muted-foreground mt-1">Demo: nurse.demo / NuruCare2026</p>
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="nurse-password">Password</Label>
                    <div className="relative">
                      <Input
                        id="nurse-password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={form.password}
                        onChange={set('password')}
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
              Already have an account?{' '}
              <Link to="/login" className="text-primary font-medium hover:underline">
                Sign in
              </Link>
            </p>
          </div>

          <p className="text-xs text-center text-muted-foreground mt-4">
            <Shield className="w-3 h-3 inline mr-1" />
            Your data is encrypted and protected under Kenya's Data Protection Act 2019.
          </p>
        </motion.div>
      </div>
    </>
  );
}
