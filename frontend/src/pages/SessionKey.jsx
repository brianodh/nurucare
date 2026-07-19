import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Key, Copy, Clock, CheckCircle, Shield, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { useLocation, Link } from 'react-router-dom';
import { useLang } from '@/lib/i18n';
import { generateSessionKey } from '@/api/apiClient';
import { getSavedProfileId } from '@/lib/useProgress';
import { Users } from 'lucide-react';

export default function SessionKey() {
  const { state } = useLocation();
  const { t } = useLang();
  const { toast } = useToast();

  // If FemaleIntake navigates here with a pre-generated key + patient ID, use it.
  const preloadedKey = state?.sessionKey || null;
  const patientId = state?.patientId || state?.sessionId || getSavedProfileId() || null;

  const [sessionKey, setSessionKey] = useState(preloadedKey || '');
  const [generated, setGenerated] = useState(!!preloadedKey);
  const [loading, setLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(900);   // 15 min
  const [copied, setCopied] = useState(false);

  // Countdown timer
  useEffect(() => {
    if (!generated || timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft((v) => v - 1), 1000);
    return () => clearInterval(timer);
  }, [generated, timeLeft]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await generateSessionKey(patientId);
      setSessionKey(response.session_key);
      setTimeLeft((response.expires_in_minutes ?? 15) * 60);
      setGenerated(true);
    } catch (err) {
      console.error('Failed to generate session key:', err);
      toast({
        title: 'Error',
        description: 'Could not generate a session key. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const copyKey = () => {
    navigator.clipboard.writeText(sessionKey).catch(() => {});
    setCopied(true);
    toast({ title: t('session_copied'), description: t('session_sub') });
    setTimeout(() => setCopied(false), 2000);
  };

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="p-6 sm:p-8 rounded-2xl">
            <div className="text-center mb-6">
              <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Key className="w-7 h-7 text-primary" />
              </div>
              <h2 className="font-heading font-bold text-xl">{t('session_title')}</h2>
              <p className="text-sm text-muted-foreground mt-1">{t('session_sub')}</p>
            </div>

            {!generated ? (
              <div className="space-y-4">
                <div className="bg-muted/50 rounded-xl p-4 text-sm text-muted-foreground space-y-2">
                  <div className="flex items-start gap-2"><Shield className="w-4 h-4 flex-shrink-0 mt-0.5" /> {t('session_expires')}</div>
                  <div className="flex items-start gap-2"><Shield className="w-4 h-4 flex-shrink-0 mt-0.5" /> {t('session_once')}</div>
                  <div className="flex items-start gap-2"><Shield className="w-4 h-4 flex-shrink-0 mt-0.5" /> {t('session_anon')}</div>
                </div>

                <Button
                  onClick={handleGenerate}
                  disabled={loading}
                  className="w-full rounded-full gap-2"
                >
                  {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                  {loading ? 'Generating…' : 'Generate Session Key'}
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="bg-muted rounded-2xl p-6 text-center">
                  <p className="text-3xl sm:text-4xl font-heading font-bold tracking-[0.3em]">{sessionKey}</p>
                </div>
                <div className="flex items-center justify-center gap-2 text-muted-foreground">
                  <Clock className="w-4 h-4 flex-shrink-0" />
                  <span className={`text-sm font-mono font-medium ${timeLeft < 120 ? 'text-destructive' : ''}`}>
                    {minutes}:{seconds.toString().padStart(2, '0')} {t('session_remaining')}
                  </span>
                </div>
                <Button onClick={copyKey} variant="outline" className="w-full rounded-full gap-2">
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? t('session_copied') : t('session_copy')}
                </Button>
                <Link to="/female/sync" className="block">
                  <Button variant="outline" className="w-full rounded-full gap-2">
                    <Users className="w-4 h-4" /> Partner Sync
                  </Button>
                </Link>
                {timeLeft <= 0 && (
                  <div className="text-center space-y-3">
                    <p className="text-sm text-destructive">{t('session_expired')}</p>
                    <Button onClick={handleGenerate} size="sm" className="rounded-full" disabled={loading}>
                      {loading && <Loader2 className="w-4 h-4 animate-spin mr-2" />}
                      Generate New Key
                    </Button>
                  </div>
                )}
              </div>
            )}
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
