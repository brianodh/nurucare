import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
  Heart,
  TrendingUp,
  BookOpen,
  Users,
  Calendar,
  Activity,
  CheckCircle2,
  ChevronRight,
  ChevronDown,
  Stethoscope,
  Plus,
  AlertCircle,
  User,
  Info,
  RefreshCw,
  AlertTriangle,
  XCircle,
  Link2,
  Pill,
  ShieldCheck,
  ArrowRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useAuth } from '@/lib/AuthContext';
import { useLang } from '@/lib/i18n.jsx';
import NotificationCenter from './components/NotificationCenter';
import PartnerSummary from './components/PartnerSummary';
import OnboardingTour from './components/OnboardingTour';
import { useToast } from '@/components/ui/use-toast';
import {
  getPatientProfile,
  updatePatientProfile,
  appendSideEffect,
  verifySyncToken,
  computeSafetyScore,
} from '@/api/apiClient';
import { loadProgress, getSavedResults } from '@/lib/useProgress';

const TOUR_STORAGE_KEY = 'patient_onboarded';

const COMMON_SIDE_EFFECTS = [
  'Nausea',
  'Headache',
  'Breakthrough bleeding',
  'Breast tenderness',
  'Mood changes',
  'Acne',
  'Weight gain',
  'Abdominal pain',
  'Dizziness',
];

const FEMALE_EDUCATION = [
  {
    title: 'Contraceptive Methods',
    description:
      'Learn about all available contraceptive options and find what works best for you based on your WHO MEC profile.',
    icon: BookOpen,
    color: 'bg-pink-100 text-pink-700 dark:bg-pink-900/20 dark:text-pink-300',
  },
  {
    title: 'Cycle Tracking',
    description:
      'Understand your menstrual cycle, recognise fertile windows and spot changes that may need a provider check.',
    icon: Calendar,
    color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300',
  },
  {
    title: 'Healthy Relationships',
    description:
      'Practical tips for communicating about contraception with your partner and negotiating shared decisions.',
    icon: Heart,
    color: 'bg-rose-100 text-rose-700 dark:bg-rose-900/20 dark:text-rose-300',
  },
  {
    title: 'General Wellness',
    description:
      'Lifestyle guidance that supports good reproductive health, including nutrition, movement and sleep.',
    icon: Activity,
    color: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300',
  },
];

const MALE_EDUCATION = [
  {
    title: 'Contraception Basics',
    description:
      'Learn the contraceptive options that involve or affect you — condoms, vasectomy, partner methods and effectiveness.',
    icon: BookOpen,
    color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300',
  },
  {
    title: 'Vasectomy Info',
    description:
      'What vasectomy is, how the no-scalpel procedure works, recovery and when it becomes effective.',
    icon: Stethoscope,
    color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300',
  },
  {
    title: 'Healthy Relationships',
    description:
      'Tips for communicating openly about contraception with your partner and making decisions together.',
    icon: Heart,
    color: 'bg-pink-100 text-pink-700 dark:bg-pink-900/20 dark:text-pink-300',
  },
  {
    title: 'General Wellness',
    description:
      'Lifestyle factors (diet, sleep, movement, smoking) that impact your cardiovascular and reproductive health.',
    icon: Activity,
    color: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300',
  },
];

const VASECTOMY_MYTHS = [
  {
    myth: 'Vasectomy affects masculinity or sexual performance',
    fact:
      'Vasectomy only blocks sperm transport. It does not affect hormone levels, libido, erection, or ejaculation.',
  },
  {
    myth: 'Vasectomy is permanent and cannot be reversed',
    fact:
      "Vasectomy reversal is possible, though success varies by time since the procedure. It's best treated as permanent with reversal as a possibility.",
  },
  {
    myth: 'Vasectomy protects against STIs',
    fact:
      'Vasectomy only prevents pregnancy. Condoms or other barrier methods are still required for STI protection.',
  },
  {
    myth: 'Recovery is long and painful',
    fact:
      'Modern no-scalpel vasectomy is minimally invasive. Most men return to light activities within 1–3 days.',
  },
];

const SEVERITY_OPTIONS = ['mild', 'moderate', 'severe'];

const SCORE_COLOURS = {
  low: { ring: 'stroke-[hsl(var(--success)_/_1)]', text: 'text-emerald-600', fill: 'bg-emerald-600' },
  medium: { ring: 'stroke-amber-500', text: 'text-amber-600', fill: 'bg-amber-500' },
  high: { ring: 'stroke-destructive', text: 'text-destructive', fill: 'bg-destructive' },
};

const RISK_BADGE = {
  low: { variant: 'secondary', label: 'Low risk' },
  medium: { variant: 'outline', label: 'Medium risk' },
  high: { variant: 'destructive', label: 'High risk' },
};

function formatMemberSince(createdAt) {
  if (!createdAt) return 'Not available';
  try {
    const d = new Date(createdAt);
    if (Number.isNaN(d.getTime())) return 'Not available';
    return d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  } catch {
    return 'Not available';
  }
}

function timeAgo(iso) {
  if (!iso) return null;
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return null;
  const diff = Date.now() - then;
  const min = Math.round(diff / 60000);
  if (min < 1) return 'just now';
  if (min < 60) return `${min}m ago`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h ago`;
  const day = Math.round(hr / 24);
  return `${day}d ago`;
}

function computeMilestones({ profile, partnerConnected, gender }) {
  const hasIntake =
    !!profile && Object.keys(profile).length > 0 && (profile.age > 0 || profile.confidence_score);

  const items = [];
  items.push({
    id: 'intake',
    title: 'Complete Health Assessment',
    progress: hasIntake ? 100 : 0,
    completed: !!hasIntake,
  });
  items.push({
    id: 'education',
    title: 'Review Personalised Education',
    progress: hasIntake ? 50 : 0,
    completed: false,
  });
  items.push({
    id: 'partner',
    title: gender === 'male' ? 'Connect with Partner' : 'Share with Partner',
    progress: partnerConnected ? 100 : 0,
    completed: !!partnerConnected,
  });
  return items;
}

function buildTimeline({ profile, progress, partnerConnected }) {
  const events = [];
  const intakeCreatedAt = profile?.created_at || progress?.completedAt || progress?.savedAt;
  if (intakeCreatedAt) {
    events.push({
      id: 'intake-complete',
      icon: CheckCircle2,
      color: 'text-emerald-600',
      action: 'Completed health assessment',
      time: intakeCreatedAt,
    });
  }
  const sideEffects = Array.isArray(profile?.side_effects) ? profile.side_effects : [];
  for (const entry of sideEffects.slice().reverse()) {
    events.push({
      id: `se-${entry.id || entry.logged_at || entry.started_on}`,
      icon: Pill,
      color: 'text-indigo-600',
      action: `Logged side effect: ${entry.symptom || '—'} (${entry.severity || 'mild'})`,
      time: entry.logged_at || entry.started_on,
    });
  }
  if (partnerConnected) {
    events.push({
      id: 'partner-linked',
      icon: Users,
      color: 'text-sky-600',
      action: 'Connected partner profile',
      time: new Date().toISOString(),
    });
  }
  events.sort((a, b) => new Date(b.time) - new Date(a.time));
  return events;
}

export default function PatientDashboard() {
  const { user } = useAuth();
  const { t } = useLang();
  const { toast } = useToast();
  const navigate = useNavigate();

  const gender = user?.gender || null;

  // ── Data loading state ───────────────────────────────────────────────────
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [profile, setProfile] = useState(null);      // raw profile row from DB
  const [recommendations, setRecommendations] = useState({
    recommended: null,
    restricted: null,
    general_advice: null,
  });
  const [progressSnapshot, setProgressSnapshot] = useState(null);

  // ── Notifications (static reminders until backend notifications table) ──
  const [notifications, setNotifications] = useState(() => buildStaticNotifs({ gender }));

  // ── Onboarding tour ─────────────────────────────────────────────────────
  const [showTour, setShowTour] = useState(false);
  const [tourStep, setTourStep] = useState(0);

  // ── Partner sync ────────────────────────────────────────────────────────
  const [partnerToken, setPartnerToken] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [partnerProfile, setPartnerProfile] = useState(null);
  const [partnerLoadError, setPartnerLoadError] = useState(null);

  // ── Side effects ────────────────────────────────────────────────────────
  const [newSideEffect, setNewSideEffect] = useState({
    symptom: '',
    severity: 'mild',
    started_on: new Date().toISOString().slice(0, 10),
    notes: '',
    method: '',
  });
  const [sideEffectSubmitting, setSideEffectSubmitting] = useState(false);

  // ── Fetch profile on mount ──────────────────────────────────────────────
  const fetchProfile = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const res = await getPatientProfile();
      setProfile(res.profile || null);

      const results = getSavedResults();
      if (results) {
        setRecommendations({
          recommended:
            (Array.isArray(results.recommended_methods) && results.recommended_methods.length
              ? results.recommended_methods
              : res.profile?.allowed_methods) || null,
          restricted:
            (Array.isArray(results.restricted_methods) && results.restricted_methods.length
              ? results.restricted_methods
              : res.profile?.restricted_methods) || null,
          general_advice: results.general_advice || null,
        });
      } else {
        setRecommendations({
          recommended: res.profile?.allowed_methods || null,
          restricted: res.profile?.restricted_methods || null,
          general_advice: null,
        });
      }

      setProgressSnapshot(loadProgress() || null);
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'Could not load your profile.';
      setLoadError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();

    try {
      const seen = localStorage.getItem(TOUR_STORAGE_KEY);
      if (!seen) setShowTour(true);
    } catch {}
  }, [fetchProfile]);

  // ── Computed data (never hardcoded display numbers) ────────────────────
  const computed = useMemo(() => {
    // If the backend returned safety_score, use it; otherwise compute identically client-side.
    const backendScore = profile?.safety_score;
    const score =
      backendScore && typeof backendScore.score === 'number'
        ? backendScore
        : computeSafetyScore(profile || {});
    const milestones = computeMilestones({
      profile,
      partnerConnected: !!partnerProfile,
      gender,
    });
    const timeline = buildTimeline({ profile, progress: progressSnapshot, partnerConnected: !!partnerProfile });
    const sideEffects = Array.isArray(profile?.side_effects) ? profile.side_effects : [];
    return { score, milestones, timeline, sideEffects };
  }, [profile, partnerProfile, progressSnapshot, gender]);

  const markAllRead = () => setNotifications((ns) => ns.map((n) => ({ ...n, read: true })));
  const markRead = (id) =>
    setNotifications((ns) => ns.map((n) => (n.id === id ? { ...n, read: true } : n)));
  const clearAll = () => setNotifications([]);
  const completeTour = () => {
    try {
      localStorage.setItem(TOUR_STORAGE_KEY, 'true');
    } catch {}
    setShowTour(false);
  };

  // ── Partner connect handler ─────────────────────────────────────────────
  const handleVerifyPartner = async () => {
    const trimmed = partnerToken.trim();
    if (!trimmed) return;
    setConnecting(true);
    setPartnerLoadError(null);
    try {
      const result = await verifySyncToken(trimmed);
      if (result.success) {
        const realPartner = result.partner_profile || null;
        if (!realPartner) {
          // Partner token redeemed successfully but their profile row is empty or couldn't be loaded.
          setPartnerLoadError('Partner token accepted, but partner profile is empty.');
          toast({
            title: 'Token used',
            description: 'Partner profile has no intake data yet — please ask them to complete intake.',
          });
        } else {
          setPartnerProfile(realPartner);
          toast({
            title: 'Partner connected!',
            description: 'You can now share health decisions together.',
          });
        }
      }
    } catch (err) {
      const msg =
        err?.response?.data?.detail || err.message || 'Invalid or expired token.';
      setPartnerLoadError(msg);
      toast({
        title: 'Could not connect',
        description: msg,
        variant: 'destructive',
      });
    } finally {
      setConnecting(false);
    }
  };

  // ── Side effects handler ────────────────────────────────────────────────
  const submitSideEffect = async () => {
    if (!newSideEffect.symptom.trim()) return;
    setSideEffectSubmitting(true);
    try {
      const res = await appendSideEffect({ ...newSideEffect });
      setProfile((p) => ({ ...(p || {}), side_effects: res.side_effects }));
      setNewSideEffect({
        symptom: '',
        severity: 'mild',
        started_on: new Date().toISOString().slice(0, 10),
        notes: '',
        method: '',
      });
      toast({
        title: 'Logged',
        description: 'Your side-effect entry has been saved.',
      });
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'Could not save entry.';
      toast({ title: 'Error', description: msg, variant: 'destructive' });
    } finally {
      setSideEffectSubmitting(false);
    }
  };

  const educationCards = gender === 'male' ? MALE_EDUCATION : FEMALE_EDUCATION;
  const colours = SCORE_COLOURS[computed.score.risk_level] || SCORE_COLOURS.medium;
  const badgeDef = RISK_BADGE[computed.score.risk_level] || RISK_BADGE.medium;

  // ── Loading / error / no profile states ─────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-[85vh] py-16 px-4 flex items-center justify-center">
        <div className="text-center space-y-3">
          <RefreshCw className="w-10 h-10 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Loading your dashboard…</p>
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="min-h-[85vh] py-16 px-4 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <XCircle className="w-5 h-5 text-destructive" /> Couldn't load your dashboard
            </CardTitle>
            <CardDescription>{loadError}</CardDescription>
          </CardHeader>
          <CardFooter className="flex gap-3 justify-end">
            <Link to="/female/intake">
              <Button variant="outline">Go to Intake</Button>
            </Link>
            <Button onClick={fetchProfile}>Retry</Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // If profile is genuinely empty/null, guide the user back through intake.
  const hasAnyIntakeData =
    !!profile && (profile.age > 0 || profile.confidence_score || profile.allowed_methods);

  if (!hasAnyIntakeData) {
    return (
      <div className="min-h-[85vh] py-16 px-4 flex items-center justify-center">
        <Card className="w-full max-w-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="w-5 h-5 text-primary" /> Complete your health assessment
            </CardTitle>
            <CardDescription>
              Your dashboard will populate once you've finished your health intake. You'll see a
              personalised safety score, method recommendations and partner-sync options.
            </CardDescription>
          </CardHeader>
          <CardFooter className="justify-end gap-2">
            <Button
              variant="secondary"
              asChild
            >
              <Link to={gender === 'male' ? '/male/intake' : '/female/intake'}>
                Start assessment <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // ────────────────────────────────────────────────────────────────────────
  // Main dashboard render
  // ────────────────────────────────────────────────────────────────────────
  const firstName = (user?.name || '').split(' ')[0] || 'there';
  const memberSince = formatMemberSince(profile.created_at);
  const dashValue = 251.2;
  const dashOffset = dashValue - (computed.score.score / 100) * dashValue;

  return (
    <div className="min-h-[85vh] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* ── Header ───────────────────────────────────────────────────── */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold font-heading flex flex-wrap items-center gap-x-2 gap-y-1">
              <span>Welcome back</span>
              <span className="text-primary">{firstName}</span>
              <span className="text-base font-normal">👋</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Here's what's happening with your health.
              <span className="ml-2 inline-flex items-center gap-1 text-xs">
                <User className="w-3 h-3" /> Member since {memberSince}
              </span>
            </p>
          </div>
          <NotificationCenter
            notifications={notifications}
            onMarkAllRead={markAllRead}
            onMarkRead={markRead}
            onClearAll={clearAll}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ── Left column (shell — 2/3) ─────────────────────────────── */}
          <div className="space-y-6 lg:col-span-2">
            {/* Score + Quick actions row ────────────────────────────── */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Safety Score Card ─────────────────────────────── */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
              >
                <Card className="h-full">
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-primary" />
                      Safety Score
                      <Badge variant={badgeDef.variant} className="ml-auto h-6 text-xs">
                        {badgeDef.label}
                      </Badge>
                    </CardTitle>
                    <CardDescription>Based on your latest profile flags</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-4">
                      <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
                        <svg className="w-full h-full" viewBox="0 0 100 100">
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="none"
                            stroke="hsl(var(--border))"
                            strokeWidth="8"
                          />
                          <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="none"
                            stroke={colours.fill.startsWith('bg-') ? 'hsl(var(--primary))' : 'currentColor'}
                            strokeWidth="8"
                            strokeLinecap="round"
                            strokeDasharray={dashValue}
                            strokeDashoffset={dashOffset}
                            transform="rotate(-90 50 50)"
                            className={colours.ring}
                          />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className={`text-3xl font-bold ${colours.text}`}>
                            {computed.score.score}
                          </span>
                          <span className="text-xs text-muted-foreground">/100</span>
                        </div>
                      </div>
                      <div className="space-y-2 flex-1 min-w-0">
                        {computed.score.flags.length > 0 ? (
                          <ul className="space-y-1.5">
                            {computed.score.flags.map((f, i) => (
                              <li
                                key={i}
                                className="flex gap-2 text-xs text-muted-foreground leading-snug"
                              >
                                <AlertTriangle className="w-3.5 h-3.5 mt-0.5 text-amber-600 shrink-0" />
                                <span className="flex-1">{f}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-muted-foreground">
                            No active risk flags — keep it up.
                          </p>
                        )}
                        <Progress
                          value={computed.score.score}
                          className="h-2"
                          indicatorClassName={colours.fill}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Quick Actions ────────────────────────────────── */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="h-full">
                  <CardHeader className="pb-2">
                    <CardTitle>Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Link to="/partner-sync" className="w-full block">
                      <Button variant="secondary" className="w-full justify-start gap-2">
                        <Users className="w-4 h-4" />
                        Partner Sync
                      </Button>
                    </Link>
                    <Link to="/education" className="w-full block">
                      <Button variant="secondary" className="w-full justify-start gap-2">
                        <BookOpen className="w-4 h-4" />
                        Education
                      </Button>
                    </Link>
                    <Link to={gender === 'male' ? '/male/intake' : '/female/intake'} className="w-full block">
                      <Button variant="secondary" className="w-full justify-start gap-2">
                        <Stethoscope className="w-4 h-4" />
                        Update Intake
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Recommendations summary ──────────────────────────────── */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-primary" />
                    Recommendation Summary
                  </CardTitle>
                  <CardDescription>
                    Based on your WHO MEC health assessment
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-5">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <h4 className="text-sm font-semibold">Recommended methods</h4>
                    </div>
                    {recommendations.recommended && recommendations.recommended.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {recommendations.recommended.map((m) => (
                          <Badge
                            key={typeof m === 'string' ? m : (m.name || JSON.stringify(m))}
                            variant="secondary"
                            className="text-xs capitalize"
                          >
                            {typeof m === 'string'
                              ? m.replace(/_/g, ' ')
                              : `${m.name}${typeof m.effectiveness === 'number' ? ` — ${m.effectiveness}%` : ''}`}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        No recommendations yet — complete your intake to see personalised options.
                      </p>
                    )}
                  </div>

                  {recommendations.restricted && recommendations.restricted.length > 0 && (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-destructive" />
                        <h4 className="text-sm font-semibold">
                          Not recommended for your profile
                        </h4>
                      </div>
                      <div className="flex flex-col gap-2">
                        {recommendations.restricted.map((r) => {
                          const label = typeof r === 'string' ? r : r.name;
                          const reason =
                            typeof r === 'string' ? null : r.reason || r.who_category;
                          return (
                            <div
                              key={label}
                              className="flex items-start gap-2 rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2"
                            >
                              <Badge variant="destructive" className="text-xs capitalize shrink-0">
                                {label.replace(/_/g, ' ')}
                              </Badge>
                              {reason && (
                                <span className="text-xs text-destructive/90 flex-1">
                                  {reason}
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {recommendations.general_advice && (
                    <div className="flex gap-3 rounded-xl bg-muted/60 p-4">
                      <Info className="w-4 h-4 mt-0.5 text-muted-foreground shrink-0" />
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {recommendations.general_advice}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Gender-specific conditional panel ──────────────────────── */}
            {gender === 'female' && (
              <FemaleHealthPanel profile={profile} sideEffects={computed.sideEffects} />
            )}
            {gender === 'male' && (
              <PartnerAwarenessPanel
                profile={profile}
                partnerProfile={partnerProfile}
                onNavigateToSync={() => navigate('/partner-sync')}
              />
            )}

            {/* Education cards ────────────────────────────────────────── */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <h2 className="text-xl font-semibold mb-4">
                {gender === 'male' ? "Men's Health Education" : "Women's Health Education"}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {educationCards.map((card, idx) => {
                  const Icon = card.icon;
                  return (
                    <Card
                      key={`${card.title}-${idx}`}
                      className="overflow-hidden hover:shadow-md transition-shadow"
                    >
                      <CardContent className="p-6">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 ${card.color}`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <h3 className="font-semibold mb-1">{card.title}</h3>
                        <p className="text-sm text-muted-foreground">{card.description}</p>
                        <Link to="/education" className="inline-flex items-center mt-3 h-8 px-0 text-primary text-sm hover:underline">
                          Learn more <ChevronRight className="w-4 h-4 ml-1" />
                        </Link>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {gender === 'male' && (
                <Card className="mt-6">
                  <CardHeader>
                    <CardTitle>Vasectomy Myths &amp; Facts</CardTitle>
                    <CardDescription>
                      Get answers to common questions about vasectomy.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Accordion type="single" collapsible className="w-full">
                      {VASECTOMY_MYTHS.map((m, i) => (
                        <AccordionItem key={i} value={`item-${i}`}>
                          <AccordionTrigger className="text-left font-medium">
                            {m.myth}
                          </AccordionTrigger>
                          <AccordionContent className="text-muted-foreground">
                            {m.fact}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </CardContent>
                </Card>
              )}
            </motion.div>
          </div>

          {/* ── Right column (shell — 1/3) ───────────────────────────── */}
          <div className="space-y-6">
            {/* Partner sync ──────────────────────────────────────────── */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-primary" />
                    Partner Sync
                  </CardTitle>
                  <CardDescription>
                    Connect with your partner to share health decisions.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!partnerProfile ? (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          Enter your partner's sync token to connect your profiles.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-2">
                          <Input
                            placeholder="Enter partner token"
                            value={partnerToken}
                            onChange={(e) => setPartnerToken(e.target.value)}
                          />
                          <Button
                            onClick={handleVerifyPartner}
                            disabled={connecting || partnerToken.trim() === ''}
                          >
                            {connecting ? (
                              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                            ) : (
                              <Link2 className="w-4 h-4 mr-2" />
                            )}
                            {connecting ? 'Connecting…' : 'Connect'}
                          </Button>
                        </div>
                        {partnerLoadError && (
                          <p className="text-xs text-destructive">{partnerLoadError}</p>
                        )}
                      </div>
                      <div className="text-center">
                        <Link to="/partner-sync">
                          <Button variant="link" className="text-sm">
                            Need a token for yourself?
                          </Button>
                        </Link>
                      </div>
                    </div>
                  ) : (
                    <PartnerSummary profile={partnerProfile} />
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Side effects log ──────────────────────────────────────── */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Pill className="w-5 h-5 text-primary" />
                    Side Effects Log
                  </CardTitle>
                  <CardDescription>
                    Track any symptoms you notice — they'll be shared with your nurse when you
                    use a session key.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3 border rounded-xl p-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="space-y-1.5">
                        <Label htmlFor="se-symptom">Symptom</Label>
                        <Select
                          value={COMMON_SIDE_EFFECTS.includes(newSideEffect.symptom) ? newSideEffect.symptom : newSideEffect.symptom ? 'other' : ''}
                          onValueChange={(v) =>
                            setNewSideEffect((s) => ({
                              ...s,
                              symptom: v === 'other' ? s.symptom : v,
                            }))
                          }
                        >
                          <SelectTrigger id="se-symptom">
                            <SelectValue placeholder="Choose or type" />
                          </SelectTrigger>
                          <SelectContent>
                            {COMMON_SIDE_EFFECTS.map((s) => (
                              <SelectItem key={s} value={s}>{s}</SelectItem>
                            ))}
                            <SelectItem value="other">Other…</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="se-severity">Severity</Label>
                        <Select
                          value={newSideEffect.severity}
                          onValueChange={(v) => setNewSideEffect((s) => ({ ...s, severity: v }))}
                        >
                          <SelectTrigger id="se-severity">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {SEVERITY_OPTIONS.map((s) => (
                              <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-1.5 sm:col-span-2">
                        <Label htmlFor="se-other">
                          {COMMON_SIDE_EFFECTS.includes(newSideEffect.symptom)
                            ? 'Method (optional)'
                            : 'Other symptom / Method'}
                        </Label>
                        <Input
                          id="se-other"
                          placeholder={
                            COMMON_SIDE_EFFECTS.includes(newSideEffect.symptom)
                              ? 'e.g. Combined pill'
                              : 'e.g. Spotting, or method name'
                          }
                          value={
                            COMMON_SIDE_EFFECTS.includes(newSideEffect.symptom)
                              ? newSideEffect.method
                              : newSideEffect.symptom &&
                                  !COMMON_SIDE_EFFECTS.includes(newSideEffect.symptom)
                                ? newSideEffect.symptom
                                : ''
                          }
                          onChange={(e) => {
                            const v = e.target.value;
                            if (COMMON_SIDE_EFFECTS.includes(newSideEffect.symptom)) {
                              setNewSideEffect((s) => ({ ...s, method: v }));
                            } else {
                              setNewSideEffect((s) => ({ ...s, symptom: v }));
                            }
                          }}
                        />
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="se-started">Started on</Label>
                        <Input
                          id="se-started"
                          type="date"
                          value={newSideEffect.started_on}
                          onChange={(e) =>
                            setNewSideEffect((s) => ({ ...s, started_on: e.target.value }))
                          }
                        />
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="se-notes">Notes (optional)</Label>
                      <Textarea
                        id="se-notes"
                        rows={2}
                        placeholder="Anything else to record"
                        value={newSideEffect.notes}
                        onChange={(e) =>
                          setNewSideEffect((s) => ({ ...s, notes: e.target.value }))
                        }
                      />
                    </div>
                    <Button
                      className="w-full gap-2"
                      disabled={!newSideEffect.symptom.trim() || sideEffectSubmitting}
                      onClick={submitSideEffect}
                    >
                      {sideEffectSubmitting ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <Plus className="w-4 h-4" />
                      )}
                      {sideEffectSubmitting ? 'Saving…' : 'Log entry'}
                    </Button>
                  </div>

                  {computed.sideEffects.length === 0 ? (
                    <div className="text-sm text-center text-muted-foreground py-6 rounded-lg bg-muted/40">
                      No entries yet — log something above if you notice any symptoms.
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                      {computed.sideEffects
                        .slice()
                        .sort((a, b) => new Date(b.logged_at || b.started_on) - new Date(a.logged_at || a.started_on))
                        .map((entry) => (
                          <div
                            key={entry.id || entry.logged_at || entry.started_on}
                            className="rounded-lg border p-3"
                          >
                            <div className="flex items-center justify-between gap-2 mb-1">
                              <div className="flex items-center gap-2 min-w-0">
                                <span className="font-medium text-sm truncate">
                                  {entry.symptom || 'Unnamed symptom'}
                                </span>
                                <Badge
                                  variant={
                                    entry.severity === 'severe'
                                      ? 'destructive'
                                      : entry.severity === 'moderate'
                                        ? 'outline'
                                        : 'secondary'
                                  }
                                  className="text-xs capitalize"
                                >
                                  {entry.severity || 'mild'}
                                </Badge>
                              </div>
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <span className="text-xs text-muted-foreground shrink-0">
                                      {timeAgo(entry.logged_at || entry.started_on) || entry.started_on || ''}
                                    </span>
                                  </TooltipTrigger>
                                  <TooltipContent>{entry.started_on}</TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            </div>
                            {entry.method && (
                              <p className="text-xs text-muted-foreground mb-1">
                                Method: {entry.method}
                              </p>
                            )}
                            {entry.notes && (
                              <p className="text-xs text-muted-foreground">{entry.notes}</p>
                            )}
                          </div>
                        ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Activity + Milestones tabs ────────────────────────────── */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Tabs defaultValue="activity" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="activity">Recent Activity</TabsTrigger>
                  <TabsTrigger value="milestones">Milestones</TabsTrigger>
                </TabsList>
                <TabsContent value="activity">
                  <Card>
                    <CardContent className="pt-6">
                      {computed.timeline.length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-8">
                          No activity yet.
                        </p>
                      ) : (
                        <div className="space-y-4">
                          {computed.timeline.slice(0, 12).map((ev) => {
                            const Icon = ev.icon;
                            return (
                              <div key={ev.id} className="flex items-center gap-4">
                                <div className={`p-2 rounded-full bg-muted ${ev.color}`}>
                                  <Icon className="w-4 h-4" />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium truncate">{ev.action}</p>
                                  <p className="text-xs text-muted-foreground">
                                    {timeAgo(ev.time) || formatMemberSince(ev.time)}
                                  </p>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="milestones">
                  <Card>
                    <CardContent className="pt-6 space-y-4">
                      {computed.milestones.map((m) => (
                        <div key={m.id} className="space-y-2">
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-sm font-medium">{m.title}</p>
                            {m.completed && (
                              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                            )}
                          </div>
                          <Progress value={m.progress} className="h-2" />
                          <p className="text-xs text-muted-foreground">{m.progress}% complete</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </motion.div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {showTour && (
          <OnboardingTour
            currentStep={tourStep}
            onNext={() => setTourStep((s) => Math.min(s + 1, 4))}
            onPrev={() => setTourStep((s) => Math.max(s - 1, 0))}
            onClose={completeTour}
            totalSteps={5}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Gender-specific sub-panels ────────────────────────────────────────────────

function FemaleHealthPanel({ profile, sideEffects }) {
  const lastPeriod = profile?.last_period_date;
  const ppWeeks = profile?.postpartum_weeks;
  const breastfeeding = profile?.breastfeeding;

  const rows = [];
  if (ppWeeks != null && ppWeeks !== '') {
    rows.push({ label: 'Postpartum', value: `${Number(ppWeeks)} weeks` });
  }
  if (breastfeeding) {
    rows.push({ label: 'Breastfeeding', value: 'Yes' });
  }
  if (lastPeriod) {
    rows.push({
      label: 'Last period',
      value: new Date(lastPeriod).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }),
    });
  }
  rows.push({
    label: 'Blood pressure',
    value:
      profile?.systolic_bp && profile?.diastolic_bp
        ? `${profile.systolic_bp}/${profile.diastolic_bp} mmHg`
        : 'Not recorded',
  });
  rows.push({
    label: 'Logged side effects',
    value: `${Array.isArray(sideEffects) ? sideEffects.length : 0} entries`,
  });

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-primary" />
            Cycle &amp; Reproductive Snapshot
          </CardTitle>
          <CardDescription>
            Latest details from your most recent intake.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {rows.map((r) => (
              <div key={r.label} className="bg-muted/50 rounded-xl p-3">
                <p className="text-xs text-muted-foreground">{r.label}</p>
                <p className="font-medium text-sm mt-0.5">{r.value}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function PartnerAwarenessPanel({ profile, partnerProfile, onNavigateToSync }) {
  const age = profile?.age || 0;
  const smoking = Boolean(profile?.smoking);
  const migraine = profile?.migraine_type || 'none';
  const systolic = profile?.systolic_bp || 0;
  const diastolic = profile?.diastolic_bp || 0;

  const keyMessages = [];
  if (age > 35 && smoking) keyMessages.push('Quit smoking support — reduces combined-method risks for your partner.');
  if (migraine === 'with_aura' || migraine === 'without_aura')
    keyMessages.push('Discuss migraine history with a provider before choosing a combined method.');
  if (systolic >= 140 || diastolic >= 90)
    keyMessages.push('Elevated BP detected — encourage partner to have it checked.');
  if (keyMessages.length === 0)
    keyMessages.push('Your cardiovascular profile supports low-risk decisions.');

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            Partner Awareness
          </CardTitle>
          <CardDescription>
            What this means for shared contraceptive decisions.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ul className="space-y-2">
            {keyMessages.map((m, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                <span>{m}</span>
              </li>
            ))}
          </ul>

          {!partnerProfile && (
            <div className="border rounded-xl p-4 flex items-start gap-3 bg-muted/40">
              <Info className="w-4 h-4 mt-0.5 text-muted-foreground shrink-0" />
              <div className="flex-1">
                <p className="text-sm">
                  No partner profile is connected yet. When you connect, you'll see their
                  recommended and restricted methods side-by-side here.
                </p>
                <Button
                  variant="link"
                  className="h-auto p-0 text-sm mt-1"
                  onClick={onNavigateToSync}
                >
                  Go to Partner Sync <ChevronRight className="w-4 h-4 ml-0.5" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function buildStaticNotifs({ gender }) {
  const now = Date.now();
  const arr = [
    {
      id: 'welcome',
      title: 'Welcome!',
      message: 'Your safety score and recommendations are ready to view below.',
      time: 'just now',
      read: false,
      createdAt: now,
    },
  ];
  if (gender === 'female') {
    arr.push({
      id: 'female-cycle-reminder',
      title: 'Cycle tracking reminder',
      message:
        "Don't forget to log your next period in the side-effects panel to keep your dashboard accurate.",
      time: '2 min ago',
      read: false,
      createdAt: now - 120_000,
    });
  } else {
    arr.push({
      id: 'male-partner-reminder',
      title: 'Share decisions with your partner',
      message:
        'Use Partner Sync with a one-time token so you both see the same contraceptive recommendations.',
      time: '2 min ago',
      read: false,
      createdAt: now - 120_000,
    });
  }
  return arr;
}
