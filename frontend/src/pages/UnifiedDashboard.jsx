
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Shield,
  Heart,
  BookOpen,
  CheckCircle,
  XCircle,
  Link2,
  Loader2,
  Info,
  AlertTriangle,
  Bell,
  TrendingUp,
  Calendar,
  Activity,
  ArrowRight,
  X,
  ChevronRight
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { verifySyncToken } from '@/api/apiClient';
import { useAuth } from '@/lib/AuthContext';

// --- Mock Data & Helper Functions ---

const getAnonymousId = () => {
  let id = sessionStorage.getItem('nuru_anon_id');
  if (!id) {
    id = 'anon_' + Math.random().toString(36).slice(2, 10);
    sessionStorage.setItem('nuru_anon_id', id);
  }
  return id;
};

const vasectomyMyths = [
  {
    myth: 'Vasectomy affects masculinity or performance',
    fact: 'Vasectomy only blocks sperm transport. It does not affect hormone levels, libido, or sexual performance.'
  },
  {
    myth: 'Vasectomy is permanent and cannot be reversed',
    fact: "Vasectomy reversal is possible, though success rates vary. It's best considered a permanent decision with reversal as a possibility."
  },
  {
    myth: 'Vasectomy is painful and requires long recovery',
    fact: 'Modern no-scalpel vasectomy is minimally invasive. Most men return to normal activities within a few days.'
  }
];

const femaleEducationCards = [
  {
    title: 'Contraceptive Options',
    desc: 'Learn about all available contraceptive methods tailored to your health profile',
    color: 'bg-primary/10 text-primary',
    icon: Shield,
    id: 'female-options'
  },
  {
    title: 'Cycle Tracking',
    desc: 'Understand your menstrual cycle to make informed decisions',
    color: 'bg-secondary/10 text-secondary',
    icon: Activity,
    id: 'female-cycle'
  },
  {
    title: 'Health Tips',
    desc: 'Personalized health recommendations based on your profile',
    color: 'bg-accent/10 text-accent',
    icon: Heart,
    id: 'female-tips'
  },
  {
    title: 'Partner Sync',
    desc: 'Share your profile securely with your partner',
    color: 'bg-primary/10 text-primary',
    icon: Users,
    id: 'female-sync'
  }
];

const maleEducationCards = [
  {
    title: 'Vasectomy Info',
    desc: 'Everything you need to know about vasectomy and other male contraceptives',
    color: 'bg-primary/10 text-primary',
    icon: Shield,
    id: 'male-vasectomy'
  },
  {
    title: 'Health Tips',
    desc: 'Personalized health recommendations for men',
    color: 'bg-secondary/10 text-secondary',
    icon: Heart,
    id: 'male-tips'
  },
  {
    title: 'Partner Sync',
    desc: 'Connect with your partner to support their health journey',
    color: 'bg-accent/10 text-accent',
    icon: BookOpen,
    id: 'male-sync'
  },
  {
    title: 'Resources',
    desc: 'Additional resources for male reproductive health',
    color: 'bg-primary/10 text-primary',
    icon: Users,
    id: 'male-resources'
  }
];

// --- Sub-Components ---

// Simple Chart Component (for data visualization)
const SimpleChart = ({ gender }) => {
  // Mock data for visualization
  const data = gender === 'female'
    ? [65, 85, 45, 90, 70]
    : [80, 60, 75, 95, 85];
  const max = Math.max(...data);

  return (
    <div className="flex items-end gap-2 h-24">
      {data.map((value, index) => (
        <div key={index} className="flex-1 flex flex-col items-center">
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: `${(value / max) * 100}%` }}
            className={`w-full rounded-t-md ${index % 2 === 0 ? 'bg-primary/50' : 'bg-secondary/50'}`}
          />
          <span className="text-xs mt-1 text-muted-foreground">{`W${index + 1}`}</span>
        </div>
      ))}
    </div>
  );
};

// Notification Bell/List
const NotificationCenter = () => {
  const [open, setOpen] = useState(false);
  const notifications = [
    { id: 1, title: 'Welcome to NuruCare!', desc: 'Complete your profile to get personalized recommendations.', type: 'info', read: false },
    { id: 2, title: 'New Health Tip Available', desc: 'Check out our latest health recommendations!', type: 'success', read: true },
    { id: 3, title: 'Partner Sync Reminder', desc: 'Invite your partner to sync profiles.', type: 'alert', read: false }
  ];

  return (
    <div className="relative">
      <Button variant="ghost" size="icon" onClick={() => setOpen(!open)} className="rounded-full">
        <Bell className="w-5 h-5" />
        <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
      </Button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute right-0 mt-2 w-80 bg-background border rounded-xl shadow-lg z-50"
          >
            <div className="p-4 border-b">
              <h3 className="font-medium">Notifications</h3>
            </div>
            <div className="p-2 max-h-80 overflow-y-auto">
              {notifications.map((n) => (
                <div key={n.id} className={`p-3 rounded-lg mb-1 cursor-pointer ${n.read ? 'bg-muted/30' : 'bg-muted/50'}`}>
                  <div className="flex items-start gap-3">
                    {n.type === 'info' && <Info className="w-4 h-4 text-primary mt-0.5" />}
                    {n.type === 'success' && <CheckCircle className="w-4 h-4 text-secondary mt-0.5" />}
                    {n.type === 'alert' && <AlertTriangle className="w-4 h-4 text-destructive mt-0.5" />}
                    <div className="flex-1">
                      <p className="text-sm font-medium">{n.title}</p>
                      <p className="text-xs text-muted-foreground">{n.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-3 border-t">
              <Button variant="ghost" className="w-full text-primary text-sm">View All</Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Partner Summary Component
const PartnerSummary = ({ profile }) => {
  if (!profile) return null;

  const fields = [
    { label: 'Age', value: profile.age },
    { label: 'Smoking', value: profile.smoking ? 'Yes' : 'No' },
    { label: 'Migraine Type', value: profile.migraine_type?.replace(/_/g, ' ') || '—' },
    { label: 'Blood Pressure', value: profile.systolic_bp && profile.diastolic_bp ? `${profile.systolic_bp}/${profile.diastolic_bp}` : '—' },
  ];

  const isHighRisk =
    (profile.smoking && profile.age > 35) || profile.migraine_type === 'with_aura';

  return (
    <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 mt-4">
      {isHighRisk && (
        <div className="flex items-start gap-3 bg-destructive/10 border border-destructive/30 rounded-xl p-4">
          <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-destructive">High Risk Profile</p>
            <p className="text-xs text-destructive/80 mt-0.5">
              Your partner should consult a healthcare provider before starting any contraceptive method.
            </p>
          </div>
        </div>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {fields.map(({ label, value }) => (
          <div key={label} className="bg-muted/50 rounded-xl p-3">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="font-medium text-sm mt-0.5 capitalize">{String(value ?? '—')}</p>
          </div>
        ))}
      </div>
      {Array.isArray(profile.allowed_methods) && profile.allowed_methods.length > 0 && (
        <div>
          <p className="text-sm font-medium mb-2 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-secondary" /> Safe Methods for Your Partner
          </p>
          <div className="flex flex-wrap gap-2">
            {profile.allowed_methods.map((m) => (
              <Badge key={m} variant="secondary" className="text-xs capitalize">{m.replace(/_/g, ' ')}</Badge>
            ))}
          </div>
        </div>
      )}
      <div className="bg-muted rounded-xl p-3 flex items-start gap-2 text-xs text-muted-foreground">
        <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
        This is a summary to support informed conversations. Always consult a healthcare provider.
      </div>
    </motion.div>
  );
};

// Onboarding Tour Component
const OnboardingTour = ({ onClose }) => {
  const [step, setStep] = useState(0);
  const tourSteps = [
    { title: 'Welcome!', desc: 'This is your personalized dashboard. Let\'s take a quick tour.', icon: Heart, highlight: 'header' },
    { title: 'Education Hub', desc: 'Find health information tailored to your needs.', icon: BookOpen, highlight: 'education' },
    { title: 'Partner Sync', desc: 'Connect with your partner to share health info securely.', icon: Link2, highlight: 'sync' },
    { title: 'Notifications', desc: 'Stay updated with important health reminders.', icon: Bell, highlight: 'notifications' }
  ];

  return (
    <div className="fixed inset-0 z-[100] bg-black/50 flex items-center justify-center p-4">
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="bg-background rounded-2xl max-w-lg w-full p-6 shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Welcome Tour</h3>
          <Button variant="ghost" size="icon" onClick={onClose}><X className="w-4 h-4" /></Button>
        </div>
        <div className="text-center">
          <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-4 ${step === 0 ? 'bg-primary/10' : step === 1 ? 'bg-secondary/10' : step === 2 ? 'bg-accent/10' : 'bg-muted'}`}>
            <tourSteps[step].icon className={`w-8 h-8 ${step === 0 ? 'text-primary' : step === 1 ? 'text-secondary' : step === 2 ? 'text-accent' : 'text-muted-foreground'}`} />
          </div>
          <h4 className="font-medium text-lg mb-2">{tourSteps[step].title}</h4>
          <p className="text-muted-foreground text-sm mb-6">{tourSteps[step].desc}</p>
        </div>
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}>Back</Button>
          <div className="flex gap-2">
            {tourSteps.map((_, i) => (
              <div key={i} className={`w-2 h-2 rounded-full ${i === step ? 'bg-primary' : 'bg-muted'}`} />
            ))}
          </div>
          <Button onClick={step === tourSteps.length - 1 ? onClose : () => setStep(step + 1)}>
            {step === tourSteps.length - 1 ? 'Get Started' : 'Next'}
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

// --- Main Component ---

export default function UnifiedDashboard({ gender = 'female' }) {
  const { user } = useAuth();
  const { toast } = useToast();

  // State
  const [showTour, setShowTour] = useState(false);
  const [partnerToken, setPartnerToken] = useState('');
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [partnerProfile, setPartnerProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Check if first-time user for tour
  useEffect(() => {
    const hasSeenTour = localStorage.getItem('nuru_tour_seen');
    if (!hasSeenTour) {
      setShowTour(true);
    }
  }, []);

  const handleTourComplete = () => {
    localStorage.setItem('nuru_tour_seen', 'true');
    setShowTour(false);
  };

  const connectPartner = async () => {
    if (partnerToken.trim().length < 6) return;
    setConnecting(true);
    try {
      const response = await verifySyncToken(partnerToken.trim(), getAnonymousId());
      if (response.success) {
        setConnected(true);
        if (response.partner_profile) setPartnerProfile(response.partner_profile);
        toast({ title: 'Connected Successfully!', description: 'You are now connected to your partner.' });
      } else {
        toast({ title: 'Connection Failed', description: response.message || 'Invalid or expired token.', variant: 'destructive' });
      }
    } catch (err) {
      toast({ title: 'Connection Failed', description: err?.response?.data?.detail || 'Could not connect. Please check the token.', variant: 'destructive' });
    } finally {
      setConnecting(false);
    }
  };

  const educationCards = gender === 'female' ? femaleEducationCards : maleEducationCards;

  return (
    <div className="min-h-[85vh] pb-20">
      <AnimatePresence>{showTour && <OnboardingTour onClose={handleTourComplete} />}</AnimatePresence>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <Badge className="mb-3 bg-primary/10 text-primary border-primary/20">
                {gender === 'female' ? 'Women\'s Health' : 'Men\'s Health'}
              </Badge>
              <h1 className="font-heading text-3xl sm:text-4xl font-bold">
                Hello{user?.fullName ? `, ${user.fullName}` : ' there'}!
              </h1>
              <p className="text-muted-foreground mt-2">Here's what's happening with your health today.</p>
            </div>
            <div className="flex items-center gap-3">
              <NotificationCenter />
            </div>
          </div>
        </motion.div>

        {/* Tabs for Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="w-full sm:w-auto grid grid-cols-3 sm:flex">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="education">Education</TabsTrigger>
            <TabsTrigger value="partner">Partner Sync</TabsTrigger>
          </TabsList>

          {/* Overview Tab Content */}
          <TabsContent value="overview" className="mt-6">
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {/* Progress/Health Score Card */}
              <Card className="lg:col-span-1 sm:col-span-2">
                <CardHeader>
                  <CardTitle>Health Score</CardTitle>
                  <CardDescription>Based on your current profile</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-6">
                    <div className="relative w-24 h-24">
                      <svg className="w-full h-full" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="40" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
                        <motion.circle
                          cx="50" cy="50" r="40" fill="none"
                          stroke="hsl(var(--primary))" strokeWidth="8"
                          strokeLinecap="round"
                          initial={{ pathLength: 0 }}
                          animate={{ pathLength: 0.85 }}
                          transform="rotate(-90 50 50)"
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-2xl font-bold">85%</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground mb-2">Your health is looking great! Here are some recommendations:</p>
                      <ul className="text-sm space-y-1">
                        <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-secondary" /> Complete your full profile</li>
                        <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-secondary" /> Connect with your partner</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full justify-start gap-2" onClick={() => setActiveTab('education')}><BookOpen className="w-4 h-4" /> Learn More</Button>
                  <Button className="w-full justify-start gap-2" onClick={() => setActiveTab('partner')}><Link2 className="w-4 h-4" /> Connect Partner</Button>
                  <Button variant="ghost" className="w-full justify-start gap-2"><Users className="w-4 h-4" /> Find a Provider</Button>
                </CardContent>
              </Card>

              {/* Data Visualization */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    Health Trends
                    <Badge variant="outline" className="flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" /> Weekly
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <SimpleChart gender={gender} />
                </CardContent>
              </Card>

              {/* Upcoming Milestones */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><Calendar className="w-4 h-4" /> Next Steps</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-muted/30 rounded-xl">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center"><CheckCircle className="w-4 h-4 text-primary" /></div>
                      <div>
                        <p className="text-sm font-medium">Complete Profile</p>
                        <p className="text-xs text-muted-foreground">50% done</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted/30 rounded-xl">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-secondary/10 flex items-center justify-center"><Heart className="w-4 h-4 text-secondary" /></div>
                      <div>
                        <p className="text-sm font-medium">Schedule Checkup</p>
                        <p className="text-xs text-muted-foreground">Recommended</p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Education Tab */}
          <TabsContent value="education" className="mt-6">
            <div className="grid sm:grid-cols-2 gap-5">
              {educationCards.map((c, i) => (
                <motion.div key={c.id} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                  <Card className="p-5 rounded-2xl h-full hover:shadow-md transition-shadow">
                    <div className={`w-10 h-10 rounded-xl ${c.color} flex items-center justify-center mb-3`}>
                      <c.icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-heading font-semibold mb-1">{c.title}</h3>
                    <p className="text-sm text-muted-foreground">{c.desc}</p>
                    <Button variant="ghost" className="mt-4 px-0 text-primary">
                      Explore <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Card>
                </motion.div>
              ))}
            </div>

            {/* Male-specific myths accordion */}
            {gender === 'male' && (
              <Card className="p-6 rounded-2xl mt-6">
                <h3 className="font-heading font-semibold text-lg mb-4">Common Myths</h3>
                <Accordion type="single" collapsible className="space-y-2">
                  {vasectomyMyths.map((vm, i) => (
                    <AccordionItem key={i} value={`vm-${i}`} className="bg-muted/30 rounded-xl border px-4">
                      <AccordionTrigger className="py-3 hover:no-underline text-left">
                        <div className="flex items-center gap-2 text-sm">
                          <XCircle className="w-4 h-4 text-destructive flex-shrink-0" />
                          <span className="font-medium">{vm.myth}</span>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="pb-3">
                        <div className="flex items-start gap-2 ml-6 text-sm">
                          <CheckCircle className="w-4 h-4 text-secondary flex-shrink-0 mt-0.5" />
                          <p className="text-muted-foreground">{vm.fact}</p>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </Card>
            )}
          </TabsContent>

          {/* Partner Sync Tab */}
          <TabsContent value="partner" className="mt-6">
            <Card className="p-6 rounded-2xl">
              <h3 className="font-heading font-semibold text-lg mb-4 flex items-center gap-2">
                <Link2 className="w-5 h-5 text-accent" /> Partner Sync
              </h3>
              {!connected ? (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Ask your partner to open <strong>Partner Sync</strong> and share their token with you.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Input
                      placeholder="Enter partner's sync token"
                      value={partnerToken}
                      onChange={(e) => setPartnerToken(e.target.value)}
                      className="flex-1 font-mono"
                      onKeyDown={(e) => e.key === 'Enter' && connectPartner()}
                    />
                    <Button onClick={connectPartner} disabled={connecting || partnerToken.trim().length < 6} className="rounded-full sm:w-auto w-full gap-2">
                      {connecting && <Loader2 className="w-4 h-4 animate-spin" />}
                      {connecting ? 'Connecting…' : 'Connect'}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="flex items-center gap-3 bg-secondary/10 rounded-xl p-4">
                    <CheckCircle className="w-5 h-5 text-secondary flex-shrink-0" />
                    <div>
                      <p className="font-medium text-sm text-secondary">Connected to Partner</p>
                      <p className="text-xs text-muted-foreground">Your profiles are synced securely.</p>
                    </div>
                  </div>
                  {partnerProfile ? <PartnerSummary profile={partnerProfile} /> : (
                    <div className="bg-muted/50 rounded-xl p-4 text-sm text-muted-foreground">
                      <p>Partner connected. Ask them to complete the health assessment to view their summary here.</p>
                    </div>
                  )}
                </div>
              )}
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
