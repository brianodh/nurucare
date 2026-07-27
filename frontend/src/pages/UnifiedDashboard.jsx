import { useState, useEffect, useMemo } from 'react';
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
  CalendarDays,
  Activity,
  ArrowRight,
  X,
  ChevronRight,
  Clock,
  MoreHorizontal,
  Filter,
  CheckSquare,
  Square
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { verifySyncToken } from '@/api/apiClient';
import { useAuth } from '@/lib/AuthContext';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer
} from 'recharts';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const getAnonymousId = () => {
  let id = sessionStorage.getItem('nuru_anon_id');
  if (!id) {
    id = 'anon_' + Math.random().toString(36).slice(2, 10);
    sessionStorage.setItem('nuru_anon_id', id);
  }
  return id;
};

const vasectomyMyths = [
  { myth: 'Vasectomy affects masculinity or performance', fact: 'Vasectomy only blocks sperm transport. It does not affect hormone levels, libido, or sexual performance.' },
  { myth: 'Vasectomy is permanent and cannot be reversed', fact: "Vasectomy reversal is possible, though success rates vary. It's best considered a permanent decision with reversal as a possibility." },
  { myth: 'Vasectomy is painful and requires long recovery', fact: 'Modern no-scalpel vasectomy is minimally invasive. Most men return to normal activities within a few days.' },
];

const femaleEducationCards = [
  { title: 'Contraceptive Options', desc: 'Learn about all available contraceptive methods tailored to your health profile', color: 'bg-primary/10 text-primary', Icon: Shield, id: 'female-options' },
  { title: 'Cycle Tracking', desc: 'Understand your menstrual cycle to make informed decisions', color: 'bg-secondary/10 text-secondary', Icon: Activity, id: 'female-cycle' },
  { title: 'Health Tips', desc: 'Personalized health recommendations based on your profile', color: 'bg-accent/10 text-accent', Icon: Heart, id: 'female-tips' },
  { title: 'Partner Sync', desc: 'Share your profile securely with your partner', color: 'bg-primary/10 text-primary', Icon: Users, id: 'female-sync' },
];

const maleEducationCards = [
  { title: 'Vasectomy Info', desc: 'Everything you need to know about vasectomy and other male contraceptives', color: 'bg-primary/10 text-primary', Icon: Shield, id: 'male-vasectomy' },
  { title: 'Health Tips', desc: 'Personalized health recommendations for men', color: 'bg-secondary/10 text-secondary', Icon: Heart, id: 'male-tips' },
  { title: 'Partner Sync', desc: 'Connect with your partner to support their health journey', color: 'bg-accent/10 text-accent', Icon: BookOpen, id: 'male-sync' },
  { title: 'Resources', desc: 'Additional resources for male reproductive health', color: 'bg-primary/10 text-primary', Icon: Users, id: 'male-resources' },
];

const HealthTrendChart = ({ gender, timeRange, data }) => {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity="0.3" />
              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity="0" />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="name" 
            stroke="hsl(var(--muted-foreground))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <RechartsTooltip 
            contentStyle={{ 
              backgroundColor: 'hsl(var(--card))', 
              border: '1px solid hsl(var(--border))',
              borderRadius: '0.5rem' 
            }}
          />
          <Area 
            type="monotone" 
            dataKey="value" 
            stroke="hsl(var(--primary))" 
            fillOpacity={1} 
            fill="url(#colorHealth)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

const NotificationCenter = ({ notifications, markRead, clearAll }) => {
  const [open, setOpen] = useState(false);
  const unreadCount = useMemo(() => notifications.filter(n => !n.read).length, [notifications]);

  return (
    <div className="relative">
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setOpen(!open)} 
              className="rounded-full relative"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Notifications</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute right-0 top-12 mt-2 w-[90vw] sm:w-80 bg-card border rounded-xl shadow-lg z-50"
          >
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-medium">Notifications</h3>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => notifications.forEach(n => markRead(n.id))}
                    className="text-xs"
                  >
                    Mark All Read
                  </Button>
                )}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={clearAll} className="text-destructive">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Clear All
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
            <div className="p-2 max-h-80 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-6 text-center text-muted-foreground">
                  <CheckCircle className="w-10 h-10 mx-auto mb-2 text-secondary" />
                  <p>No new notifications</p>
                </div>
              ) : (
                notifications.map((n) => (
                  <div 
                    key={n.id} 
                    className="p-3 rounded-lg mb-1 cursor-pointer transition-all"
                    style={{ backgroundColor: n.read ? 'hsl(var(--muted)/0.3)' : 'hsl(var(--muted)/0.5)' }}
                    onClick={() => markRead(n.id)}
                  >
                    <div className="flex items-start gap-3">
                      {n.type === 'info' && <Info className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />}
                      {n.type === 'success' && <CheckCircle className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />}
                      {n.type === 'alert' && <AlertTriangle className="w-4 h-4 text-destructive mt-0.5 flex-shrink-0" />}
                      {n.type === 'warning' && <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />}
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium">{n.title}</p>
                          {!n.read && <div className="w-2 h-2 bg-primary rounded-full" />}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{n.desc}</p>
                        <p className="text-[10px] text-muted-foreground mt-1">{n.time}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const PartnerSummary = ({ profile }) => {
  if (!profile) return null;

  const fields = [
    { label: 'Age', value: profile.age },
    { label: 'Smoking', value: profile.smoking ? 'Yes' : 'No' },
    { label: 'Migraine Type', value: profile.migraine_type?.replace(/_/g, ' ') || '—' },
    { label: 'Blood Pressure', value: profile.systolic_bp && profile.diastolic_bp ? `${profile.systolic_bp}/${profile.diastolic_bp}` : '—' },
  ];

  const isHighRisk = (profile.smoking && profile.age > 35) || profile.migraine_type === 'with_aura';

  return (
    <motion.div initial={{ opacity: 0, y:15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 mt-4">
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

const OnboardingTour = ({ currentStep, steps, onNext, onPrev, onClose, totalSteps }) => {
  const StepIcon = steps[currentStep].Icon;
  return (
    <div className="fixed inset-0 z-[100] bg-black/60 flex items-center justify-center p-4">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }} 
        animate={{ scale: 1, opacity: 1 }} 
        className="bg-card rounded-2xl max-w-lg w-full p-6 shadow-2xl"
      >
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <StepIcon className="w-5 h-5 text-primary" />
            </div>
            <h3 className="text-xl font-bold">Welcome Tour</h3>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}><X className="w-4 h-4" /></Button>
        </div>
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-medium text-muted-foreground">
              Step {currentStep + 1} of {totalSteps}
            </span>
            <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-primary"
                initial={{ width: `${(currentStep / totalSteps) * 100}%` }}
                animate={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
              />
            </div>
          </div>
          <h4 className="font-medium text-lg mb-2">{steps[currentStep].title}</h4>
          <p className="text-muted-foreground text-sm">{steps[currentStep].desc}</p>
        </div>
        <div className="flex items-center justify-between">
          <Button 
            variant="ghost" 
            onClick={onPrev} 
            disabled={currentStep === 0}
          >
            Back
          </Button>
          <Button onClick={currentStep === totalSteps -1 ? onClose : onNext} >
            {currentStep === totalSteps - 1 ? 'Get Started' : 'Next'}
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default function UnifiedDashboard({ gender = 'female' }) {
  const { user } = useAuth();
  const { toast } = useToast();
  const [showTour, setShowTour] = useState(false);
  const [tourStep, setTourStep] = useState(0);
  const [partnerToken, setPartnerToken] = useState('');
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [partnerProfile, setPartnerProfile] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('week');
  const [notifications, setNotifications] = useState([
    { id: 1, title: 'Welcome to NuruCare!', desc: 'Complete your profile to get personalized recommendations.', type: 'info', read: false, time: 'Just now' },
    { id: 2, title: 'New Health Tip Available', desc: 'Check out our latest health recommendations!', type: 'success', read: true, time: '2 hours ago' },
    { id: 3, title: 'Partner Sync Reminder', desc: 'Invite your partner to sync profiles.', type: 'alert', read: false, time: '1 day ago' },
  ]);
  const [recentActivity, setRecentActivity] = useState([
    { id: 1, title: 'Profile Updated', desc: 'You completed your health profile', time: '2 hours ago', type: 'success' },
    { id: 2, title: 'Health Check', desc: 'You viewed your health recommendations', time: '1 day ago', type: 'info' },
  ]);
  const [milestones, setMilestones] = useState([
    { id: 1, title: 'Complete Profile', progress: 50, completed: false },
    { id: 2, title: 'Connect Partner', progress: 0, completed: false },
  ]);

  const educationCards = gender === 'female' ? femaleEducationCards : maleEducationCards;

  const chartData = useMemo(() => {
    if (timeRange === 'week') {
      return [
        { name: 'Mon', value: 60 },
        { name: 'Tue', value: 75 },
        { name: 'Wed', value: 65 },
        { name: 'Thu', value: 80 },
        { name: 'Fri', value: 70 },
        { name: 'Sat', value: 85 },
        { name: 'Sun', value: 78 },
      ];
    } else if (timeRange === 'month') {
      return [
        { name: 'Week 1', value: 65 },
        { name: 'Week 2', value: 70 },
        { name: 'Week 3', value: 75 },
        { name: 'Week 4', value: 80 },
      ];
    }
    return [
      { name: 'Jan', value: 60 },
      { name: 'Feb', value: 65 },
      { name: 'Mar', value: 70 },
      { name: 'Apr', value: 75 },
      { name: 'May', value: 78 },
      { name: 'Jun', value: 85 },
    ];
  }, [timeRange]);

  const tourSteps = useMemo(() => {
    return [
      { title: 'Welcome!', desc: 'This is your personalized dashboard. Let\'s take a quick tour.', Icon: Heart },
      { title: 'Overview', desc: 'View your health score, trends and quick actions.', Icon: TrendingUp },
      { title: 'Education Hub', desc: 'Find health information tailored to your needs.', Icon: BookOpen },
      { title: 'Partner Sync', desc: 'Connect with your partner to share health info securely.', Icon: Link2 },
      { title: 'Notifications', desc: 'Stay updated with important health reminders.', Icon: Bell },
    ];
  }, []);

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
        setNotifications(prev => [...prev, { id: Date.now(), title: 'Partner Connected!', desc: 'You and your partner are now synced.', type: 'success', read: false, time: 'Just now' }]);
      } else {
        toast({ title: 'Connection failed', description: response.message || 'Invalid or expired token.', variant: 'destructive' });
      }
    } catch (err) {
      toast({ title: 'Connection failed', description: err?.response?.data?.detail || 'Could not connect. Please check the token.', variant: 'destructive' });
    } finally {
      setConnecting(false);
    }
  };

  const markNotificationRead = (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  const markMilestoneComplete = (id) => {
    setMilestones(prev => prev.map(m => m.id === id ? { ...m, completed: true, progress: 100 } : m));
  };

  return (
    <div className="min-h-[85vh] pb-20">
      <AnimatePresence>
        {showTour && (
          <OnboardingTour
            currentStep={tourStep}
            steps={tourSteps}
            onNext={() => setTourStep(s => s + 1)}
            onPrev={() => setTourStep(s => s - 1)}
            onClose={handleTourComplete}
            totalSteps={tourSteps.length}
          />
        )}
      </AnimatePresence>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
              <NotificationCenter 
                notifications={notifications} 
                markRead={markNotificationRead} 
                clearAll={clearAllNotifications} 
              />
            </div>
          </div>
        </motion.div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="w-full sm:w-auto grid grid-cols-3 sm:flex">
            <TabsTrigger value="overview" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">Overview</TabsTrigger>
            <TabsTrigger value="education" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">Education</TabsTrigger>
            <TabsTrigger value="partner" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">Partner Sync</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="lg:col-span-1 sm:col-span-2">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Health Score</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
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
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Health Trends
                    </CardTitle>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8 gap-1">
                          <Filter className="h-3 w-3" />
                          <span className="sr-only">Filter</span>
                          {timeRange === 'week' ? 'Week' : timeRange === 'month' ? 'Month' : 'Year'}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => setTimeRange('week')}>Week</DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setTimeRange('month')}>Month</DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setTimeRange('year')}>Year</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent>
                  <HealthTrendChart gender={gender} timeRange={timeRange} data={chartData} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><CalendarDays className="w-4 h-4" /> Upcoming Milestones</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {milestones.map((m) => (
                    <div key={m.id} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => markMilestoneComplete(m.id)}
                          >
                            {m.completed ? <CheckSquare className="h-4 w-4 text-secondary" /> : <Square className="h-4 w-4" />}
                          </Button>
                          <div>
                            <p className="text-sm font-medium">{m.title}</p>
                            <p className="text-xs text-muted-foreground">{m.progress}% done</p>
                          </div>
                        </div>
                        {!m.completed && <ChevronRight className="w-4 h-4 text-muted-foreground" />}
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-primary"
                          initial={{ width: '0%' }}
                          animate={{ width: `${m.progress}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Clock className="w-4 h-4" /> Recent Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {recentActivity.map((a) => (
                  <div key={a.id} className="flex items-start gap-3 bg-muted/30 rounded-xl p-3">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                      {a.type === 'success' ? <CheckCircle className="w-4 h-4 text-secondary" /> : <Info className="w-4 h-4 text-primary" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{a.title}</p>
                      <p className="text-xs text-muted-foreground">{a.desc}</p>
                    </div>
                    <span className="text-[10px] text-muted-foreground">{a.time}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="education" className="mt-6">
            <div className="grid sm:grid-cols-2 gap-5">
              {educationCards.map((c, i) => (
                <motion.div
                  key={c.id}
                  initial={{ opacity:0, y:15 }}
                  animate={{ opacity:1, y:0 }}
                  transition={{ delay: i *0.08 }}
                >
                  <Card className="p-5 rounded-2xl h-full hover:shadow-md transition-shadow cursor-pointer group">
                    <div className={`w-10 h-10 rounded-xl ${c.color} flex items-center justify-center mb-3`}>
                      <c.Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-heading font-semibold mb-1">{c.title}</h3>
                    <p className="text-sm text-muted-foreground">{c.desc}</p>
                    <Button variant="ghost" className="mt-4 px-0 text-primary gap-1 group-hover:gap-2 transition-all">
                      Explore <ArrowRight className="w-4 h-4" />
                    </Button>
                  </Card>
                </motion.div>
              ))}
            </div>

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
                    <Button
                      onClick={connectPartner}
                      disabled={connecting || partnerToken.trim().length < 6}
                      className="rounded-full sm:w-auto w-full gap-2"
                    >
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
                  {partnerProfile ? (
                    <PartnerSummary profile={partnerProfile} />
                  ) : (
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
