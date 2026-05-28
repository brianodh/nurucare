import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Key, Copy, Clock, CheckCircle, Shield } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { useLocation } from 'react-router-dom';
import { useLang } from '@/lib/i18n';

export default function SessionKey() {
  const { state } = useLocation();
  const { t } = useLang();
  const preloadedKey = state?.sessionKey || null;
  const [sessionKey] = useState(preloadedKey || '');
  const generated = !!preloadedKey;
  const [timeLeft, setTimeLeft] = useState(900);
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (!generated || timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft(v => v - 1), 1000);
    return () => clearInterval(timer);
  }, [generated, timeLeft]);

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
                <p className="text-sm text-center text-muted-foreground">{t('session_complete_first')}</p>
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
                {timeLeft <= 0 && (
                  <div className="text-center">
                    <p className="text-sm text-destructive mb-3">{t('session_expired')}</p>
                    <p className="text-xs text-muted-foreground">{t('session_new')}</p>
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