import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Key, Copy, Clock, CheckCircle, Shield } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export default function SessionKey() {
  const [generated, setGenerated] = useState(false);
  const [sessionKey, setSessionKey] = useState('');
  const [timeLeft, setTimeLeft] = useState(900);
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const generateKey = () => {
    const key = Math.floor(100000 + Math.random() * 900000).toString();
    setSessionKey(key);
    setGenerated(true);
    setTimeLeft(900);
  };

  useEffect(() => {
    if (!generated || timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft(t => t - 1), 1000);
    return () => clearInterval(timer);
  }, [generated, timeLeft]);

  const copyKey = () => {
    navigator.clipboard.writeText(sessionKey);
    setCopied(true);
    toast({ title: 'Session key copied!', description: 'Share this key with your healthcare provider.' });
    setTimeout(() => setCopied(false), 2000);
  };

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12">
      <div className="max-w-md mx-auto px-4 w-full">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="p-6 sm:p-8 rounded-2xl">
            <div className="text-center mb-6">
              <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                <Key className="w-7 h-7 text-primary" />
              </div>
              <h2 className="font-heading font-bold text-xl">Secure Session Key</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Generate a temporary key for healthcare provider access.
              </p>
            </div>

            {!generated ? (
              <div className="space-y-4">
                <div className="bg-muted/50 rounded-xl p-4 text-sm text-muted-foreground space-y-2">
                  <div className="flex items-start gap-2"><Shield className="w-4 h-4 flex-shrink-0 mt-0.5" /> Key expires after 15 minutes</div>
                  <div className="flex items-start gap-2"><Shield className="w-4 h-4 flex-shrink-0 mt-0.5" /> One-time use only</div>
                  <div className="flex items-start gap-2"><Shield className="w-4 h-4 flex-shrink-0 mt-0.5" /> Your data stays anonymous</div>
                </div>
                <Button onClick={generateKey} className="w-full rounded-full" size="lg">
                  Generate Session Key
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="bg-muted rounded-2xl p-6 text-center">
                  <p className="text-4xl font-heading font-bold tracking-[0.3em]">{sessionKey}</p>
                </div>
                <div className="flex items-center justify-center gap-2 text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span className={`text-sm font-mono font-medium ${timeLeft < 120 ? 'text-destructive' : ''}`}>
                    {minutes}:{seconds.toString().padStart(2, '0')} remaining
                  </span>
                </div>
                <Button onClick={copyKey} variant="outline" className="w-full rounded-full gap-2">
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy Key'}
                </Button>
                {timeLeft <= 0 && (
                  <div className="text-center">
                    <p className="text-sm text-destructive mb-3">Session key has expired</p>
                    <Button onClick={generateKey} className="rounded-full" size="sm">Generate New Key</Button>
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