import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  User,
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
import { useAuth } from '@/lib/AuthContext';
import { useLang } from '@/lib/i18n.jsx';
import NotificationCenter from '../components/NotificationCenter';
import HealthTrendChart from '../components/HealthTrendChart';
import PartnerSummary from '../components/PartnerSummary';
import OnboardingTour from '../components/OnboardingTour';
import { verifySyncToken } from '@/api/apiClient';
import { useToast } from '@/components/ui/use-toast';

// Mock data
const mockNotifications = [
  { id: 1, title: 'Welcome!', message: 'Complete your profile for personalized recommendations.', time: '2m ago', read: false },
  { id: 2, title: 'New Content', message: 'Check out our latest men\'s health guide.', time: '1h ago', read: false },
  { id: 3, title: 'Reminder', message: 'Don\'t forget to log your health metrics.', time: '1d ago', read: true },
];

const mockRecentActivity = [
  { id: 1, action: 'Completed profile', time: '2 days ago', icon: CheckCircle2, color: 'text-green-500' },
  { id: 2, action: 'Viewed educational content', time: '1 week ago', icon: BookOpen, color: 'text-blue-500' },
];

const mockMilestones = [
  { id: 1, title: 'Complete Health Assessment', progress: 100, completed: true },
  { id: 2, title: 'Explore Educational Resources', progress: 40, completed: false },
  { id: 3, title: 'Connect with a Partner', progress: 0, completed: false },
];

const maleEducationCards = [
  {
    title: 'Contraception Basics',
    description: 'Learn about the different contraceptive options available for men.',
    icon: BookOpen,
    color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300',
  },
  {
    title: 'Vasectomy Info',
    description: 'Understand what vasectomy is, how it works and what to expect.',
    icon: Stethoscope,
    color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300',
  },
  {
    title: 'Healthy Relationships',
    description: 'Tips for communicating about contraception with your partner.',
    icon: Heart,
    color: 'bg-pink-100 text-pink-700 dark:bg-pink-900/20 dark:text-pink-300',
  },
  {
    title: 'General Wellness',
    description: 'Lifestyle tips for maintaining good overall health.',
    icon: Activity,
    color: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300',
  },
];

const vasectomyMyths = [
  { question: 'Does a vasectomy affect sexual performance?', answer: 'No, a vasectomy does not affect sexual performance, libido, or hormone levels. It only blocks the vas deferens to prevent sperm from reaching the semen.' },
  { question: 'Is a vasectomy permanent?', answer: 'A vasectomy is intended to be permanent, but in some cases, it can be reversed. Reversal success depends on factors like time since the procedure.' },
  { question: 'Will a vasectomy protect against STIs?', answer: 'No, a vasectomy does not protect against sexually transmitted infections (STIs). You should still use condoms for STI protection.' },
  { question: 'What is the recovery like?', answer: 'Most men recover within a week. You may experience mild discomfort, swelling, or bruising. Follow your doctor\'s post-procedure instructions.' },
];

export default function MaleDashboard() {
  const { user } = useAuth();
  const { t } = useLang();
  const { toast } = useToast();

  // Notification state
  const [notifications, setNotifications] = useState(mockNotifications);
  const markAllRead = () => setNotifications(notifications.map(n => ({ ...n, read: true })));
  const markRead = (id) => setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
  const clearAll = () => setNotifications([]);

  // Tour state
  const [showTour, setShowTour] = useState(false);
  const [tourStep, setTourStep] = useState(0);

  useEffect(() => {
    const hasSeenTour = localStorage.getItem('male_onboarded');
    if (!hasSeenTour) {
      setShowTour(true);
    }
  }, []);

  const completeTour = () => {
    localStorage.setItem('male_onboarded', 'true');
    setShowTour(false);
  };

  // Partner sync state
  const [partnerToken, setPartnerToken] = useState('');
  const [connecting, setConnecting] = useState(false);
  const [partnerProfile, setPartnerProfile] = useState(null);
  const handleVerifyPartner = async () => {
    setConnecting(true);
    try {
      const result = await verifySyncToken(partnerToken);
      if (result.success) {
        // Mock partner profile for demo purposes
        setPartnerProfile({
          age: 28,
          smoking: false,
          migraine_type: 'none',
          systolic_bp: 110,
          diastolic_bp: 70,
          allowed_methods: ['condoms', 'other_barrier', 'coitus_interruptus'],
        });
        toast({ title: 'Partner connected!', description: 'You can now share health decisions together.' });
      }
    } catch (err) {
      toast({ title: 'Invalid token', description: 'Please check the token and try again.', variant: 'destructive' });
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div className="min-h-[85vh] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold font-heading flex items-center gap-2">
              <span>Welcome back</span>
              <span className="text-primary">{user?.name?.split(' ')[0] || 'User'}!</span>
            </h1>
            <p className="text-muted-foreground mt-1">Here's what's happening with your health.</p>
          </div>
          <NotificationCenter
            notifications={notifications}
            onMarkAllRead={markAllRead}
            onMarkRead={markRead}
            onClearAll={clearAll}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="space-y-6 lg:col-span-2">
            {/* Health Score & Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Health Score Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="h-full">
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-primary" />
                      Health Score
                    </CardTitle>
                    <CardDescription>Based on your health profile</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4">
                      <div className="relative w-24 h-24 flex items-center justify-center">
                        <svg className="w-full h-full" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="40" fill="none" stroke="hsl(var(--border))" strokeWidth="8" />
                          <circle cx="50" cy="50" r="40" fill="none" stroke="hsl(var(--primary))" strokeWidth="8" strokeLinecap="round"
                            strokeDasharray="251.2" strokeDashoffset="62.8" transform="rotate(-90 50 50)" />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-3xl font-bold">75</span>
                          <span className="text-xs text-muted-foreground">/100</span>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Great job! Your health profile looks good.</p>
                        <Progress value={75} className="h-2" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Quick Actions */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="h-full">
                  <CardHeader className="pb-2">
                    <CardTitle>Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <Link to="/patient/male/sync" className="w-full">
                      <Button variant="secondary" className="w-full justify-start gap-2">
                        <Users className="w-4 h-4" />
                        Partner Sync
                      </Button>
                    </Link>
                    <Link to="/education" className="w-full">
                      <Button variant="secondary" className="w-full justify-start gap-2">
                        <BookOpen className="w-4 h-4" />
                        Education
                      </Button>
                    </Link>
                    <Button variant="secondary" className="w-full justify-start gap-2">
                      <Stethoscope className="w-4 h-4" />
                      Find Provider
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Health Trends Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card>
                <CardContent className="pt-6">
                  <HealthTrendChart />
                </CardContent>
              </Card>
            </motion.div>

            {/* Male-specific Education Cards */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-xl font-semibold mb-4">Men's Health Education</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {maleEducationCards.map((card, index) => {
                  const Icon = card.icon;
                  return (
                    <Card key={index} className="overflow-hidden hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 ${card.color}`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <h3 className="font-semibold mb-1">{card.title}</h3>
                        <p className="text-sm text-muted-foreground">{card.description}</p>
                        <Button variant="ghost" className="mt-3 h-8 px-0 hover:bg-transparent text-primary">
                          Learn more <ChevronRight className="w-4 h-4 ml-1" />
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Vasectomy Myths Accordion */}
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle>Vasectomy Myths & Facts</CardTitle>
                  <CardDescription>Get answers to common questions about vasectomy.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="w-full">
                    {vasectomyMyths.map((myth, index) => (
                      <AccordionItem key={index} value={`item-${index}`}>
                        <AccordionTrigger className="text-left font-medium">{myth.question}</AccordionTrigger>
                        <AccordionContent className="text-muted-foreground">{myth.answer}</AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Partner Sync Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-primary" />
                    Partner Sync
                  </CardTitle>
                  <CardDescription>Connect with your partner to share health decisions.</CardDescription>
                </CardHeader>
                <CardContent>
                  {!partnerProfile ? (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          Enter your partner's sync token to connect your profiles.
                        </p>
                        <div className="flex gap-2">
                          <Input
                            placeholder="Enter partner token"
                            value={partnerToken}
                            onChange={(e) => setPartnerToken(e.target.value)}
                          />
                          <Button
                            onClick={handleVerifyPartner}
                            disabled={connecting || partnerToken.trim() === ''}
                          >
                            Connect
                          </Button>
                        </div>
                      </div>
                      <div className="text-center">
                        <Link to="/partner-sync">
                          <Button variant="link" className="text-sm">Need a token for yourself?</Button>
                        </Link>
                      </div>
                    </div>
                  ) : (
                    <PartnerSummary profile={partnerProfile} />
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {/* Recent Activity & Milestones */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Tabs defaultValue="activity" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="activity">Recent Activity</TabsTrigger>
                  <TabsTrigger value="milestones">Milestones</TabsTrigger>
                </TabsList>
                <TabsContent value="activity">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="space-y-4">
                        {mockRecentActivity.map((activity) => {
                          const Icon = activity.icon;
                          return (
                            <div key={activity.id} className="flex items-center gap-4">
                              <div className={`p-2 rounded-full bg-muted ${activity.color}`}>
                                <Icon className="w-4 h-4" />
                              </div>
                              <div className="flex-1">
                                <p className="text-sm font-medium">{activity.action}</p>
                                <p className="text-xs text-muted-foreground">{activity.time}</p>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
                <TabsContent value="milestones">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="space-y-4">
                        {mockMilestones.map((milestone) => (
                          <div key={milestone.id} className="space-y-2">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium">{milestone.title}</p>
                              {milestone.completed && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                            </div>
                            <Progress value={milestone.progress} className="h-2" />
                            <p className="text-xs text-muted-foreground">{milestone.progress}% complete</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Onboarding Tour */}
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
